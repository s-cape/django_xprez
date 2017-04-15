/**
 * Created by snakey on 04.02.16.
 */

function enableTab($scope) {
    var el = $scope.find('.js-code-snippet');
    el.keydown(function (e) {
            console.log(e);
            if (e.keyCode === 9) { // tab was pressed

                // get caret position/selection
                var val = this.value,
                    start = this.selectionStart,
                    end = this.selectionEnd;

                // set textarea value to: text before caret + tab + text after caret
                this.value = val.substring(0, start) + '\t' + val.substring(end);

                // put caret at right position again
                this.selectionStart = this.selectionEnd = start + 1;

                // prevent the focus lose
                return false;
            }

        }
    );
}

// Enable the tab character onkeypress (onkeydown) inside textarea...
// ... for a textarea that has an `id="my-textarea"`
// $(document).ready(function() {
//     enableTab();
// });

