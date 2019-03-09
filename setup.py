from setuptools import setup, find_packages
from pkg_resources import get_distribution
from os import path

release = get_distribution('kairos').version
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='Kairos',
    packages=find_packages(),
    license='End-User License Agreement: https://eulatemplate.com/live.php?token=F2am7Ud98HlFDECoTq2GYhIksQmn6T9A',
    author='Sanne Appel',
    version=release,
    author_email='sjappel@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.',
    long_description=long_description,
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3', 'selenium', 'configparser', 'tools', 'pip>=18.1', 'Pillow', 'requests>=2.21', 'gspread', 'google-api-python-client', 'oauth2client', 'pymongo', 'dill'],
    extras_require={
        'platform_system == "Windows"': [],
        'platform_system == "Linux"': ['python3-Xlib'],
        'platform_system == "Darwin"': ['pyobjc-core', 'pyobjc']
    },
)
