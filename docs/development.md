Development
===========

Setup
-----

To set up automated black formatting connected to git commits:

- Install [pre-commit](https://pre-commit.com/#installation)
- Run `pre-commit install`

Rebuilding CKEditor
-------------------

    cd xprez/ck_editor/assets/ckeditor5
    npm install
    npm run build

Rebuilding CSS styles
---------------------

    cd xprez/static/xprez
    npm install
    npm run build

Use `npm run watch` when actively developing.

Releasing
---------

Releases are published via GitHub Actions:
https://github.com/s-cape/django_xprez/actions/workflows/release.yml
