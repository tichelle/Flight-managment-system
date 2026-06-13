// Flight Detail Card - Favorite Toggle
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.fav-btn');
  if (!btn) return;

  // Visual toggle for UX; form will still submit to server for persistence
  const pressed = btn.getAttribute('aria-pressed') === 'true';
  btn.setAttribute('aria-pressed', String(!pressed));

  const heart = btn.querySelector('.heart');
  if (heart) {
    heart.textContent = pressed ? '♡' : '♥';
  }
});
