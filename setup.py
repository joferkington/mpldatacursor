from setuptools import setup

setup(
    name = 'mpldatacursor',
    version = '0.7.0',
    description = "Interactive data cursors for Matplotlib",
    author = 'Joe Kington',
    author_email = 'joferkington@gmail.com',
    license = 'MIT',
    url = 'https://github.com/joferkington/mpldatacursor/',
    packages = ['mpldatacursor'],
    install_requires = [
        'matplotlib >= 0.9',
        'numpy >= 1.1']
)
