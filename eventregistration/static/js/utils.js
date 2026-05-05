/**
 * EventHub — Shared JS utilities loaded on every page.
 */

/**
 * Format an ISO date string into a human-readable local date + time.
 * @param {string} iso
 * @returns {string}
 */
function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * HTML-escape a string to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Show a toast notification at the bottom of the screen.
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 */
function showToast(message, type = 'info') {
  const colours = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-brand-600',
  };

  const toast = document.createElement('div');
  toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl shadow-xl text-white text-sm font-medium
                     ${colours[type] || colours.info} transition-all duration-300 opacity-0 translate-y-2`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.classList.remove('opacity-0', 'translate-y-2');
  });

  // Auto-remove after 4 s
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
