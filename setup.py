#!/usr/bin/python
from setuptools import setup

setup(
    name                 = 'slippi_viz',
    version              = '0.2.0',
    packages             = ["slippi_viz"],
    include_package_data = True,
    zip_safe             = False,
    install_requires     = [
        "Flask",
        "Flask-Executor",
        "Flask-Limiter",
        "Flask-Login",
        "Flask-SQLAlchemy",
        "Flask-WTF",
    ],
)
