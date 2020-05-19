#!/usr/bin/python
from setuptools import find_packages, setup

setup(
    name='slippi_viz',
    version='0.2.0',
    packages=["slippi_viz"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "email-validator",
        "Flask",
        "Flask-Executor",
        "Flask-Limiter",
        "Flask-Login",
        "Flask-Migrate",
        "Flask-SQLAlchemy",
        "Flask-WTF",
    ],
)
