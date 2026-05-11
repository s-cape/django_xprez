function initializeCkEditors(scope) {
    scope.querySelectorAll('.js-ck-editor-source').forEach((textarea, index) => {
        var editorRoot = textarea.closest('.js-ck-editor-root');
        initializeCkEditor(textarea, editorRoot);
    });
}

function getCsrfToken() {
    const cookie = document.cookie.split(';')
        .map(c => c.trim())
        .find(c => c.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

function initializeCkEditor(textarea, editorRoot) {
    var form = editorRoot.closest('form');

    var config = JSON.parse(textarea.getAttribute('data-ck-editor-config'));
    config.initialData = textarea.value;
    if (config.simpleUpload) {
        config.simpleUpload.headers = { 'X-CSRFToken': getCsrfToken() };
    }

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
