from setuptools import setup

setup(
    name = 'mpldatacursor',
    version = '0.2.1',
    description = "Interactive data cursors for Matplotlib",
    author = 'Joe Kington',
    author_email = 'joferkington@gmail.com',
    license = 'MIT',
    url = 'https://github.com/joferkington/mpldatacursor/',
    py_modules = ['mpldatacursor'],
    install_requires = [
        'matplotlib >= 0.9',
        'numpy >= 1.1']
)
