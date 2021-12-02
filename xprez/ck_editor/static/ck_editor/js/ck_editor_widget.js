// var jqueryCK = jQuery.noConflict(true);


function initializeCkEditors($scope) {
    var editors = [];
    $scope.find('.js-ck-editor-source').each(function(index) {
        var $textarea = $(this);
        var $editorRoot = $textarea.parent().siblings('.js-ck-editor-root');
        var $form = $editorRoot.parents('form');

        if ($textarea.data('ck-editor-variant') == 'simple') {
            console.log('TODO: ckeditor simple config')
        } else {
            var config = {
                initialData: $textarea.val(),
                // blockToolbar: ['paragraph', 'heading2', 'heading3', '|', 'blockQuote', 'bulletedList', 'numberedList', '|', 'imageUpload', 'MediaEmbed'],
                // toolbar: ['bold', 'italic', 'link', '|', 'paragraph', 'heading2', 'heading3', '|', 'blockQuote', 'bulletedList', 'numberedList', '|', 'imageUpload', 'MediaEmbed'],

                blockToolbar: ['heading', '|', 'blockQuote', 'bulletedList', 'numberedList', '|', 'imageUpload', 'MediaEmbed'],
                toolbar: ['bold', 'italic', 'link', '|', 'heading', '|', 'blockQuote', 'bulletedList', 'numberedList', '|', 'imageUpload', 'MediaEmbed'],

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
                    options: [
                        'tiny',
                        'default',
                        'big'
                    ]
                },
                image: {
                    toolbar: [ 'imageTextAlternative', 'toggleImageCaption', '|', 'imageStyle:alignLeft', 'imageStyle:block', 'imageStyle:alignRight', '|', 'linkImage' ],
                    styles: [
                        'block',
                        'alignLeft',
                        'alignRight'
                    ]
                },
                simpleUpload: {
                    uploadUrl: $textarea.data('file-upload')
                },
                placeholder: 'Type your text',
                mediaEmbed: {
                    previewsInData: true
                }
            }
        }

        BalloonBlockEditor
            .create($editorRoot[0], config)
            .then(function(editor) {
                $form.submit(function () {
                    $textarea.val(editor.getData());
                });
                editors.push(editor);
            });

        // console.log(BalloonBlockEditor.builtinPlugins.map( plugin => plugin.pluginName ));

        // $(this).parents('form').submit(function () {
        //     console.log('data');
        //     console.log(editor.getData());
        //     $textarea.val('xyz');
        //     // $textarea.val(editor.getData());
        // });
    });

    return editors;
    /*
    rangy.init();

    var SmallTextButton = MediumEditor.extensions.button.extend({
        name: 'smalltext',

        tagNames: ['small'], // nodeName which indicates the button should be 'active' when isAlreadyApplied() is called
        contentDefault: '<b>H</b>', // default innerHTML of the button
        contentFA: 'sm', // innerHTML of button when 'fontawesome' is being used
        aria: 'small', // used as both aria-label and title attributes
        action: 'small', // used as the data-action attribute of the button

        init: function () {
            MediumEditor.extensions.button.prototype.init.call(this);

            this.classApplier = rangy.createCssClassApplier('small', {
                elementTagName: 'small',
                normalize: true
            });
        },

        handleClick: function (event) {
            this.classApplier.toggleSelection();
        }
    });

    var buttonsFull = [
        'bold',
        'italic',
        'anchor',
        'h2',
        'h3',
        'quote',
        'smalltext',
        'unorderedlist',
        'orderedlist'
    ];

    var buttonsSimple = [
        'bold',
        'italic',
        'anchor',
        'h4',
        'unorderedlist'
    ];

    var editorOptionsBase = {
        buttonLabels: 'fontawesome',
        disableDoubleReturn: true,
        extensions: {
            'smalltext': new SmallTextButton()
        },
        toolbar: {
            buttons: []
        },
        anchor: {
            linkValidation: false,
            customClassOption: 'btn btn-large',
            customClassOptionText: 'Button'
        }
    };

    var editorOptionsFull = jqueryCK.extend(true, {}, editorOptionsBase);
    var editorOptionsSimple = jqueryCK.extend(true, {}, editorOptionsBase);

    editorOptionsFull.toolbar.buttons = buttonsFull;
    editorOptionsSimple.toolbar.buttons = buttonsSimple;

    $scope.find('.medium-editor-simple').each(function (index) {
        var textarea = jqueryCK(this);
        var editor1 = new MediumEditor(this, editorOptionsSimple);
        jqueryCK(this).parents('form').submit(function () {
            textarea.val(editor1.serialize()[editor1.elements[0].id].value);
        });
    });

    $scope.find('.medium-editor-no-insert-plugin').each(function (index) {
        var textarea = jqueryCK(this);
        var editor1 = new MediumEditor(this, editorOptionsFull);
        jqueryCK(this).parents('form').submit(function () {
            textarea.val(editor1.serialize()[editor1.elements[0].id].value);
        });
    });

    $scope.find('.medium-editor').each(function (index) {
        var textarea = jqueryCK(this);
        var editor = new MediumEditor(this, editorOptionsFull);
        jqueryCK($(this)).mediumInsert({
            editor: editor,
            addons: {
                images: {
                    fileUploadOptions: {
                        url: jqueryCK(this).data('file-upload')
                    },
                    deleteScript: jqueryCK(this).data('file-delete'),
                    deleteMethod: 'POST',
                    //uploadScript: jqueryCK(this).data('file-upload'),
                    autoGrid: false,
                    styles: {
                        grid: false
                    },
                    captionPlaceholder: 'image description'
                },
                embeds: {
                    captionPlaceholder: 'description',
                    oembedProxy: null
                }
                // customAddon: {}
            }
        });

        jqueryCK(this).parents('form').submit(function () {
            textarea.val(editor.serialize()[editor.elements[0].id].value);
        });
    });
    */
}


// jqueryCK(document).ready(function () {
//     initializeMediumEditors(jqueryCK('body'));
// })
// ;
