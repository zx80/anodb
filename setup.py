from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="aiodb",
    version="1.0.0",
    packages=find_packages(),
    author="Fabien Coelho",
    author_email="aio.db@coelho.net",
    url="https://github.com/zx80/aiodb",
    install_requires=["aiosql>=3.1.2"],
    description="Convenient Wrapper around AioSQL and a Database Connection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python",
        "Programming Language :: SQL",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
