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
    url="https://github.com/pycta2045/pycta2045",
    project_urls={
        "Bug Tracker": "https://github.com/pycta2045/pycta2045/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "pycta2045"},
    packages=setuptools.find_packages(where="pycta2045"),
    python_requires=">=3.6",
)