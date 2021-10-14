from setuptools import setup, find_packages

setup(
    name="djmongouser",
    version="0.0.1",
    description="Out-of-the-box support for user register, signin, email verification and password recovery workflow for websites built with django and mongo",
    url="https://github.com/Haotian9850/dj-mongo-user",
    author="hao",
    author_email="hl7gr@virginia.edu",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "djongo==1.3.1",
        "Django>=2.2.24"
    ]
)