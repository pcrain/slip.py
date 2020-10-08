#!/usr/bin/python
from setuptools import setup
import os

#Get version from slip.py's config file
def get_version():
  with open(os.path.join("slippi_viz","app","config.py"),'r') as fin:
    for line in [f for f in fin.readlines() if "SITE_VERSION" in f]:
      return line.split('"')[1]

setup(
    name                 = 'slippi_viz',
    version              = get_version(),
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
