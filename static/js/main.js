document.addEventListener('DOMContentLoaded', function() {
    // Handle sub-menu functionality for inventory dropdown
    const inventoryDropdown = document.getElementById('inventoryDropdown');
    const subMenus = document.querySelectorAll('.dropdown-submenu');

    subMenus.forEach(function(subMenu) {
        const toggle = subMenu.querySelector('.dropdown-toggle');
        const menu = subMenu.querySelector('.dropdown-menu');

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Hide other sub-menus
            subMenus.forEach(function(otherSubMenu) {
                if (otherSubMenu !== subMenu) {
                    otherSubMenu.querySelector('.dropdown-menu').classList.remove('show');
                }
            });

            // Toggle current sub-menu
            menu.classList.toggle('show');
        });
    });

    // Close sub-menus when clicking outside
    document.addEventListener('click', function(e) {
        if (!inventoryDropdown.contains(e.target)) {
            subMenus.forEach(function(subMenu) {
                subMenu.querySelector('.dropdown-menu').classList.remove('show');
            });
        }
    });

    // Close sub-menus when main dropdown closes
    inventoryDropdown.addEventListener('hidden.bs.dropdown', function() {
        subMenus.forEach(function(subMenu) {
            subMenu.querySelector('.dropdown-menu').classList.remove('show');
        });
    });
});
