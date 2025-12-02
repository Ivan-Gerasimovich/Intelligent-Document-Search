
let polling = false;
let currentTask = "search";
let pollingInterval = 1000;

/**
 * Starts polling for progress and live results.
 */
function startPolling(type = "search") {
  polling = false; // Stop previous polling
  currentTask = type;

  // Reset bars smoothly
  ["search-bar", "file-bar", "page-bar"].forEach(id => {
    const bar = document.getElementById(id);
    if (bar) {
      bar.style.transition = "none"; // Disable transition just for reset
      bar.style.width = "0%";
      setTimeout(() => {
        bar.style.transition = "width 1s ease-in-out"; // Re-enable
      }, 50);
    }
  });

  // Clear old results if needed
  if (type === "search") {
    const tbody = document.getElementById("results-body");
    if (tbody) tbody.innerHTML = "";
  }
  if (type === "file"){
  const tbody = document.getElementById("results-body")
  if (tbody) tbody.innerHTML = "";
  }

  polling = true;
  pollProgress();
  if (type === "search") pollLiveResults();
}

/**
 * Polls backend for progress updates.
 */
function pollProgress() {
  if (!polling) return;

  fetch("/progress")
    .then(res => res.ok ? res.json() : Promise.reject(res.status))
    .then(data => {
      if (Array.isArray(data)) updateProgressBars(data);
      else console.warn("Unexpected progress format:", data);
    })
    .catch(err => {
      console.error("Progress Polling error:", err);
      polling = false;
    })
    .finally(() => {
      if (polling) setTimeout(pollProgress, pollingInterval);
    });
}

/**
 * Updates the progress bars based on backend data.
 */


function updateProgressBars(progressArray) {
  progressArray.forEach(({ type, value }) => {
    if (type === "done") {
      fetch("/stream_next")
        .then(res => (res.status === 204 ? null : res.json()))
        .then(data => {
          if (Array.isArray(data)) data.forEach(renderSingleRow);
          else if (data) renderSingleRow(data);
        })
        .catch(err => console.error("Final result fetch error:", err))
        .finally(() => polling = false);
      return;
    }

    if (typeof value !== "number") {
      console.warn("Invalid progress entry:", { type, value });
      return;
    }

    const percent = (value * 100).toFixed(1) + "%";

    const bar = document.getElementById(`${type}-bar`);
    if (bar) {
      bar.style.width = percent;
    }

    const label = document.getElementById(`${type}-label`);
    if (label) {
      label.textContent = `${(value * 100).toFixed(0)}%`;
    }
  });
}

/**
 * Polls backend for streaming search results.
 */
function pollLiveResults() {
  if (!polling || currentTask !== "search") return;

  fetch("/stream_next")
    .then(res => (res.status === 204 ? null : res.json()))
    .then(data => {
      if (Array.isArray(data)) data.forEach(renderSingleRow);
      else if (data) renderSingleRow(data);
    })
    .catch(err => {
      console.error("Live Results Polling error:", err);
      polling = false;
    })
    .finally(() => {
      if (polling) setTimeout(pollLiveResults, pollingInterval);
    });
}
