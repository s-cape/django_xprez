from django.shortcuts import render

from . import css  # noqa: F401


def photoswipe(request):
    return render(request, "xprez/includes/photoswipe.html")
