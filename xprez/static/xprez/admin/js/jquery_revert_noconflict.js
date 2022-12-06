/* use django.jQuery as global $/jQuery */

window.$ = django.jQuery || $ || jQuery;
window.jQuery = window.$;