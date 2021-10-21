import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="djmongoauth",
    version="0.0.1",
    description="Out-of-the-box support register, sign in, email verification and password recovery workflows for websites based on Django and MongoDB",
    url="https://github.com/Haotian9850/djmongoauth",
    long_description=README,
    long_description_content_type="text/markdown",
    author="hao",
    author_email="hl7gr@virginia.edu",
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",

    ],
    packages=find_packages(exclude=["test", "djmongouser_legacy"]),
    zip_safe=False,
    install_requires=[
        "djongo==1.3.1",
        "Django>=2.2.24"
    ]
)