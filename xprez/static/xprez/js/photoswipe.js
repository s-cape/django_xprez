function openPhotoSwipe($gallery, index) {
    var pswpElement = document.querySelectorAll('.pswp')[0];
    var items = [];
    $gallery.find('.js-photo').each(function (index, el) {
        var $el = $(el);
        items.push({
            src: $el.data('original_url'),
            w: parseInt($el.data('original_width')),
            h: parseInt($el.data('original_height')),
            title: $el.data('title')
        })
    });

    // define options (if needed)
    var options = {
        // history & focus options are disabled on CodePen
        history: false,
        focus: false,
        showAnimationDuration: 0,
        hideAnimationDuration: 0,
        index: index,
        shareEl: false

    };
    var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
    gallery.init();
}

function initGallery() {
    $('body').each(function (index, el) {
        var $gallery = $(el);
        $gallery.find('.js-photo').each(function (index, el) {
            $(el).on('click', function (e) {
                openPhotoSwipe($gallery, index);
                e.preventDefault();
            });
        });

    });
}


$(function () {
    initGallery()
});