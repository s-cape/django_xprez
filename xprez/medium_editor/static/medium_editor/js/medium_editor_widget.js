var jqueryME = jQuery.noConflict(true);


function initializeMediumEditors($scope) {
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

    var editorOptionsFull = jqueryME.extend(true, {}, editorOptionsBase);
    var editorOptionsSimple = jqueryME.extend(true, {}, editorOptionsBase);

    editorOptionsFull.toolbar.buttons = buttonsFull;
    editorOptionsSimple.toolbar.buttons = buttonsSimple;

    $scope.find('.medium-editor-simple').each(function (index) {
        var textarea = jqueryME(this);
        var editor1 = new MediumEditor(this, editorOptionsSimple);
        jqueryME(this).parents('form').submit(function () {
            textarea.val(editor1.serialize()[editor1.elements[0].id].value);
        });
    });

    $scope.find('.medium-editor-no-insert-plugin').each(function (index) {
        var textarea = jqueryME(this);
        var editor1 = new MediumEditor(this, editorOptionsFull);
        jqueryME(this).parents('form').submit(function () {
            textarea.val(editor1.serialize()[editor1.elements[0].id].value);
        });
    });

    $scope.find('.medium-editor').each(function (index) {
        var textarea = jqueryME(this);
        var editor = new MediumEditor(this, editorOptionsFull);
        jqueryME($(this)).mediumInsert({
            editor: editor,
            addons: {
                images: {
                    fileUploadOptions: {
                        url: jqueryME(this).data('file-upload')
                    },
                    deleteScript: jqueryME(this).data('file-delete'),
                    deleteMethod: 'POST',
                    //uploadScript: jqueryME(this).data('file-upload'),
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

        jqueryME(this).parents('form').submit(function () {
            textarea.val(editor.serialize()[editor.elements[0].id].value);
        });
    });

}


// jqueryME(document).ready(function () {
//     initializeMediumEditors(jqueryME('body'));
// })
// ;
