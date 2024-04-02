document.addEventListener('DOMContentLoaded', function() {
    let preferredColorScheme = localStorage.getItem('preferred-color-scheme');
    if (!preferredColorScheme) {
      preferredColorScheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      localStorage.setItem('preferred-color-scheme', preferredColorScheme);
    }

    // Set the initial logo image based on the preferred color scheme
    const logoSrc = preferredColorScheme === 'light' ? '../static/common/img/degree-planner-logo-dark.png' : '../static/common/img/degree-planner-logo.png';
    document.getElementById('degree-planner-logo').src = logoSrc;

    // Set the initial system mode icon based on the preferred color scheme
    const systemModeIconSrc = preferredColorScheme === 'dark' ? '../static/common/img/moon.png' : '../static/common/img/sun.png';
    document.getElementById('system-mode-icon').src = systemModeIconSrc;

    // Set the initial system mode mobile icon based on the preferred color scheme
    const systemModeMobileIconSrc = preferredColorScheme === 'dark' ? '../static/common/img/moon.png' : '../static/common/img/sun.png';
    document.getElementById('system-mode-mobile-icon').src = systemModeMobileIconSrc;

    // Set the initial menu icon based on the preferred color scheme
    const menuIconSrc = preferredColorScheme === 'dark' ? '../static/common/img/menu-dark.png' : '../static/common/img/menu.png';
    document.getElementById('menu-icon').src = menuIconSrc;

    // Set the initial close menu icon based on the preferred color scheme
    const closeIconSrc = preferredColorScheme === 'dark' ? '../static/common/img/close-menu-dark.png' : '../static/common/img/close-menu.png';
    document.getElementById('close-icon').src = closeIconSrc;

    // Apply the preferred color scheme
    document.documentElement.className = preferredColorScheme;

    // Add event listener to the system mode icon
    document.getElementById('system-mode-icon').addEventListener('click', toggleDarkMode);

    // Add event listener to the system mode mobile icon
    document.getElementById('system-mode-mobile-icon').addEventListener('click', toggleDarkMode);
  });

  function toggleDarkMode() {
    const currentTheme = document.documentElement.className || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    // Update the logo image
    const logoSrc = newTheme === 'light' ? '../static/common/img/degree-planner-logo-dark.png' : '../static/common/img/degree-planner-logo.png';
    document.getElementById('degree-planner-logo').src = logoSrc;

    // Update the system mode icon
    const systemModeIconSrc = newTheme === 'dark' ? '../static/common/img/moon.png' : '../static/common/img/sun.png';
    document.getElementById('system-mode-icon').src = systemModeIconSrc;

    // Update the system mode mobile icon
    const systemModeMobileIconSrc = newTheme === 'dark' ? '../static/common/img/moon.png' : '../static/common/img/sun.png';
    document.getElementById('system-mode-mobile-icon').src = systemModeMobileIconSrc;

    // Update the menu icon
    const menuIconSrc = newTheme === 'dark' ? '../static/common/img/menu-dark.png' : '../static/common/img/menu.png';
    document.getElementById('menu-icon').src = menuIconSrc;

    // Update the close menu icon
    const closeIconSrc = newTheme === 'dark' ? '../static/common/img/close-menu-dark.png' : '../static/common/img/close-menu.png';
    document.getElementById('close-icon').src = closeIconSrc;

    // Apply the new theme
    document.documentElement.className = newTheme;
    localStorage.setItem('preferred-color-scheme', newTheme);
  }