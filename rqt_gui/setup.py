#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

setup(
    name='rqt_gui',
    version='0.5.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=['bin/rqt'],
    install_requires=['setuptools', 'qt_gui'],
    author='Dirk Thomas',
    author_email='dthomas@osrfoundation.org',
    maintainer='Dirk Thomas',
    maintainer_email='dthomas@osrfoundation.org',
    url='https://github.com/ros2/rqt_gui',
    keywords=['ROS'],
    description='rqt_gui package',
    long_description=('rqt_gui provides the main to start an instance of the ROS integrated graphical user interface provided by qt_gui.'),
    license='Apache License, Version 2.0',
)
