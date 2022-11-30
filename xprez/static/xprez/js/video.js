function initPosters() {
    $('.js-video-with-poster').each(function (index, el) {
        var $el = $(el);
        var $poster = $el.find('.js-poster');
        $poster.on('click', function () {
            var $youtube = $el.find('.js-youtube');
            if ($youtube.length) {
                new YT.Player($youtube.attr('id'), {
                  events: {
                    'onReady': function(event) {
                        event.target.playVideo();
                    }
                  }
                });
                setTimeout(function() {
                    $poster.hide();
                }, 250);
            }

            var $vimeo = $el.find('.js-vimeo');
            if ($vimeo.length) {
                new Vimeo.Player($vimeo[0]).play();
                $poster.hide();
            }
        })
    });
}

$(function () { initPosters() });