#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

setup(
    name='rqt_gui_py',
    version='0.5.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    author='Dirk Thomas',
    author_email='dthomas@osrfoundation.org',
    maintainer='Dirk Thomas',
    maintainer_email='dthomas@osrfoundation.org',
    url='https://github.com/ros2/rqt_gui_py',
    keywords=['ROS'],
    description='rqt_gui_py package',
    long_description=('rqt_gui_py enables GUI plugins to use the Python client library for ROS.'),
    license='Apache License, Version 2.0',
)
