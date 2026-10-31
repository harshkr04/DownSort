// DownSort Frontend Application Logic
let allFiles = [];
let categoriesMeta = [];
let currentFilter = 'ALL';
let currentSearch = '';
let currentMode = 'move'; // 'move' or 'copy'
let isScanning = false;
let isOrganizing = false;

// DOM Elements
const folderPathInput = document.getElementById('folderPathInput');
const btnScan = document.getElementById('btnScan');
const scanText = document.getElementById('scanText');
const scanIcon = document.getElementById('scanIcon');
const statTotalFiles = document.getElementById('statTotalFiles');
const statPdfCount = document.getElementById('statPdfCount');
const statTotalSize = document.getElementById('statTotalSize');
const statCategories = document.getElementById('statCategories');
const categoryChips = document.getElementById('categoryChips');
const countAll = document.getElementById('countAll');
const filterStatus = document.getElementById('filterStatus');
const searchInput = document.getElementById('searchInput');
const selectAllCheckbox = document.getElementById('selectAllCheckbox');
const modeMove = document.getElementById('modeMove');
const modeCopy = document.getElementById('modeCopy');
const btnOrganize = document.getElementById('btnOrganize');
const organizeBtnText = document.getElementById('organizeBtnText');
const filesTableBody = document.getElementById('filesTableBody');
const historyModal = document.getElementById('historyModal');
const btnHistory = document.getElementById('btnHistory');
const btnCloseModal = document.getElementById('btnCloseModal');
const historyList = document.getElementById('historyList');

// Init
window.addEventListener('DOMContentLoaded', async () => {
  await fetchStatus();
  await fetchCategories();
  // Auto-scan default folder on startup for instant utility
  triggerScan();
});

// Fetch system status
async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.default_folder && !folderPathInput.value) {
      folderPathInput.value = data.default_folder;
    }
  } catch (err) {
    console.error('Error fetching status:', err);
  }
}

// Fetch categories
async function fetchCategories() {
  try {
    const res = await fetch('/api/categories');
    const data = await res.json();
    categoriesMeta = data.categories || [];
  } catch (err) {
    console.error('Error fetching categories:', err);
  }
}

// Trigger folder scan
btnScan.addEventListener('click', triggerScan);

async function triggerScan() {
  const folder = folderPathInput.value.trim();
  if (!folder) {
    alert('Please enter a valid folder path.');
    return;
  }

  isScanning = true;
  btnScan.disabled = true;
  scanIcon.innerHTML = `<div class="spinner"></div>`;
  scanText.textContent = 'Scanning...';

  try {
    const res = await fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: folder })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Scan failed');
    }

    const data = await res.json();
    allFiles = data.files || [];
    renderStats(data);
    renderCategoryChips(data.categories_breakdown);
    renderTable();
    updateOrganizeButton();
  } catch (err) {
    alert(`Scan error: ${err.message}`);
  } finally {
    isScanning = false;
    btnScan.disabled = false;
    scanIcon.innerHTML = `<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>`;
    scanText.textContent = 'Scan Folder';
  }
}

// Render Stats
function renderStats(data) {
  statTotalFiles.textContent = data.total_files || 0;
  statPdfCount.textContent = data.pdf_count || 0;
  statTotalSize.textContent = data.total_size_formatted || '0 B';
  statCategories.textContent = data.categories_breakdown ? data.categories_breakdown.length : 0;
  countAll.textContent = data.total_files || 0;
}

// Render Category Filter Chips
function renderCategoryChips(breakdown) {
  categoryChips.innerHTML = `
    <div class="chip ${currentFilter === 'ALL' ? 'active' : ''}" data-category="ALL">
      <span>All Files</span>
      <span class="chip-count" id="countAll">${allFiles.length}</span>
    </div>
  `;

  if (!breakdown) return;

  breakdown.forEach(cat => {
    const chip = document.createElement('div');
    chip.className = `chip ${currentFilter === cat.category ? 'active' : ''}`;
    chip.dataset.category = cat.category;
    chip.innerHTML = `
      <span>${cat.label}</span>
      <span class="chip-count">${cat.count}</span>
    `;
    chip.addEventListener('click', () => {
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentFilter = cat.category;
      filterStatus.textContent = `Filtered by: ${cat.label}`;
      renderTable();
    });
    categoryChips.appendChild(chip);
  });

  // Re-attach listener for "ALL"
  categoryChips.firstElementChild.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    categoryChips.firstElementChild.classList.add('active');
    currentFilter = 'ALL';
    filterStatus.textContent = 'Showing all files';
    renderTable();
  });
}

// Render Table
function renderTable() {
  const filtered = getFilteredFiles();

  if (filtered.length === 0) {
    filesTableBody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state">
          <p>No files match the current filter or search criteria.</p>
        </td>
      </tr>
    `;
    selectAllCheckbox.checked = false;
    updateOrganizeButton();
    return;
  }

  filesTableBody.innerHTML = '';

  filtered.forEach(file => {
    const tr = document.createElement('tr');

    // Extension styling color
    const ext = file.extension.replace('.', '') || 'file';
    let extColor = '#818cf8';
    if (['pdf'].includes(ext)) extColor = '#f43f5e';
    else if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) extColor = '#38bdf8';
    else if (['mp4', 'mkv'].includes(ext)) extColor = '#fb923c';
    else if (['docx', 'doc'].includes(ext)) extColor = '#3b82f6';
    else if (['xlsx', 'csv'].includes(ext)) extColor = '#10b981';
    else if (['zip', 'rar'].includes(ext)) extColor = '#f59e0b';
    else if (['apk'].includes(ext)) extColor = '#34d399';

    // Category options for dropdown
    const catOptions = categoriesMeta.map(c => 
      `<option value="${c.id}" ${file.target_folder === c.id ? 'selected' : ''}>${c.label}</option>`
    ).join('');

    tr.innerHTML = `
      <td class="checkbox-col">
        <input type="checkbox" class="custom-checkbox file-cb" data-id="${file.id}" ${file.selected ? 'checked' : ''}>
      </td>
      <td>
        <div class="file-name-cell">
          <div class="file-ext-icon" style="background: ${extColor}22; color: ${extColor}; border: 1px solid ${extColor}55;">
            ${ext.slice(0, 4)}
          </div>
          <div class="file-name-info">
            <span class="file-main-name" title="${file.filename}">${file.filename}</span>
            <span class="file-sub-info">${file.modified}</span>
          </div>
        </div>
      </td>
      <td>
        <span style="font-size: 12px; font-weight: 500; color: var(--text-secondary);">${file.size_formatted}</span>
      </td>
      <td>
        <select class="cat-select" data-id="${file.id}">
          ${catOptions}
        </select>
      </td>
      <td>
        <div class="reason-cell">
          <span class="cat-pill color-${file.color}">${file.reason}</span>
        </div>
      </td>
    `;

    // Event listener for checkbox
    const cb = tr.querySelector('.file-cb');
    cb.addEventListener('change', (e) => {
      file.selected = e.target.checked;
      updateOrganizeButton();
      updateSelectAllCheckboxState();
    });

    // Event listener for category select
    const sel = tr.querySelector('.cat-select');
    sel.addEventListener('change', (e) => {
      file.target_folder = e.target.value;
      const foundMeta = categoriesMeta.find(m => m.id === e.target.value);
      if (foundMeta) {
        file.category = foundMeta.id;
        file.color = foundMeta.color;
        file.label = foundMeta.label;
      }
    });

    filesTableBody.appendChild(tr);
  });

  updateSelectAllCheckboxState();
  updateOrganizeButton();
}

function getFilteredFiles() {
  return allFiles.filter(f => {
    const matchesCategory = currentFilter === 'ALL' || f.category === currentFilter;
    const matchesSearch = !currentSearch || 
      f.filename.toLowerCase().includes(currentSearch) ||
      f.reason.toLowerCase().includes(currentSearch) ||
      f.category.toLowerCase().includes(currentSearch) ||
      f.extension.toLowerCase().includes(currentSearch);
    return matchesCategory && matchesSearch;
  });
}

function updateSelectAllCheckboxState() {
  const filtered = getFilteredFiles();
  if (filtered.length === 0) {
    selectAllCheckbox.checked = false;
    return;
  }
  const allSelected = filtered.every(f => f.selected);
  const someSelected = filtered.some(f => f.selected);
  selectAllCheckbox.checked = allSelected;
  selectAllCheckbox.indeterminate = !allSelected && someSelected;
}

selectAllCheckbox.addEventListener('change', (e) => {
  const isChecked = e.target.checked;
  const filtered = getFilteredFiles();
  filtered.forEach(f => {
    f.selected = isChecked;
  });
  renderTable();
});

// Search input debounce
searchInput.addEventListener('input', (e) => {
  currentSearch = e.target.value.trim().toLowerCase();
  renderTable();
});

// Mode buttons
modeMove.addEventListener('click', () => {
  currentMode = 'move';
  modeMove.classList.add('active');
  modeCopy.classList.remove('active');
});

modeCopy.addEventListener('click', () => {
  currentMode = 'copy';
  modeCopy.classList.add('active');
  modeMove.classList.remove('active');
});

function updateOrganizeButton() {
  const selectedCount = allFiles.filter(f => f.selected).length;
  btnOrganize.disabled = selectedCount === 0 || isOrganizing;
  organizeBtnText.textContent = selectedCount > 0 
    ? `${currentMode === 'move' ? 'Move' : 'Copy'} ${selectedCount} File${selectedCount > 1 ? 's' : ''}` 
    : 'Select Files to Organize';
}

// Execute Organization
btnOrganize.addEventListener('click', async () => {
  const selectedFiles = allFiles.filter(f => f.selected);
  if (selectedFiles.length === 0) return;

  const folder = folderPathInput.value.trim();
  const confirmed = confirm(`Are you sure you want to ${currentMode} ${selectedFiles.length} files into organized folders?`);
  if (!confirmed) return;

  isOrganizing = true;
  btnOrganize.disabled = true;
  organizeBtnText.textContent = 'Organizing...';

  const actions = selectedFiles.map(f => ({
    filepath: f.filepath,
    target_folder: f.target_folder
  }));

  try {
    const res = await fetch('/api/organize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        folder_path: folder,
        actions: actions,
        mode: currentMode
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Organization failed');
    }

    alert(`Successfully organized ${data.successful} file(s)!`);
    // Re-scan to show updated clean state
    await triggerScan();
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    isOrganizing = false;
    btnOrganize.disabled = false;
    updateOrganizeButton();
  }
});

// History & Undo Modal
btnHistory.addEventListener('click', async () => {
  historyModal.classList.add('open');
  await loadHistory();
});

btnCloseModal.addEventListener('click', () => {
  historyModal.classList.remove('open');
});

historyModal.addEventListener('click', (e) => {
  if (e.target === historyModal) {
    historyModal.classList.remove('open');
  }
});

async function loadHistory() {
  historyList.innerHTML = `<div class="empty-state"><div class="spinner" style="margin: 0 auto 12px;"></div>Loading history...</div>`;

  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const history = data.history || [];

    if (history.length === 0) {
      historyList.innerHTML = `<div class="empty-state"><p>No organization history yet.</p></div>`;
      return;
    }

    historyList.innerHTML = '';
    history.forEach(session => {
      const item = document.createElement('div');
      item.className = `history-item ${session.status === 'undone' ? 'undone' : ''}`;
      
      const fileCount = session.moves ? session.moves.length : 0;
      const isUndone = session.status === 'undone';

      item.innerHTML = `
        <div>
          <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">
            ${session.timestamp} (${fileCount} files ${session.mode === 'copy' ? 'copied' : 'moved'})
          </div>
          <div style="font-size: 12px; color: var(--text-secondary);">
            Folder: <code style="color: var(--accent-indigo);">${session.base_folder}</code>
          </div>
          ${isUndone ? `<div style="font-size: 11px; color: #f43f5e; margin-top: 4px;">Rolled back on ${session.undone_at}</div>` : ''}
        </div>
        <div>
          ${!isUndone ? `
            <button class="btn btn-danger btn-undo" data-id="${session.session_id}" style="padding: 8px 14px; font-size: 12px;">
              Undo / Revert
            </button>
          ` : `
            <span class="badge" style="background: rgba(244, 63, 94, 0.1); color: #fda4af;">Undone</span>
          `}
        </div>
      `;

      if (!isUndone) {
        const undoBtn = item.querySelector('.btn-undo');
        undoBtn.addEventListener('click', async () => {
          if (!confirm(`Do you want to restore these ${fileCount} files to their original locations?`)) return;
          undoBtn.disabled = true;
          undoBtn.textContent = 'Restoring...';
          try {
            const uRes = await fetch('/api/undo', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: session.session_id })
            });
            const uData = await uRes.json();
            if (!uRes.ok) throw new Error(uData.detail || 'Undo failed');
            alert(`Restored ${uData.restored} files!`);
            await loadHistory();
            await triggerScan();
          } catch (err) {
            alert(`Undo error: ${err.message}`);
            undoBtn.disabled = false;
            undoBtn.textContent = 'Undo / Revert';
          }
        });
      }

      historyList.appendChild(item);
    });
  } catch (err) {
    historyList.innerHTML = `<div class="empty-state"><p style="color: #f43f5e;">Error loading history: ${err.message}</p></div>`;
  }
}
