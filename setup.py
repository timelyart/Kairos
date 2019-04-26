"""
    Create a tag with a version number
    SCM will add 1 to the last number when using python setyp.pu sdist
    If you want to create version 1.1.5 going from version 1.1.4 create tag 1.1.4
    If you want to create version 1.2 going from version 1.1.4 create tag 1.1
    If you want to create version 2 going from version 1.1.4 create tag 1
"""
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='Kairos',
    packages=find_packages(),
    url='https://github.com/timelyart/Kairos/',
    license='GNU General Public License v3.0',
    author='timelyart',
    version='1.2.10',
    author_email='timelyart@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.',
    long_description=long_description,
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3>=1.21.1,<1.25', 'selenium', 'configparser', 'tools', 'pip>=18.1', 'Pillow', 'requests>=2.21', 'gspread', 'google-api-python-client', 'oauth2client'],
    extras_require={
        'platform_system == "Windows"': [],
        'platform_system == "Linux"': ['python3-Xlib'],
        'platform_system == "Darwin"': ['pyobjc-core', 'pyobjc']
    },
)
