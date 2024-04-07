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

    $('#search-bar').on('input', function(event) {
        performSearch();
    });

    $('input[name="filter"]').on('change', function(event) {
        performSearch();
    });

    function performSearch() {
        var searchQuery = $('#search-bar').val();
        var filterOption = $('input[name="filter"]:checked').val();

        var requestData = { query: searchQuery };
        if (filterOption) {
            requestData.filter = filterOption;
        }

        if (searchQuery.length > 2) {
            $.ajax({
                url: '/search_results',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(requestData),
                success: function(response) {
                    var resultsDiv = $('#search-results');
                    resultsDiv.empty();

                    var hasResults = false;
                    for (var category in response) {
                        var results = response[category];
                        if (results.length > 0) {
                            hasResults = true;
                            resultsDiv.append('<h6>' + category + '</h6>');
                            results.forEach(function(result) {
                                var resultElement = $('<p class="search-result">' + result + '</p>');
                                resultElement.on('click', (function(result) {
                                    return function() {
                                        var courseCode = result.split(' ')[0];
                                        $.ajax({
                                            url: '/course/' + encodeURIComponent(courseCode),
                                            method: 'GET',
                                            success: function(course) {
                                                var description = course.description;
                                                var formattedDescription = formatDescription(description);
                                                var courseDetails = '<h2>' + course.title + ' (' + course.course_code + ')</h2>' +
                                                                    '<p><strong>Level:</strong> ' + course.level + '</p>' +
                                                                    '<p><strong>Credit:</strong> ' + course.credit + '</p>' +
                                                                    '<p><strong>Semester:</strong> ' + course.semester + '</p>' +
                                                                    '<p><strong>Is Elective:</strong> ' + (course.is_elective ? 'Yes' : 'No') + '</p>' +
                                                                    '<p><strong>Department:</strong> ' + course.department_name + '</p>' +
                                                                    '<p><strong>Faculty:</strong> ' + course.faculty_name + '</p>' +
                                                                    '<div class="description">' + formattedDescription + '</div>';
                                                $('#selected-search-item').html(courseDetails);
                                            }
                                        });
                                    };
                                })(result));
                                resultsDiv.append(resultElement);
                            });
                        }
                    }

                    if (hasResults) {
                        resultsDiv.show();
                    } else {
                        resultsDiv.hide();
                    }
                }
            });
        } else {
            $('#search-results').hide();
        }
    }
});

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
