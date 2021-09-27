import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycta2045",
    version="0.0.1",
    author="mohamm-alsaid",
    author_email="mohamm-alsaid@gmail.com",
    description="A library for CTA2045 standard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohamm-alsaid/pycta2045",
    project_urls={
        "Bug Tracker": "https://github.com/mohamm-alsaid/pycta2045/issues",
        "Documentation": "https://github.com/mohamm-alsaid/pycta2045/tree/main/doc",
        "Examples":"https://github.com/mohamm-alsaid/pycta2045/tree/main/examples",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(exclude=['tests','doc']),
    python_requires=">=3.8",
)