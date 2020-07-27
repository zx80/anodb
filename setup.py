from setuptools import setup, find_packages
setup(
    name="anodb",
    version="1.0.0",
    packages=find_packages(),
    author="Fabien Coelho",
    author_email="ano.db@coelho.net",
    url="https://github.com/zx80/anodb",
    install_requires=["anosql>=1.0.0"],
    description="Convenient Wrapper around AnoSQL and a Database Connection"
)
