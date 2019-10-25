#!/usr/bin/env python

from setuptools import setup, find_packages

setup(

    name = 'advanceXCMS',
    version = '1.0.0',
    author = 'Michael Leeming',
    license = 'LICENSE.txt',
    description = 'Set of tools for reviewing XCMS results and aligning matrices',

    packages = find_packages(),
    include_package_data=True,

    entry_points = {
        'gui_scripts' : ['advanceXCMS = advanceXCMS.__main__:main']
    },

    install_requires = [
        'numpy',
        'pymzml',
        'rtree',
        'pyteomics',
        'pyqtgraph'
    ],
    dependency_links = ['http://pyqt.sourceforge.net/Docs/PyQt4/installation.html'],
    zip_safe = False
)
