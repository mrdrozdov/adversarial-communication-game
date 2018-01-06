import os

from setuptools import setup, find_packages

setup(
    name='acg',
    version='0.0.1',
    description='acg',
    classifiers=[],
    author='Andrew Drozdov',
    author_email='apd283@nyu.edu',
    url='',
    keywords='adverserial communication game',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'paste.app_factory': [
            'myapp = server:main',
        ],
        'console_scripts': []
    }
)
