document.addEventListener("DOMContentLoaded", function () {
    // Оновлення середнього рейтингу
    const averageRatingBlocks = document.querySelectorAll('.average-star-rating');
    averageRatingBlocks.forEach(function (ratingBlock) {
        const stars = ratingBlock.querySelectorAll('.star');
        const averageRating = ratingBlock.getAttribute('data-average-rating');
        highlightStars(stars, averageRating);
    });

    // Оновлення рейтингу користувача
    const userRatingBlocks = document.querySelectorAll('.user-star-rating');
    userRatingBlocks.forEach(function (ratingBlock) {
        const stars = ratingBlock.querySelectorAll('.star');
        const userRating = ratingBlock.getAttribute('data-user-rating');
        highlightStars(stars, userRating); // Відобразити оцінку користувача
    });

    function highlightStars(stars, rating) {
        stars.forEach(function (star) {
            star.textContent = star.getAttribute('data-value') <= rating ? '★' : '☆'; // Заповнені та пусті зірки
        });
    }
});
