function xprezCheckVideoPoster() {
    var $activeElement = $(document.activeElement);
    if ($activeElement.hasClass('js-xprez-video-with-poster')) {
        $activeElement.closest('.xprez-module').find('.js-xprez-video-poster').hide();
        $activeElement.removeClass('js-xprez-video-with-poster');
    }
}

function xprezInitVideoHidePoster() {
    focus();
    $(window).blur(function() { xprezCheckVideoPoster(); });  // detect if window lose focus, possibly to iframe
    setInterval(xprezCheckVideoPoster, 500);  // Fallback in case blur detection does not work. For example when you have multiple iframes.

    // in case css pointer-events: none does not work (opera mini)
    $('.js-xprez-video-poster').click(function () {
        $(this).hide();
    });
}

xprezInitVideoHidePoster();
