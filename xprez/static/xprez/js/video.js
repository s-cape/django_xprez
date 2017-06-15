


function handlePoster($contents) {
    $contents.each(function (index, el) {
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
                var player = $f($vimeo[0]);
                player.api("play");
                $poster.hide();

            }
        })

    });

}


$(function () {
    handlePoster($('.js-video-with-poster'));

});