$(document).ready(function() {
    $('#like-btn').click(function() {
        var catecategoryIdVar = $(this).attr('data-categoryid');
        $.get(
            '/rango/like_category/',
            { 'category_id': catecategoryIdVar },
            function(data) {
                $('#like-count').html(data);
                $('#like-btn').hide();
            }
        );
    });
});

$('#search-input').keyup(function() {
    var query;
    query = $(this).val();

    $.get('/rango/suggest/',
        {'suggestion': query},
        function(data) {
            $('#categories-listing').html(data);
        }
    );
});