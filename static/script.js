function beginFill(taskId) {
  $.ajax({
    type: 'POST',
    url: '/begin_fill/',
    data: {
      csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
      task_id: taskId,
    },
    success: function (data) {
      window.location.href = data.redirect_url;
    },
    error: function (error) {
      console.error('Error:', error);
    }
  });
}
