(function ($) {

    "use strict";

    $('nav .dropdown').hover(function () {
        var $this = $(this);
        $this.addClass('show');
        $this.find('> a').attr('aria-expanded', true);
        $this.find('.dropdown-menu').addClass('show');
    }, function () {
        var $this = $(this);
        $this.removeClass('show');
        $this.find('> a').attr('aria-expanded', false);
        $this.find('.dropdown-menu').removeClass('show');
    });

})(jQuery);

function showToast(message) {
    const toast = document.getElementById('toast');
    const progressBar = toast.querySelector('.progress');
    const closeIcon = toast.querySelector('.close');
    const messageElement = toast.querySelector('.text.text-2');

    messageElement.textContent = message;
    toast.classList.add('active');
    progressBar.classList.add('active');

    const timer = setTimeout(() => {
        toast.classList.remove('active');
    }, 5000);

    closeIcon.addEventListener('click', () => {
        toast.classList.remove('active');
        setTimeout(() => {
            progressBar.classList.remove('active');
        }, 300);
        clearTimeout(timer);
    });
}

// Listen for custom event
document.addEventListener('subscriptionSuccess', function(e) {
    showToast(e.detail.message);
});
