function getCookie(name) {
    var cookie, cookieValue, cookies, i;
    cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        cookies = document.cookie.split(';');
        i = 0;
        while (i < cookies.length) {
            cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
            i++;
        }
    }
    return cookieValue;
}

function activateDropzone($scope, formset_prefix) {
    $scope.find('.js-dropzone').each(function (index, element) {
        var $el = $(element);
        var content_pk = $el.data('content_pk');
        var $content = $('.js-content-' + content_pk);
        var $dropzone = $el.dropzone({
            url: $el.data('uploadurl'),
            parallelUploads: 1,
            uploadMultiple: false,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        var dropzone = $dropzone[0].dropzone;
        dropzone.on("success", function (file, response) {
            var $formset = $content.find('.js-item-formset');
            var $photoContainer = $content.find('.js-item-container');
            this.removeFile(file);


            $photoContainer.append(response.template);
            $formset.append(response.form);
            activateFormfieldControllers($photoContainer.find('.js-item:last-child'));
            var $totalForms = $('#id_'+formset_prefix+'-' + + content_pk + '-TOTAL_FORMS');
            var $initialForms = $('#id_'+formset_prefix+'-' + + content_pk + '-INITIAL_FORMS');
            $totalForms.val(parseInt($totalForms.val()) + 1);
            $initialForms.val(parseInt($initialForms.val()) + 1);
        });
    })
}


function activateItemSorting($scope, formset_prefix) {
    var $itemContainer = $scope.find('.js-item-container');
    $itemContainer.sortable({
            handle: $itemContainer.find('.js-item-handle').length ? '.js-item-handle' : null,
            update: function (event, ui) {
                $itemContainer.find('.js-item').each(function (index, el) {
                    var $el = $(el);
                    $('#id_'+formset_prefix+'-' + $itemContainer.data('content_pk') + '-' + $el.data('number') + '-position').val(index);
                });
            }
        }
    );
}


function activateAjaxUploadFormset($scope, formset_prefix) {
    activateDropzone($scope, formset_prefix);
    activateItemSorting($scope, formset_prefix);
}


// $(function() {
//    activateDropzone()
// });
