document.addEventListener('DOMContentLoaded', function () {
  const toggles = document.querySelectorAll('[data-toggle="theme"]');
  toggles.forEach(function(toggle) {
    toggle.addEventListener('click', function() {
      document.body.classList.toggle('dark-theme');
    });
  });
});
