from django.test import TestCase, override_settings

from xprez.admin import XprezAdminMixin


class DummyAdmin(XprezAdminMixin):
    def xprez_allowed_modules(self, container=None):
        return [
            "xprez.VideoModule",
            "xprez.TextModule",
            "xprez.GalleryModule",
        ]


class XprezAddMenuModulesTest(TestCase):
    def test_follows_allowed_modules_order_when_add_menu_not_configured(self):
        admin = DummyAdmin()
        self.assertEqual(
            admin.xprez_add_menu_modules(),
            [
                "xprez.VideoModule",
                "xprez.TextModule",
                "xprez.GalleryModule",
            ],
        )

    @override_settings(
        XPREZ_MODULES_ADD_MENU=[
            "xprez.TextModule",
            "xprez.VideoModule",
            "xprez.GalleryModule",
        ],
    )
    def test_uses_explicit_add_menu_order_when_configured(self):
        admin = DummyAdmin()
        self.assertEqual(
            admin.xprez_add_menu_modules(),
            [
                "xprez.TextModule",
                "xprez.VideoModule",
                "xprez.GalleryModule",
            ],
        )

    @override_settings(
        XPREZ_MODULES_ADD_MENU=["xprez.TextModule", "xprez.MissingModule"],
    )
    def test_explicit_add_menu_filters_by_allowed(self):
        admin = DummyAdmin()
        self.assertEqual(
            admin.xprez_add_menu_modules(),
            ["xprez.TextModule"],
        )
