window.addEventListener('load', function() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.getElementById('search-icon').src = '../common/img/search-icon-dark.svg';
    }
  });

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  const newImageSrc = e.matches ? '../common/img/search-icon-dark.svg' : '../common/img/search-icon.svg';
  document.getElementById('search-icon').src = newImageSrc;
});