# setup.py
from setuptools import setup, find_packages

with open('README.md', 'r', encoding="utf-8", errors='ignore') as fh:
    long_description = fh.read()

version = {}
with open("podtrader/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)

setup(
    name='podtrader',
    version=version['__version__'],
    description='PodTrader is a platform designed for developing and executing quantitative trading strategies.',
    author_email='julianwong925@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PH626/podtrader/',
    packages=find_packages(),
    install_requires=[
        'websocket-client',
        'vectorbt[full]',
    ],
)
