var initBoxActions = function ($actionsScope) {
    $actionsScope.find('.js-grid-box-delete').click(function (e) {
        e.preventDefault()
        $(this).parent().parent('.js-box-wrapper').remove();
    });
    $actionsScope.find('.js-grid-box-move-up').click(function (e) {
        e.preventDefault()
        var $me = $(this).parent().parent('.js-box-wrapper');
        var $aboveMe = $me.prev('.js-box-wrapper');
        if ($aboveMe.length) {
            $me.after($aboveMe);
        }
    });

    $actionsScope.find('.js-grid-box-move-down').click(function (e) {
        e.preventDefault()
        var $me = $(this).parent().parent('.js-box-wrapper');
        var $belowMe = $me.next('.js-box-wrapper');
        if ($belowMe.length) {
            $me.before($belowMe);
        }
    });

};

var initAddAnotherBtn = function ($scope, contentID, boxesCount) {
    var $addAnotherBtn = $scope.find('.js-add-another');

    $addAnotherBtn.click(function (e) {
        e.preventDefault();
        var $box = $($scope.find('.js-box-tpl').html());
        $scope.find('.js-boxes').append($box);
        // initializeMediumEditors($box);
        initializeCkEditors($box);
        initBoxActions($box);
    });

    if (boxesCount === 0) {
        $addAnotherBtn.trigger('click'); // start with one box by default
    }
}

var handleFormSubmit = function ($scope, contentID) {
    $('form').submit(function (e) {
        var boxes = []
        $scope.find('.js-boxes .js-ck-editor-root').each(function (index, element) {
            boxes.push($(element)[0].ckeditorInstance.getData())
        });
        var value = JSON.stringify(boxes)
        $('#id_content-' + contentID + '-boxes').val(value)
    });
}

var initImageSizingControls = function ($scope) {
    var $input = $($scope.find('.js-image-sizing-controller').data('formfield_selector'));
    var toggleMaxWidthController = function () {
        $scope.find('.js-image-max-width-controller').toggle($input.val() === 'icon');
    }
    $input.on('change', toggleMaxWidthController);
    toggleMaxWidthController();
}

var initGridBox = function ($scope, contentID, boxesCount) {
    initBoxActions($scope.find('.js-boxes'));
    initAddAnotherBtn($scope, contentID, boxesCount);
    initImageSizingControls($scope);
    handleFormSubmit($scope, contentID);
}
