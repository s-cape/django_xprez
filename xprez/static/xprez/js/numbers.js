function initNumbers() {
    $('.js-number-container').each(function (index, el) {
        var $el = $(el);
        $el.css('min-width', ($el.width() + 10).toString() + 'px');
    });
    $('.js-counter-up').counterUp({
        // delay: 30,
        time: 3000
    });
}


$(document).ready(function () {
    initNumbers();
});