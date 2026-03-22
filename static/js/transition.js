// Smooth page transitions
function navigateTo(url) {
  const frame = document.querySelector('.phone-frame');
  if (frame) {
    frame.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
    frame.style.opacity = '0';
    frame.style.transform = 'translateY(-8px)';
    setTimeout(() => { window.location.href = url; }, 240);
  } else {
    window.location.href = url;
  }
}

// Intercept all internal links for smooth transition
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.startsWith('/') && !href.startsWith('//')) {
      link.addEventListener('click', e => {
        e.preventDefault();
        navigateTo(href);
      });
    }
  });
});
