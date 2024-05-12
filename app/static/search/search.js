$(document).ready(function() {
    var searchButton = $('#search-bar').next();

    searchButton.on('click', function(event) {
        event.preventDefault();
        performSearch();
    });

    $('#search-bar').on('keypress', function(event) {
        if (event.which == 13) {
            event.preventDefault();
            searchButton.click();
        }
    });

    $('#search-bar').on('input', performSearch);
    $('input[name="filter"]').on('change', performSearch);

    function performSearch() {
        var searchQuery = $('#search-bar').val();
        var filterOption = $('input[name="filter"]:checked').val();

        var requestData = { query: searchQuery };
        if (filterOption) {
            requestData.filter = filterOption;
        }

        if (searchQuery.length > 2) {
            fetchSearchResults(requestData);
        } else {
            $('#search-results').hide();
        }
    }
});

function fetchSearchResults(requestData) {
    $.ajax({
        url: '/search_results',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: handleSearchResults
    });
}

function handleSearchResults(response) {
    var resultsDiv = $('#search-results');
    resultsDiv.empty();

    var hasResults = false;
    for (var category in response) {
        var results = response[category];
        if (results.length > 0) {
            hasResults = true;
            resultsDiv.append('<h6>' + category + '</h6>');
            appendResults(results, resultsDiv, category);
        }
    }

    if (hasResults) {
        resultsDiv.show();
    } else {
        resultsDiv.hide();
    }
}

function appendResults(results, resultsDiv, category) {
    results.forEach(function(result) {
        var resultElement = $('<p class="search-result">' + result + '</p>');
        resultElement.on('click', function() {
            fetchResults(result, category);
        });
        resultsDiv.append(resultElement);
    });
}

function fetchResults(result, category) {
    category = category.trim(); // Trim the category string

    var resultParts = result.split(' ');
    var resultType = category;
    var resultName;
    var url;

    // Check if the result matches the format ABCD1234
    if (/^[A-Z]{4}\d{4}$/.test(resultParts[0])) {
        url = '/course/';
        resultName = resultParts[0]; // Use the first part as the course code
    } else {
        url = '/' + resultType.toLowerCase() + '/';
        resultName = resultParts.join(' '); // Use space instead of '%20'
    }

    $.ajax({
        url: url + encodeURIComponent(resultName), // Use '%20' instead of space
        method: 'GET',
        success: function(data) {
            var details;
            var description = data.description;
            var formattedDescription = description ? formatDescription(description) : '';

            // Generate details based on category
            switch(category.toLowerCase()) {
                case 'major':
                    details = generateMajorDetails(data);
                    break;
                case 'minor':
                    details = generateMinorDetails(data);
                    break;
                case 'programme':
                    details = generateProgrammeDetails(data);
                    break;
                case 'faculty':
                    details = generateFacultyDetails(data);
                    break;
                case 'department':
                    details = generateDepartmentDetails(data);
                    break;
                default:
                    details = generateCourseDetails(data, formattedDescription);
            }

            $('#selected-search-item').html(details);
        }
    });
}

function generateMajorDetails(data) {
    var html = '<h2>' + data.name + '  (Major)' + '</h2>';
    html += '<p><strong>Level 1 Credits: </strong>' + data.level1_credits + '</p>';
    html += '<p><strong>Advanced Credits: </strong>' + data.advanced_credits + '</p>';
    html += '<p><strong>Compulsory Level 1 Courses</strong></p><ul>';
    data.level1_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Compulsory Advanced Courses</strong></p><ul>';
    data.advanced_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Department: </strong>' + data.department + '</p>';
    return html;
}

function generateMinorDetails(data) {
    var html = '<h2>' + data.name + ' (Minor)' + '</h2>';
    html += '<p><strong>Level 1 Credits: </strong>' + data.level1_credits + '</p>';
    html += '<p><strong>Advanced Credits: </strong>' + data.advanced_credits + '</p>';
    html += '<p><strong>Compulsory Level 1 Courses</strong></p><ul>';
    data.level1_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Compulsory Advanced Courses</strong></p><ul>';
    data.advanced_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Department: </strong>' + data.department + '</p>';
    return html;
}

function generateProgrammeDetails(data) {
    var html = '<h2>' + data.name + ' (B.Sc.)' + '</h2>';
    html += '<p><strong>Level 1 Credits: </strong>' + data.level1_credits + '</p>';
    html += '<p><strong>Advanced Credits: </strong>' + data.advanced_credits + '</p>';
    html += '<p><strong>Compulsory Level 1 Courses</strong></p><ul>';
    data.level1_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Compulsory Advanced Courses</strong></p><ul>';
    data.advanced_courses.forEach(function(course) {
        html += '<li>' + course + '</li>';
    });
    html += '</ul><p><strong>Department: </strong>' + data.department + '</p>';
    return html;
}

function generateFacultyDetails(data) {
    departments = data.departments.map(department => '<li>' + department + '</li>').join('');
    return '<h2>' + data.name + '</h2>' +
        '<p><strong>Level 1 Credits Required:</strong> ' + data.level_1_credits_required + '</p>' +
        '<p><strong>Advanced Credits Required:</strong> ' + data.advanced_credits_required + '</p>' +
        '<p><strong>Foundation Credits Required:</strong> ' + data.foundation_credits_required + '</p>' +
        '<p><strong>Departments:</strong><ul>' + departments + '</ul></p>' +
        '<p><strong>Notes:</strong> ' + data.notes + '</p>';
}

function generateDepartmentDetails(data) {
    var majors = data.majors.map(major => '<li>' + major + '</li>').join('');
    var minors = data.minors.map(minor => '<li>' + minor + '</li>').join('');
    var programmes = data.programmes.map(programme => '<li>' + programme + '</li>').join('');

    return '<h2>' + 'Department of ' + data.name + '</h2>' +
        '<p><strong>Faculty Name:</strong> ' + data.faculty_name + '</p>' +
        '<p><strong>Course Count:</strong> ' + data.course_count + '</p>' +
        '<p><strong>Majors:</strong><ul>' + majors + '</ul></p>' +
        '<p><strong>Minors:</strong><ul>' + minors + '</ul></p>' +
        '<p><strong>Programmes:</strong><ul>' + programmes + '</ul></p>'
}

function generateCourseDetails(course, formattedDescription) {
    return '<h2>' + course.title + ' (' + course.course_code + ')</h2>' +
        '<p><strong>Level:</strong> ' + course.level + '</p>' +
        '<p><strong>Credit:</strong> ' + course.credit + '</p>' +
        '<p><strong>Semester:</strong> ' + course.semester + '</p>' +
        '<p><strong>Is Elective:</strong> ' + (course.is_elective ? 'Yes' : 'No') + '</p>' +
        '<p><strong>Department:</strong> ' + course.department_name + '</p>' +
        '<p><strong>Faculty:</strong> ' + course.faculty_name + '</p>' +
        '<div class="description">' + formattedDescription + '</div>';
}

function formatDescription(description) {
    var lines = description.split('\n');
    lines.splice(0, 3);
    var newDescription = lines.join('\n');

    var sections = newDescription.split('\n\n');
    var formattedDescription = '';
    sections.forEach(function(section) {
        var lines = section.trim().split('\n');
        formattedDescription += '<div class="section">';
        lines.forEach(function(line) {
            if (line.startsWith('-')) {
                formattedDescription += '<div class="indent"><ul><li>' + line.trim().substring(1).trim() + '</li></ul></div>';
            } else if (line.startsWith('Pre-requisites:') || line.startsWith('Pre-requisite:') || line.startsWith('Co-requisites:') || line.startsWith('Co-requisite:') || line.startsWith('Course Content:') || line.startsWith('Evaluation:')) {
                formattedDescription += '<p><strong>' + line.trim() + '</strong></p>';
            } else {
                formattedDescription += '<p>' + line.trim() + '</p>';
            }
        });
        formattedDescription += '</div>';
    });
    return formattedDescription;
}
