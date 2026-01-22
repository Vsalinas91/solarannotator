from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='solarannotator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.0.1',
    packages=['solarannotator'],
    url='',
    license='',
    author='J. Marcus Hughes',
    author_email='j-marcus.hughes@noaa.gov',
    description='A tool to annotate images of the Sun',
    install_requires=["PyQt5~=5.15.9",
                      "matplotlib~=3.7.2",
                      "astropy~=5.3.1",
                      "numpy~=1.23.5",
                      "goes-solar-retriever",
                      "scipy~=1.11.1",
                      "scikit-image~=0.21.0",
                      "pillow~=10.0.0",
                      "sunpy~=6.0.0",
                      "lxml~=4.9.3",
                      "reproject~=0.11.0",
                      "zeep~=4.2.1",
                      "drms~=0.6.4"],
    data_files=[('solarannotator', ['cfg/default.json'])],
    entry_points={"console_scripts": ["SolarAnnotator = solarannotator.main:main"]}

)
