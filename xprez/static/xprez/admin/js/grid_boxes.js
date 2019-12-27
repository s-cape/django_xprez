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
        $scope.find('.js-boxes').append($scope.find('.js-box-tpl').html())
        initializeMediumEditors(jqueryME('.js-content-' + contentID + ' .js-boxes:last'));
        initBoxActions($scope.find('.js-boxes:last'));
    });

    if (boxesCount === 0) {
        $addAnotherBtn.trigger('click'); // start with one box by default
    }
}

var handleFormSubmit = function ($scope, contentID) {
    $('form').submit(function (e) {
        var boxes = []
        $scope.find('.js-boxes textarea.js-grid-box').each(function (index, element) {
            boxes.push($(element).val())
        })
        var value = JSON.stringify(boxes)
        $('#id_content-' + contentID + '-boxes').val(value)
    })
}


var initGridBox = function ($scope, contentID, boxesCount) {
    initBoxActions($scope.find('.js-boxes'));
    initAddAnotherBtn($scope, contentID, boxesCount);
    handleFormSubmit($scope, contentID);
}