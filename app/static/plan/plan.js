$(document).ready(function() {
    $('.search-select').select2();
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create').addEventListener('click', function() {
        document.querySelector('.plan-creation').style.display = 'block';
    });
});

$(document).ready(function() {
    // Populate majors
    $.ajax({
        url: '/get_majors',
        type: 'GET',
        success: function(data) {
            var select1 = $('#select-major1');
            var select2 = $('#select-major2');

            for (var i = 0; i < data.length; i++) {
                var option = $('<option value="' + data[i] + '">' + data[i] + '</option>');
                select1.append(option.clone());
                select2.append(option.clone());
            }
        }
    });

    // Populate minors
    $.ajax({
        url: '/get_minors',
        type: 'GET',
        success: function(data) {
            var select1 = $('#select-minor1');
            var select2 = $('#select-minor2');

            for (var i = 0; i < data.length; i++) {
                var option = $('<option value="' + data[i] + '">' + data[i] + '</option>');
                select1.append(option.clone());
                select2.append(option.clone());
            }
        }
    });

    // Populate programmes
    $.ajax({
        url: '/get_programmes',
        type: 'GET',
        success: function(data) {
            var select = $('#select-programme');

            for (var i = 0; i < data.length; i++) {
                var option = $('<option value="' + data[i] + '">' + data[i] + '</option>');
                select.append(option);
            }
        }
    });
});

$(document).ready(function() {
    $('#interest-input').on('keypress', function(e) {
        if (e.which == 13) {  // 'Enter' key
            e.preventDefault();

            // Get the input value
            var interest = $(this).val();

            // Create a new chip
            var chip = $('<div class="chip">' + interest + '</div>');

            // Append the chip to the #interest-chips div
            $('#interest-chips').append(chip);

            // Clear the input field
            $(this).val('');
        }
    });
});

$(document).ready(function() {
    $('#create-button').on('click', function(e) {
        e.preventDefault();

        // Get the values of the select dropdowns
        var major1 = $('#select-major1').val();
        var major2 = $('#select-major2').val();
        var minor1 = $('#select-minor1').val();
        var minor2 = $('#select-minor2').val();
        var programme = $('#select-programme').val();

        // Check for duplicate selections excluding the default option
        if ((major1 == major2 && major1 != "") || (minor1 == minor2 && minor1 != "")) {
            alert('Duplicate selections are not allowed');
            return;
        }

        /// Check if a valid combination was chosen
        if (programme && !(major1 || major2 || minor1 || minor2)) {
            processDegreePlan('/process_programme', {programme: programme});
        } else if (major1 && !(major2 || minor1 || minor2 || programme)) {
            processDegreePlan('/process_single_major', {major1: major1});
        } else if (major2 && !(major1 || minor1 || minor2 || programme)) {
            processDegreePlan('/process_single_major', {major1: major2});
        } else if (major1 && major2 && !(minor1 || minor2 || programme)) {
            processDegreePlan('/process_two_majors', {major1: major1, major2: major2});
        } else if (major1 && minor1 && !(major2 || minor2 || programme)) {
            processDegreePlan('/process_major_and_minor', {major1: major1, minor1: minor1});
        } else if (major2 && minor1 && !(major1 || minor2 || programme)) {
            processDegreePlan('/process_major_and_minor', {major1: major2, minor1: minor1});
        } else if (major1 && minor1 && minor2 && !(major2 || programme)) {
            processDegreePlan('/process_major_and_two_minors', {major1: major1, minor1: minor1, minor2: minor2});
        } else {
            alert('Invalid combination chosen');
        }
    });
});

function processDegreePlan(url, data) {
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            // Handle the response here
            console.log(response.message);
        },
        error: function(error) {
            // Handle error here
            console.log(error);
        }
    });
}
