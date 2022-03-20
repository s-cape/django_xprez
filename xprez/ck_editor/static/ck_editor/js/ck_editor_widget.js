// var jqueryCK = jQuery.noConflict(true);


function initializeCkEditors($scope) {
    $scope.find('.js-ck-editor-source').each(function(index) {
        var $textarea = $(this);
        var $editorRoot = $textarea.parent().siblings('.js-ck-editor-root');
        initializeCkEditor($textarea, $editorRoot);
    });
}


function initializeCkEditor($textarea, $editorRoot) {
    var $form = $editorRoot.parents('form');

    var config = $textarea.data('ck-editor-config');
    config.initialData = $textarea.val();

    BalloonBlockEditor
        .create($editorRoot[0], config)
        .then(function(editor) {
            $form.submit(function () {
                $textarea.val(editor.getData());
            });
            editor.keystrokes.set('Ctrl+space', function(key, stop) {
                editor.execute('input', { text: '\u00a0' } );
                stop();
            });
        });
}
