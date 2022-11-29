function xprezInitVimeo() {
    $('.js-video-with-poster').each(function (index, el) {
        var $wrapper = $(el);
        var $iframe = $wrapper.find('.js-vimeo');
        if ($iframe.length) {
            var $poster = $wrapper.find('.js-poster');
            var player = new Vimeo.Player($iframe[0]);
            player.on('play', function() {
                $poster.hide();
            });
        }
    });
}

function xprezInitYoutube() {
    $('.js-video-with-poster').each(function (index, el) {
        var $wrapper = $(el);
        var $iframe = $wrapper.find('.js-youtube');
        if ($iframe.length) {
            var $poster = $wrapper.find('.js-poster');
            new YT.Player($iframe.attr('id'), {
                events: {
                    'onStateChange': function(event) {
                        if (event.data == YT.PlayerState.PLAYING) {
                            $poster.hide();
                        }
                    }
                }
            });
        }
    });
}

function xprezInitVideoFallback() {
    // just in case pointer-events: none does not work (opera mini)
    $('.js-video-with-poster .js-poster').click(function () {
        $(this).hide();
    });
}

$(function () {
    xprezInitVimeo();
    // youtube init is handled by the youtube onYoutubeIframeAPIReady callback
    xprezInitVideoFallback();
});

function onYouTubeIframeAPIReady() { xprezInitYoutube; }
window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
