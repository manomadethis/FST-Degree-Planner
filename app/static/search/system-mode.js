document.addEventListener('DOMContentLoaded', function() {
  let preferredColorScheme = localStorage.getItem('preferred-color-scheme');
  if (!preferredColorScheme) {
    preferredColorScheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    localStorage.setItem('preferred-color-scheme', preferredColorScheme);
  }

  // Apply the preferred color scheme
  document.documentElement.className = preferredColorScheme;

  updateSystemModeIcons(preferredColorScheme);


  // Add event listener to the system mode mobile icon
  document.getElementById('system-mode-mobile-icon').addEventListener('click', toggleDarkMode);
});

function toggleDarkMode() {
  const currentTheme = document.documentElement.className || 'light';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  // Apply the new theme
  document.documentElement.className = newTheme;
  localStorage.setItem('preferred-color-scheme', newTheme);

  // Update the system mode icons
  updateSystemModeIcons(newTheme);

}

function updateSystemModeIcons(theme) {
  const systemModeMobileIcon = document.getElementById('system-mode-mobile-icon');

  if (theme === 'dark') {
      systemModeMobileIcon.innerHTML = 'wb_sunny';
  } else {
      systemModeMobileIcon.innerHTML = 'nights_stay';
  }
}
