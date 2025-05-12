$(document).ready(function() {
    $('#chatbot-form').on('submit', function(e) {
        e.preventDefault();
        var chatbotUrl = $(this).data('chatbot-url'); // Get URL from data attribute
        $.ajax({
            url: chatbotUrl,
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                // Extract the chatbot-response content from the response HTML
                var responseText = $(response).find('#chatbot-response').text();
                if (responseText) {
                    $('#chatbot-response').text(responseText);
                } else {
                    $('#chatbot-response').text('No response received.');
                }
            },
            error: function(xhr, status, error) {
                $('#chatbot-response').text('Error processing request: ' + error);
            }
        });
    });
});