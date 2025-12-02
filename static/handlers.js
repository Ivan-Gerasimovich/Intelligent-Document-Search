document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.getElementById("search-form");
  const indexForm = document.getElementById("index-form");
  const uploadForm = document.getElementById("upload-form");
  const fileInput = document.getElementById("query_file");
  const uploadBtn = document.getElementById("uploadBtn");
  const selectedFile = document.getElementById("selectedFile");
  const fileLabel = document.getElementById("fileLabel");
  const dropzone = document.getElementById("dropzone");

  // Enable/disable upload button & show file name
  if (fileInput && uploadBtn) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        selectedFile.textContent = file.name;
        fileLabel.textContent = `✅ Выбран файл: ${file.name}`;
        uploadBtn.disabled = false;
      } else {
        selectedFile.textContent = "";
        fileLabel.textContent = "Перетащите файл сюда или выберите вручную (.txt)";
        uploadBtn.disabled = true;
      }
    });

    // Optional drag effect
    ["dragenter", "dragover"].forEach(evt =>
      dropzone.addEventListener(evt, () => dropzone.classList.add("bg-blue-200"))
    );
    ["dragleave", "drop"].forEach(evt =>
      dropzone.addEventListener(evt, () => dropzone.classList.remove("bg-blue-200"))
    );
  }

  // Handle search form submit
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      fetch("/start_search", {
        method: "POST",
        body: new FormData(searchForm),
      }).then(() => startPolling("search"));
    });
  }

  // Handle index form submit
  if (indexForm) {
    indexForm.addEventListener("submit", (e) => {
      e.preventDefault();
      fetch("/index_database", {
        method: "POST",
        body: new FormData(indexForm),
      }).then(() => startPolling("index"));
    });
  }

  // Handle file upload form submit
  if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
      e.preventDefault();
      fetch("/upload_query", {
        method: "POST",
        body: new FormData(uploadForm),
      }).then(() => startPolling("file"));
    });
  }
});
