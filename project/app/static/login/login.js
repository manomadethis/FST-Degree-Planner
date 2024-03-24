function openTab(evt, tabName) {
    // Prevent the default action of the link
    evt.preventDefault();

    // Get all elements with class="tabcontent" and hide them
    var i, tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Show the current tab
    document.getElementById(tabName).style.display = "block";
}

window.onload = function() {
    // Hide the login tab
    document.getElementById('login').style.display = 'none';

    // Show the signup tab
    document.getElementById('signup').style.display = 'block';
};