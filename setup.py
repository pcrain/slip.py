#!/usr/bin/python
from setuptools import setup

setup(
    name                 = 'slippi_viz',
    version              = '0.3.1',
    packages             = ["slippi_viz"],
    include_package_data = True,
    zip_safe             = False,
    install_requires     = [
        "Flask",
        "Flask-Executor",
        "Flask-Login",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "PyFladesk"
    ],
)
