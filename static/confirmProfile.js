function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Проверяем, начинается ли куки с нужного имени
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitProfileForm() {
    const selectedProfile = document.querySelector('input[name="selected_profile"]:checked');

    if (selectedProfile) {
        const formData = new FormData();
        formData.append('selected_profile', selectedProfile.value);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                console.log('Form submitted successfully:', data);
                // Дополнительная логика после успешного ответа
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }
    // Обработка, если профиль не выбран
}
