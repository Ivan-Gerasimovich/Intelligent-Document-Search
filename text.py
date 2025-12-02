import json
import glob

from rapidfuzz import fuzz



def fuzzy_search(query:str, company:dict[str, str], search_type:str, accuracy=100) -> bool:
    query = query.lower()
    if search_type == "NAME":
        search_type = "Name"
    elif search_type == "ContractNumber":
        search_type = "CKKO"
    value = company[search_type]
    if len(value) >= 6:
        score = fuzz.partial_ratio(query, value.lower())
        if score >= accuracy:
            return True
    return False


def search_by_query_json(query: str,accuracy:int, search_type:str, results_queue, progress_queue, is_file=False) -> None:
    files = glob.glob("Indexed/**/*.json", recursive=True)
    results = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
                for company in data:
                    result = fuzzy_search(query, company, search_type, accuracy)
                    if result:
                        results.append({
                            "Query" : query,
                            "UNP" : company["UNP"],
                            "KO" : company["KO"],
                            "CKKO" : company["CKKO"],
                            "Name" : company["Name"], 
                            "File": file.replace(".json", ".pdf").replace("Indexed", "AKTY"),
                            "Page" : company["Page"]
                        })
    if results:
        results_queue.put(results)
    else:
        results_queue.put([{"Query": query}])
    if not is_file:
        progress_queue.put({"type": "search", "value" : 1.0})
        progress_queue.put({"type": "done"})


def search_by_file(inputs:bytes, accuracy:int, results_queue, progress_queue) -> None:
    queries = inputs.decode("utf-8").split("\n")
    for query in queries:
        search_by_query_json(query, accuracy, "UNP", results_queue, progress_queue, is_file=True)
    progress_queue.put({"type": "search", "value" : 1.0})
    progress_queue.put({"type": "done"})

