document.addEventListener('DOMContentLoaded', function() {
  let preferredColorScheme = localStorage.getItem('preferred-color-scheme');
  if (!preferredColorScheme) {
    preferredColorScheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    localStorage.setItem('preferred-color-scheme', preferredColorScheme);
  }

  // Set the initial logo image based on the preferred color scheme
  const logoSrc = preferredColorScheme === 'light' ? '../common/img/degree-planner-logo-dark.png' : '../common/img/degree-planner-logo.png';
  document.getElementById('degree-planner-logo').src = logoSrc;

  // Set the initial system mode icon based on the preferred color scheme
  const systemModeIconSrc = preferredColorScheme === 'dark' ? '../common/img/moon.png' : '../common/img/sun.png';
  document.getElementById('system-mode-icon').src = systemModeIconSrc;

  // Set the initial menu icon based on the preferred color scheme
  const menuIconSrc = preferredColorScheme === 'dark' ? '../common/img/menu-dark.png' : '../common/img/menu.png';
  document.getElementById('menu-icon').src = menuIconSrc;

  // Apply the preferred color scheme
  document.documentElement.className = preferredColorScheme;

  // Add event listener to the system mode icon
  document.getElementById('system-mode-icon').addEventListener('click', toggleDarkMode);
});

function toggleDarkMode() {
  const currentTheme = document.documentElement.className || 'light';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  // Update the logo image
  const logoSrc = newTheme === 'light' ? '../common/img/degree-planner-logo-dark.png' : '../common/img/degree-planner-logo.png';
  document.getElementById('degree-planner-logo').src = logoSrc;

  // Update the system mode icon
  const systemModeIconSrc = newTheme === 'dark' ? '../common/img/moon.png' : '../common/img/sun.png';
  document.getElementById('system-mode-icon').src = systemModeIconSrc;

  // Update the menu icon
  const menuIconSrc = newTheme === 'dark' ? '../common/img/menu-dark.png' : '../common/img/menu.png';
  document.getElementById('menu-icon').src = menuIconSrc;

  // Apply the new theme
  document.documentElement.className = newTheme;
  localStorage.setItem('preferred-color-scheme', newTheme);
}

