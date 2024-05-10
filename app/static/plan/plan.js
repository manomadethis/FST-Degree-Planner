window.onload = function() {
    document.getElementById('create-plan-button').addEventListener('click', function() {
        document.querySelector('.no-plan').style.display = 'none';
        document.querySelector('.create').style.display = 'block';
        document.querySelector('.degree-plan').style.display = 'none';
    });
    document.getElementById('create-button').addEventListener('click', function() {
        document.querySelector('.no-plan').style.display = 'none';
        document.querySelector('.create').style.display = 'none';
        document.querySelector('.degree-plan').style.display = 'block';
    });
}