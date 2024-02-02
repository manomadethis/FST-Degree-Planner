function openNav() {
	document.getElementById("sidebar-menu").style.width = "13.25rem";
	document.getElementById("menu-icon").style.display = "none";
	document.getElementById("close-icon").style.display = "block";
}

function closeNav() {
	document.getElementById("sidebar-menu").style.width = "0";
	document.getElementById("menu-icon").style.display = "block";
	document.getElementById("close-icon").style.display = "none";
}

window.onclick = function(event) {
	if (event.target == document.getElementById("sidebar-menu")) {
		closeNav();
	}
}

window.addEventListener('resize', function() {
    if (window.innerWidth > 1000) {
        closeNav();
        document.getElementById("menu-icon").style.display = "none";
    } else {
        document.getElementById("menu-icon").style.display = "block";
    }
});
