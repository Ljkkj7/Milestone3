document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const sideMenu = document.getElementById('sideMenu');
  
    let menuOpen = false;
  
    function toggleMenu() {
      sideMenu.classList.toggle('open');
      hamburger.classList.toggle('open');
      menuOpen = sideMenu.classList.contains('open');
  
      if (menuOpen) {
        // Add outside click listener
        document.addEventListener('click', handleOutsideClick);
      } else {
        // Remove it if menu is closed
        document.removeEventListener('click', handleOutsideClick);
      }
    }
  
    function handleOutsideClick(e) {
      if (!sideMenu.contains(e.target) && e.target !== hamburger) {
        toggleMenu(); // Close the menu
      }
    }
  
    hamburger.addEventListener('click', function (e) {
      e.stopPropagation(); // Prevent document click from firing first
      toggleMenu();
    });
  });