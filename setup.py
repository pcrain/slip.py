#!/usr/bin/python
from setuptools import find_packages, setup

setup(
    name='slippi_viz',
    version='0.2.0',
    packages=["slippi_viz"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask_executor',
        'flask_login',
        'flask_migrate',
        'flask_sqlalchemy',
        'flask_wtf',
    ],
)