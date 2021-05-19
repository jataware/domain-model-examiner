from setuptools import find_packages, setup 

def read_requirements(path: str):
    with open(path) as f:
        return f.read().splitlines()

with open("README.md") as readme_file:
    readme = readme_file.read()

install_requirements = read_requirements("requirements.txt")

setup(
    author="Robnet Kerns",
    author_email="brobnet@jataware.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description="A library to perform machine reading over a model codebase in order to automatically extract key metadata.",
    install_requires=install_requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="dmx",
    name="dmx",
    packages=find_packages(include=["dmx", "dmx.*"]),
    test_suite="tests",
    url="https://github.com/jataware/domain-model-examiner",
    version='0.0.1',
    zip_safe=False,




)