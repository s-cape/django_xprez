from django.shortcuts import render, get_object_or_404
from .models import Page


def page(request, slug='home'):
    page = get_object_or_404(Page, slug=slug)
    pages = Page.objects.all()
    return render(request, 'page.html', {
        'page': page,
        'pages': pages,
    })