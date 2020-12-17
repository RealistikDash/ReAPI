# This file is going to be ugly but its not going to be used frequently so no point giving it proper structure
from setuptools import setup

# Read packages.
packages = []
with open("requirements.txt") as f:
    # Split by new lines.
    f_split = f.read().split("\n")
    # Remove empty nl.
    f_split.remove("")
    # Remove comments.
    for i in f_split:
        if i[0] == "#":
            f_split.remove(i)
        
    # Set packages from file.
    packages = f_split

# Read the readme.
with open("README.md") as f:
    readme_text = f.read()


setup(
    name= "ReAPI",
    version= "0.0.2",
    py_modules= ["reapi", "objects", "exceptions"],
    description= "A simple yet powerful API creation library.",
    package_dir= {"": "reapi"},
    classifiers= [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Framework :: AsyncIO",
        "Development Status :: 3 - Alpha",
        "Topic :: Database"
        
    ],
    author= "RealistikDash",
    license="MIT",
    python_requires=">=3.7",
    install_requires= packages,
    url= "https://github.com/RealistikDash/ReAPI",
    project_urls= {
        "GitHub: repo": "https://github.com/RealistikDash/ReAPI",
        "GitHub: issues": "https://github.com/RealistikDash/ReAPI/issues"
    },
    long_description_content_type= "text/markdown",
    long_description= readme_text
)
