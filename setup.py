# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

PACKAGE = "xprez"
NAME = "django_xprez"
DESCRIPTION = "Django CMS for presentation websites"
AUTHOR = "Michal Májský, Martin Kappel, Jakub Dolejšek, Michal Tilsch - s-cape.cz & mimatik.com"
AUTHOR_EMAIL = "michal.majsky@s-cape.cz"
URL = "https://www.s-cape.cz"
VERSION = '0.1.0'
LICENSE = "Mozilla Public License 2.0 (MPL 2.0)"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(exclude=['tests', 'tests.*', 'example_app', 'example_app.*']),
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
        "django>=1.10"
    ],
    # test_suite="runtests.run_tests",
)
