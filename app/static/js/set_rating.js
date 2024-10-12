document.addEventListener("DOMContentLoaded", function () {
    // Оновлення та взаємодія з рейтингом користувача
    const userRatingBlocks = document.querySelectorAll('.user-star-rating');
    userRatingBlocks.forEach(function (ratingBlock) {
        const stars = ratingBlock.querySelectorAll('.star');
        const photoId = ratingBlock.getAttribute('data-photo-id');
        const userRatingDisplay = document.getElementById(`user-rating-${photoId}`);
        let userRating = ratingBlock.getAttribute('data-user-rating');  // Локальна змінна userRating

        // Відображення рейтингу користувача при завантаженні
        highlightStars(stars, userRating);
        
        // Взаємодія з зірками (mouseover, mouseout, click)
        stars.forEach(function (star) {
            // Підсвічуємо зірки при наведенні
            star.addEventListener('mouseover', function () {
                highlightStars(stars, this.getAttribute('data-value'));
            });

            star.addEventListener('mouseout', function () {
                highlightStars(stars, ratingBlock.getAttribute('data-user-rating')); // Повертаємо попередню оцінку користувача
            });
            
            star.addEventListener('click', function () {
                const ratingValue = this.getAttribute('data-value');
                submitRating(photoId, ratingValue, userRatingDisplay, ratingBlock, stars);
            });
        });
    });

    function highlightStars(stars, rating) {
        stars.forEach(function (star) {
            star.textContent = star.getAttribute('data-value') <= rating ? '★' : '☆'; // Заповнені та порожні зірки
        });
    }

    // Відправка рейтингу користувача на сервер
    function submitRating(photoId, rating, userRatingDisplay, ratingBlock, stars) {
        fetch('/photo/ratings/' + photoId + '/rate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // Передаємо CSRF токен
            },
            body: JSON.stringify({
                'rating': rating
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Оновлюємо атрибут 'data-user-rating' та локальну змінну
                ratingBlock.setAttribute('data-user-rating', data.user_rating);
                userRating = data.user_rating; // Оновлюємо локальну змінну userRating

                // Оновлюємо зірки для нового рейтингу
                highlightStars(stars, userRating)

                // Оновлюємо текст з новим рейтингом користувача
                userRatingDisplay.textContent = userRating; // Відображаємо новий рейтинг
            } else {
                alert('Failed to submit rating: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Отримання CSRF токену
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
