document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.display = 'none';
        }, 3000);
    });

    // Smooth scroll for anchor links
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            target.scrollIntoView({ behavior: 'smooth' });
        });
    });
});
