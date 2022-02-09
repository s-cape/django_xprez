function initNumbers() {
    $('.js-number-container').each(function (index, el) {
        var $el = $(el);
        var w = $el.outerWidth();
        $el.css('min-width', (w + 10).toString() + 'px');
    });
    $('.js-counter-up').counterUp({
        time: 3000
    });
}

$(document).ready(function () {
    initNumbers();
});