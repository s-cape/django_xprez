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

var handleFormSubmit = function ($scope, contentID, editors) {
    $('form').submit(function (e) {
        var boxes = []
        for (var ii=0; ii<editors.length; ii++) {
            boxes.push(editors[ii].getData());
        }

        var value = JSON.stringify(boxes);
        $('#id_content-' + contentID + '-boxes').val(value);
    })
}


var initGridBox = function ($scope, contentID, boxesCount, editors) {
    initBoxActions($scope.find('.js-boxes'));
    initAddAnotherBtn($scope, contentID, boxesCount);
    handleFormSubmit($scope, contentID, editors);
}
