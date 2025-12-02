
let lastQuery = null;

function renderSingleRow(row) {
  const tbody = document.getElementById("results-body");
  if (!tbody) return;

  const hasContent = row.UNP?.trim() || row.KO?.trim() || row.CKKO?.trim() || row.Name?.trim() || (row.File && row.Page !== undefined);

  // Show query header if it's the first time or it changes
  if (lastQuery === null || row.Query !== lastQuery) {
    const headerTr = document.createElement("tr");
    headerTr.innerHTML = `
      <td colspan="5" class="px-4 py-2 border border-gray-200 bg-gray-100 text-center text-gray-700 text-sm font-semibold">
        🔎 Запрос: ${row.Query}
      </td>
    `;
    tbody.appendChild(headerTr);
    lastQuery = row.Query;
  }

  if (!hasContent) {
    const emptyTr = document.createElement("tr");
    emptyTr.innerHTML = `
      <td colspan="5" class="px-4 py-2 border-t border-gray-200 text-center text-gray-400 italic">
        Нет данных для этого запроса
      </td>
    `;
    tbody.appendChild(emptyTr);
    return;
  }

  const tr = document.createElement("tr");

  const pageLink = (row.File && row.Page !== undefined)
    ? `<a href="/view_pdf?path=${encodeURIComponent(row.File)}#page=${row.Page}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline underline-offset-2">Открыть</a>`
    : `<span class="text-gray-400"></span>`;

  tr.innerHTML = `
    <td class="px-4 py-2 border border-gray-200 text-center align-middle">${row.UNP?.trim() || ""}</td>
    <td class="px-4 py-2 border border-gray-200 text-center align-middle">${row.KO?.trim() || ""}</td>
    <td class="px-4 py-2 border border-gray-200 text-center align-middle">${row.CKKO?.trim() || ""}</td>
    <td class="px-4 py-2 border border-gray-200 text-center align-middle">${row.Name || ""}</td>
    <td class="px-4 py-2 border border-gray-200 text-center align-middle">${pageLink}</td>
  `;

  tbody.appendChild(tr);
}
