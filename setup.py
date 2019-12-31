from os import path
from setuptools import setup

root_dir = path.abspath(path.dirname(__file__))
with open(path.join(root_dir, 'README.rst')) as infile:
    long_description = infile.read()

setup(
    name = 'mpldatacursor',
    version = '0.7.1',
    description = "Interactive data cursors for Matplotlib",
    author = 'Joe Kington',
    author_email = 'joferkington@gmail.com',
    license = 'MIT',
    url = 'https://github.com/joferkington/mpldatacursor/',
    packages = ['mpldatacursor'],
    install_requires = [
        'matplotlib >= 0.9',
        'numpy >= 1.1'],
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
)
