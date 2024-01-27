function submitCreatePageForm(redirect_page) {
    // Собираем данные с формы
    let formData = new FormData(document.getElementById('createPageForm'));

    // Отправляем данные на сервер
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            window.location.href = redirect_page;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}