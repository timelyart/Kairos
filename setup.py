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
    author_email='timelyart@protonmail.com',
    description='Kairos aims to help you save time by automating repetitive tasks on TradingView such as refreshing alerts and creating new ones.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['pyyaml', 'beautifulsoup4', 'urllib3', 'selenium', 'configparser', 'tools'],
)
