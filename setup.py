import re
import platform
from setuptools import setup, find_packages
import subprocess

REQUIRES = [
    "requests>=2.24.0",
    "inflection>=0.5.0",
    "pyyaml>=5.4.1",
    "jsonschema>=3.2.0",
]
REQUIRES_DEV = [
    "pytest>=5.4.3",
    "pytest-cov>=2.10.0",
    "requests-mock>=1.8.0",
    "coverage>=5.2",
    "pytest-mock>=3.6.1",
]
REQUIRES_DOCS = []

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="magellan-models",
    version="1.0.0",
    author="Talha Ahsan",
    author_email="tahsan@mmm.com",
    description="An API wrapper library that creates 'ActiveRecord' inspired models to access JSON:API compliant endpoints via OpenAPI specifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3mcloud/magellan-models",
    packages=find_packages(),
    install_requires=REQUIRES,
    extras_require={
        "dev": REQUIRES_DEV,
        "docs": REQUIRES_DOCS,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
