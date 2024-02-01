window.addEventListener('load', function() {
  let preferredColorScheme = localStorage.getItem('preferred-color-scheme');
  if (!preferredColorScheme) {
    preferredColorScheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    localStorage.setItem('preferred-color-scheme', preferredColorScheme);
  }
  const logoSrc = preferredColorScheme === 'dark' ? '../common/img/degree-planner-logo.png' : '../common/img/degree-planner-logo-dark.png';
  document.getElementById('degree-planner-logo').src = logoSrc;
});

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  const newColorScheme = e.matches ? 'dark' : 'light';
  localStorage.setItem('preferred-color-scheme', newColorScheme);
  const newImageSrc = newColorScheme === 'dark' ? '../common/img/degree-planner-logo.png' : '../common/img/degree-planner-logo-dark.png';
  document.getElementById('degree-planner-logo').src = newImageSrc;
});