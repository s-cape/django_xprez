function initializeCkEditors(scope) {
    scope.querySelectorAll('.js-ck-editor-source').forEach((textarea, index) => {
        var editorRoot = textarea.closest('.js-ck-editor-root');
        initializeCkEditor(textarea, editorRoot);
    });
}

function initializeCkEditor(textarea, editorRoot) {
    var form = editorRoot.closest('form');

    var config = JSON.parse(textarea.getAttribute('data-ck-editor-config'));
    config.initialData = textarea.value;

    BalloonBlockEditor
        .create(editorRoot, config)
        .then(editor => {
            form.addEventListener('submit', () => {
                textarea.value = editor.getData();
            });
            editor.keystrokes.set('Ctrl+space', (key, stop) => {
                editor.execute('input', { text: '\u00a0' });
                stop();
            });
        });
}

window.initializeCkEditors = initializeCkEditors;
window.initializeCkEditor = initializeCkEditor;
