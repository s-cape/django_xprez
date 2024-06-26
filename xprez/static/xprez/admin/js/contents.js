function activateAddContentLinks($scope) {
    var $contentsContainer = $('.js-xprez-contents-container');
    $scope.find('.js-add-content, .js-copy-content').each(function (index, el) {
        var $el = $(el);
        $el.click(function () {
            $.get($el.data('url'), function (data) {
                var insertBefore = $el.data('insert-before');
                if (insertBefore) {
                    $(data.template).insertBefore($(insertBefore))
                } else if ($el.hasClass('js-copy-content')) {
                    $(data.template).insertAfter($el.closest('.js-content'));
                } else {
                    $contentsContainer.append(data.template);
                }

                var $content = $('.js-content-' + data.content_pk);
                activateContent($content);
                updateContentPositions(data);
            });
        });
    });
}

function updateContentPositions(data) {
    var $contentsContainer = $('.js-xprez-contents-container');
    if (data.updated_content_positions) {
        for (id in data.updated_content_positions) {
            $contentsContainer.find('#id_content-'+id+'-position').val(data.updated_content_positions[id]);
        }
    }
}

function activateContent($content) {
    activateAddContentLinks($content);
    activateFormfieldControllers($content);
    activateCollapsers($content);
    activateCommonOptions($content);
    activateSubmenus($content);
    activateClipboardContent($content);
}

function activateCheckboxControllers($scope) {
    $scope.find('.js-checkbox_controller').each(function (index, el) {
        var $el = $(el);
        var $checkbox = $($el.data('formfield_selector'));
        if ($checkbox.is(':checked')) {
            $el.addClass('active');
            $el.trigger('activated');
        }
        else {
            $el.trigger('deactivated');
        }
        $el.click(function () {
            if ($checkbox.is(':checked')) {
                $checkbox.prop('checked', false);
                $el.removeClass('active');
                $el.trigger('deactivated');
            }
            else {
                $checkbox.prop('checked', true);
                $el.addClass('active');
                $el.trigger('activated');

            }
        });
    });
}

function activateSelectControllers($scope) {
    $scope.find('.js-select_controller').each(function (index, el) {
        var $el = $(el);
        var $options = $el.find('.js-option');
        var $formField = $($el.data('formfield_selector'));
        $el.find('.js-option[data-formfield_value="' + $formField.val() + '"]').addClass('active');
        $options.click(function () {
            var $this = $(this);
            $options.removeClass('active');
            $this.addClass('active');
            $formField.val($this.data('formfield_value'));
            $formField.trigger('change');
        });
    });
}

function activateMultipleSelectControllers($scope) {
    $scope.find('.js-multiple_select_controller').each(function (index, el) {
        var $el = $(el);
        var $options = $el.find('.js-option');
        var $formField = $($el.data('formfield_selector'));
        var values = $formField.val();
        if (values) {
            for (var i=0; i < values.length; i++) {
                $el.find('.js-option[data-formfield_value="' + values[i] + '"]').addClass('active');
            }
        }
        $options.click(function () {
            var $this = $(this);
            var val = $this.data('formfield_value').toString();
            var values = $formField.val();
            if (values === null) {
                values = [];
            }
            if ($this.hasClass('active')) {
                $this.removeClass('active');
                var index = values.indexOf(val);
                values.splice(index, 1);
            }
            else {
                $this.addClass('active');
                values.push(val);
            }
            $formField.val(values);
            $formField.trigger('change');
        });

    });
}

function activateCollapsers($scope) {
    $scope.find('.js-collapser').each(function (index, el) {
        var $collapsible = $(this).parent().parent('.xprez-module');
        $(this).click(function () {
            $collapsible.toggleClass('collapsed')
        });

    });
}

function activateCommonOptions($scope) {
    $scope.find('.js-common-options-toggle').each(function (index, el) {
        var $toggle = $(this);
        var $commonOptions = $toggle.closest('.js-content').find('.js-common-options');

        function setVisibility() {
            var active = $toggle.hasClass('active');
            $commonOptions.toggle(active);

            if (active) {
                $toggle.parent().parent('.xprez-module').removeClass('collapsed');
            }
        }

        setVisibility();

        $toggle.click(function() {
            $toggle.toggleClass('active');
            setVisibility();
        });
    });
}

function activateTextControllers($scope) {
    $scope.find('.js-text_controller').each(function (index, el) {
        var $el = $(el);
        var $formField = $($el.data('formfield_selector'));
        $el.val($formField.val());
        $el.on("change paste keyup", function () {
            $formField.val($el.val());
        })
    });
}


function activateDeleteButtons($scope) {
    $scope.find('.js-delete-content').each(function (index, el) {
        var $el = $(el);
        var url = $el.data('url');
        $el.on('click', function () {
            if (confirm("Are you sure you wish to delete this block?")) {
                $.post(url);
                $('.js-content-' + $el.data('pk')).remove();
            }
        });

    })
}

function activateFormfieldControllers($scope) {
    activateCheckboxControllers($scope);
    activateSelectControllers($scope);
    activateMultipleSelectControllers($scope);
    activateTextControllers($scope);
    activateDeleteButtons($scope);
}

function activateSubmenus($scope) {
    $scope.find('.js-xprez-submenu-toggle').click(function(e) {
        e.stopPropagation();
        $(this).toggleClass('active');
    });
}

function activateClipboardCopyLink($el) {
    $el.click(function(e) {
        if ($el.closest('.js-xprez-submenu-toggle.active').length) {
            e.stopPropagation();
        }

        $el.removeClass('success');
        $.post($el.data('url'), function() {
            $el.addClass('success');
            setTimeout(function() {
                $el.closest('.js-xprez-submenu-toggle.active').removeClass('active');
            }, 1000);
            $('.js-xprez-clipboard-list-trigger').show();
            removeClipboardLists();
        });
    });
}

function loadClipboardList($trigger) {
    removeClipboardLists();

    var $contentsContainer = $('.js-xprez-contents-container');
    var $content = $trigger.closest('.js-content');

    $.get($trigger.data('url'), function(data) {
        $clipboardList = $(data);

        if ($content.length) {
            $clipboardList.insertBefore($content);
        } else {
            $contentsContainer.append($clipboardList);
        }

        $clipboardList.find('.js-clipboard-paste').click(function(e) {
            e.stopPropagation();
            var $pasteEl = $(this);
            $.post($pasteEl.data('url'), function(data) {
                for (const contentData of data.contents) {
                    $(contentData.template).insertBefore($clipboardList);
                    var $content = $('.js-content-' + contentData.content_pk);
                    activateContent($content);
                }
                updateContentPositions(data);
                removeClipboardLists();
            });
        });
    });
}

function removeClipboardLists() { $('.js-xprez-clipboard-list').remove(); }


function activateClipboardContent($scope) {
    $scope.find('.js-clipboard-copy').each(function() {
        activateClipboardCopyLink($(this))
    });

    $scope.find('.js-xprez-clipboard-list-trigger').click(function(e) {
        loadClipboardList($(this));
    });
}

function activateClipboardGlobal() {
    activateClipboardCopyLink($('.js-xprez-clipboard-copy-all'));
    activateClipboardContent($('.js-xprez-add'));

    $(document)
        .click(removeClipboardLists)
        .click(function() { $('.js-xprez-submenu-toggle.active').removeClass('active'); });
}

$(function () {
    var $xprez = $('.js-xprez');
    var $container = $('.js-xprez-contents-container');
    activateAddContentLinks($('.js-xprez-add,.js-xprez-contents-container'));
    activateFormfieldControllers($container);
    activateCollapsers($container);
    activateCommonOptions($container);
    activateSubmenus($container);

    activateClipboardGlobal();
    activateClipboardContent($container);
    // hideErrorsForDeletedContents();

    $container.sortable({
        'handle': '.js-sortable-handler',
        update: function (event, ui) {
            $('.js-content').each(function (index, el) {
                var $el = $(el);
                var $positionForm = $('#id_content-' + $el.data('pk') + '-position');
                $positionForm.val(index);
            });
        }

    });

    $('.js-collapse_all').click(function () {
        $('.xprez-module').addClass('collapsed');
    });
});
