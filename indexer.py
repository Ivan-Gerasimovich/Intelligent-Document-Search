import fitz
from PIL import Image
from pytesseract import image_to_string
import cv2
import numpy as np
from multiprocessing import Pool

from fuzzysearch import find_near_matches as fnm

from glob import glob
from pathlib import Path
import json


def ocr_worker(args):
    file_path, page_index = args
    doc = fitz.open(file_path)
    page = doc.load_page(page_index)
    text = ocr_page(page)
    doc.close()
    return get_data(text.replace("\n", ""), page_index)

def ocr_page(page) -> str: 
    pixmap = page.get_pixmap(colorspace=fitz.csGRAY)
    image = Image.frombytes("L", (pixmap.width, pixmap.height), pixmap.samples)
    width, height = image.size
    top = int(height * 0.05)
    bottom = int(height * 0.33)

    cropped_image = image.crop((0, top, width, bottom))

    proccesed_image = preprocess_level(cropped_image)

    return image_to_string(proccesed_image, lang="rus", config="--oem 3 --psm 6")




def preprocess_level(img):
    gray = np.array(img) 
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_img = clahe.apply(gray)

    gamma = 1.5
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
    gamma_corrected = cv2.LUT(contrast_img, lut)

    return cv2.resize(gamma_corrected, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)



def get_CKKO(text:str, accuracy:int) -> str:
    result = ""
    matches = fnm("№ скко", text.lower(), max_l_dist=accuracy)
    if matches:
        match = matches[-1]
        result = "".join([char for char in text[match.end - 3:match.end + 12] if char.isdigit()])
    return result


def get_KO(text:str, accuracy:int) -> str:
    result = ""
    matches = fnm("учетный номер ко ", text.lower(), max_l_dist=accuracy)
    if matches:
        match = matches[0]
        result = "".join([char for char in text[match.end - 3:match.end + 12] if char.isdigit()])
    return result

def get_UNP_and_NAME(text:str, UNP_accuracy:int, NAME_accuracy:int) -> tuple[str, str]:
    UNP, NAME = "", ""
    UNP_matches = fnm("Настоящий", text, max_l_dist=UNP_accuracy)
    NAME_matches = fnm("Пользователь: ", text, max_l_dist=NAME_accuracy)
    if UNP_matches and NAME_matches:
        UNP_match = UNP_matches[0]
        NAME_match = NAME_matches[0]
        UNP = "".join([char for char in text[UNP_match.start - 12:UNP_match.start + 3] if char.isdigit()])
        NAME = text[NAME_match.end:UNP_match.start-11]
    return UNP, NAME


def get_data(text: str, page)  -> dict[str, str]:
    final_dict = {}
    CKKO = get_CKKO(text, accuracy=1)
    KO = get_KO(text, accuracy=2)
    UNP, NAME = get_UNP_and_NAME(text, UNP_accuracy=4, NAME_accuracy=5)
    if all([CKKO, KO, UNP, NAME]): 
        final_dict = {"Name": NAME,
                      "KO": KO,
                      "UNP": UNP,
                      "CKKO": CKKO,
                      "Page": str(page + 1)}
    return final_dict


def split_pdf_to_parts(file: str, part_size=10) -> list[str]:
    doc = fitz.open(file)
    total_pages = doc.page_count
    if total_pages <= part_size:
        return [file]
    pathes = []
    part_index = 1
    for start_page in range(0, doc.page_count, part_size):
        part = fitz.open()
        last_page = min(start_page + part_size - 1, total_pages - 1)
        file_base = Path(file).with_suffix("").as_posix()
        output_path = f"{file_base}_part_{part_index}.pdf"
        part.insert_pdf(doc, from_page=start_page, to_page=last_page)
        part.save(output_path)
        part.close()
        part_index += 1
        pathes.append(output_path)
    Path(file).unlink()
    doc.close()
    return pathes


def index_local_pdfs(progress_queue) -> None:
    pdf_files = glob("AKTY/**/*.pdf", recursive=True)
    already_indexed = glob("Indexed/**/*.json", recursive=True)
    for indexed_file in already_indexed:
        if indexed_file.replace(".json", ".pdf").replace("Indexed", "AKTY") not in pdf_files:
            Path(indexed_file).unlink()
    files = []
    for f in pdf_files:
        if f.replace("AKTY", "Indexed").replace(".pdf", '.json') not in already_indexed:
            files.append(f)
    num_of_files = len(files)
    for file_index, file in enumerate(files, 1):
        output = []
        files_to_parts = split_pdf_to_parts(file)
        for part in files_to_parts:
            document = fitz.open(part)
            num_of_pages = document.page_count
            pages_args = [(part, i) for i in range(num_of_pages)]
            with Pool() as pool:
                results = pool.map(ocr_worker, pages_args)
                output.extend([r for r in results if r])
                # progress_queue.put({"type": "page", "value": page_index/num_of_pages})
            document.close()
            progress_queue.put({"type": "file", "value": file_index/num_of_files})
            path = file[:-4].replace("AKTY", "Indexed") + ".json"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).touch()
            if output:
                with open(path, 'w', encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
    progress_queue.put({"type": "page", "value": 1.0})
    progress_queue.put({"type": "file", "value": 1.0})
    progress_queue.put({"type" : "done"})


if __name__ == "__main__":
    print("Error!")
