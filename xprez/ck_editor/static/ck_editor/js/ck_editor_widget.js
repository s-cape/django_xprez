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

    if ($textarea.data('ck-editor-variant') == 'simple') {
        var config = {
            initialData: $textarea.val(),
            toolbar: ['bold', 'italic', 'link'],
            blockToolbar: [],
        }
    } else {
        var config = {
            initialData: $textarea.val(),

            blockToolbar: ['heading', '|', 'blockQuote', 'bulletedList', 'numberedList'],
            toolbar: ['bold', 'italic', 'link', '|', 'heading', '|', 'blockQuote', 'bulletedList', 'numberedList'],

            placeholder: 'Type your text',
            link: {
                decorators: {
                    toggleButtonPrimary: {
                        mode: 'manual',
                        label: 'Primary button',
                        attributes: {
                            class: 'btn btn-primary'
                        }
                    },
                    toggleButtonSecondary: {
                        mode: 'manual',
                        label: 'Secondary button',
                        attributes: {
                            class: 'btn btn-secondary'
                        }
                    },
                    openInNewTab: {
                        mode: 'manual',
                        label: 'Open in a new tab',
                        defaultValue: false,
                        attributes: {
                            target: '_blank',
                        }
                    }
                }
            },
            heading: {
                options: [
                    { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                    { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                    { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
                ]
            },
            fontSize: {
                options: ['tiny', 'default', 'big']
            },
        }

        if ($textarea.data('ck-editor-variant') == 'full_no_insert_plugin') {
            config.image = {
                toolbar: ['|']
            }
        } else if ($textarea.data('ck-editor-variant') == 'full') {
            config.blockToolbar.push('|', 'imageUpload', 'MediaEmbed');
            config.toolbar.push('|', 'imageUpload', 'MediaEmbed');
            config.simpleUpload = { uploadUrl: $textarea.data('file-upload') }
            config.mediaEmbed = { previewsInData: true }
            config.image = {
                toolbar: [ 'imageTextAlternative', 'toggleImageCaption', '|', 'imageStyle:alignLeft', 'imageStyle:block', 'imageStyle:alignRight', '|', 'linkImage' ],
                styles: [
                    'block',
                    'alignLeft',
                    'alignRight'
                ]
            }
        }
    } 

    BalloonBlockEditor
        .create($editorRoot[0], config)
        .then(function(editor) {
            $form.submit(function () {
                $textarea.val(editor.getData());
            });
        });
}
