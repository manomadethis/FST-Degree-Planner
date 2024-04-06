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
                                resultsDiv.append('<p>' + result + '</p>');
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