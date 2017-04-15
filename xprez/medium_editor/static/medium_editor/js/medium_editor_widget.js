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
    var editorOptions = {
        buttonLabels: 'fontawesome',
        disableDoubleReturn: true,
        extensions: {
            'smalltext': new SmallTextButton()
        },
        toolbar: {
            buttons: [
                'bold',
                'italic',
                'anchor',
                'h2',
                'h3',
                'quote',
                // {name: 'pre', action: 'append-pre', aria: 'small', tagNames: ['pre'], contentDefault: '<b>0101</b>', contentFA: 'small'},
                'smalltext',
                'unorderedlist',
                'orderedlist']
        },
        anchor: {
            linkValidation: true,
            customClassOption: 'btn btn-large',
            customClassOptionText: 'Button'
        }
    };

    $scope.find('.medium-editor-simple').each(function (index) {
        var textarea = jqueryME(this);
        var editor1 = new MediumEditor(this, editorOptions);
        jqueryME(this).parents('form').submit(function () {
            textarea.val(editor1.serialize()[editor1.elements[0].id].value);
        });
    });

    $scope.find('.medium-editor').each(function (index) {
        var textarea = jqueryME(this);
        var editor = new MediumEditor(this, editorOptions);
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