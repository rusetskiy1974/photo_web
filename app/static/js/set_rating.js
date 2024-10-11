document.addEventListener("DOMContentLoaded", function () {
    const ratingBlocks = document.querySelectorAll('.star-rating');

    ratingBlocks.forEach(function (ratingBlock) {
        const stars = ratingBlock.querySelectorAll('.star');
        const photoId = ratingBlock.getAttribute('data-photo-id');
        const userRatingDisplay = document.getElementById(`user-rating-${photoId}`);

        stars.forEach(function (star) {
            // Підсвічуємо зірки при наведенні
            star.addEventListener('mouseover', function () {
                highlightStars(stars, this.getAttribute('data-value'));
            });

            star.addEventListener('mouseout', function () {
                clearStars(stars);
            });

            star.addEventListener('click', function () {
                const ratingValue = this.getAttribute('data-value');
                submitRating(photoId, ratingValue, userRatingDisplay);
                highlightStars(stars, ratingValue);  // Залишаємо підсвічені зірки після кліку
            });
        });
    });

    function highlightStars(stars, rating) {
        stars.forEach(function (star) {
            star.textContent = star.getAttribute('data-value') <= rating ? '★' : '☆';  // Заповнюємо зірки
        });
    }

    function clearStars(stars) {
        stars.forEach(function (star) {
            star.textContent = '☆';  // Очищаємо зірки
        });
    }

    function submitRating(photoId, rating, userRatingDisplay) {
        fetch('/photo/ratings/' + photoId + '/rate/', {  // Правильний URL для оцінки
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()  // Передаємо CSRF токен
            },
            body: JSON.stringify({
                'rating': rating
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userRatingDisplay.textContent = data.user_rating;  // Оновлюємо рейтинг користувача
            } else {
                alert('Failed to submit rating: ' + data.error);  // Обробляємо помилку
            }
        })
        .catch(error => {
            console.error('Error:', error);  // Виводимо помилку в консоль
        });
    }

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
