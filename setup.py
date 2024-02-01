# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import find_packages, setup

PACKAGE = "xprez"
NAME = "django_xprez"
DESCRIPTION = "Django CMS for presentation websites"
AUTHOR = "Michal Májský, Martin Kappel, Jakub Dolejšek, Michal Tilsch - s-cape.cz & mimatik.com"
AUTHOR_EMAIL = "michal.majsky@s-cape.cz"
URL = "https://github.com/s-cape/django_xprez"
VERSION = "0.2.22"
LICENSE = "Mozilla Public License 2.0 (MPL 2.0)"

if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=(Path(__file__).parent / "README.md").read_text(),
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        url=URL,
        packages=find_packages(
            exclude=["tests", "tests.*", "example_app", "example_app.*"]
        ),
        include_package_data=True,
        classifiers=[
            # "Development Status :: 5 - Production/Stable",
            "Development Status :: 4 - Beta",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
        ],
        install_requires=[
            "html5lib>=1.0b3",
            "beautifulsoup4>=4.5.3",
            "Pillow>=3.0.0",
            "sorl-thumbnail",
            "django>=3.1",
        ],
        # test_suite="runtests.run_tests",
    )
