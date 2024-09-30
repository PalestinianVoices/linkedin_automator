# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def read_requirements(name):
    """Read requirements from requirements.txt."""
    with open(path.join(HERE, name), encoding='utf-8') as f:
        requirements = f.read().splitlines()
    return requirements

# This call to setup() does all the work
setup(
    name="linkedin_automator",
    version="0.2.0",
    description="A Python library to automate various operations on LinkedIn posts, comments, and replies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PalestinianVoices/linkedin_automator",
    author="Hala H. & Essam W.",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["linkedin_automator"],
    include_package_data=True,
    install_requires=read_requirements('./requirements.txt'),
)

# update:
# pip install wheel
# pip install twine
# python setup.py sdist bdist_wheel     
# twine check dist/*
# twine upload dist/*