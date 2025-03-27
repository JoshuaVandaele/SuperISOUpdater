"""Based off of pypa/sampleproject
https://raw.githubusercontent.com/pypa/sampleproject/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py
"""

import pathlib

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="sisou",  # Required
    version="1.4.1",  # Required
    description="A powerful tool to conveniently update all of your ISO files!",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/JoshuaVandaele/SuperISOUpdater",  # Optional
    author="Joshua Vandaele",  # Optional
    author_email="joshua@vandaele.software",  # Optional
    classifiers=[  # Optional
        # https://pypi.org/classifiers/
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="ventoy, updater, os, iso, updater, sisou, cli",  # Optional
    packages=find_packages(),  # Required
    py_modules=["sisou"],  # Required
    include_package_data=True,
    package_data={"": ["config.toml.default"]},
    python_requires=">=3.10, <4",
    install_requires=[
        "beautifulsoup4==4.12.2",
        "requests==2.31.0",
        "tqdm==4.65.0",
        "PGPy13==0.6.1rc1",
    ],  # Optional
    # extras_require={
    #     "dev": [""],
    #     "test": [""],
    # },
    entry_points={  # Optional
        "console_scripts": [
            "sisou = sisou:main",
        ],
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/JoshuaVandaele/SuperISOUpdater/issues",
        "Source": "https://github.com/JoshuaVandaele/SuperISOUpdater/",
    },
    zip_safe=False,
)
