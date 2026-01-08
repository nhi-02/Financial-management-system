// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Confirm delete
function confirmDelete(message) {
    return confirm(message || 'Bạn có chắc muốn xóa?');
}

// Format number input with thousand separators
function formatNumberInput(input) {
    let value = input.value.replace(/[^0-9]/g, '');
    if (value) {
        input.value = parseInt(value).toLocaleString('vi-VN');
    }
}

function openTransactionModal() {
  document.getElementById('transactionModal').classList.remove('hidden');
  loadCategories();
}

function closeTransactionModal() {
  document.getElementById('transactionModal').classList.add('hidden');
}

// ================== CATEGORY LOGIC ==================

function loadCategories(selectedId = null) {
  const type = document.getElementById('transType').value;
  const select = document.getElementById('categorySelect');

  fetch(`/api/categories?type=${type}`)
    .then(res => res.json())
    .then(data => {
      select.innerHTML = '';
      data.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = cat.name;
        if (selectedId && cat.id === selectedId) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });
    });
}

function showAddCategory() {
  document.getElementById('addCategoryBox').classList.toggle('hidden');
}

function createCategory() {
  const nameInput = document.getElementById('newCategoryName');
  const name = nameInput.value.trim();
  const type = document.getElementById('transType').value;

  if (!name) {
    alert('Nhập tên danh mục');
    return;
  }

  fetch('/api/category/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name, type })
  })
    .then(res => res.json())
    .then(cat => {
      if (cat.error) {
        alert(cat.error);
        return;
      }

      // Reload danh mục và chọn luôn cái mới
      loadCategories(cat.id);

      // Reset UI
      nameInput.value = '';
      document.getElementById('addCategoryBox').classList.add('hidden');
    });
}
