from setuptools import setup, find_packages

with open("VERSION") as f:
    version = f.read()

setup(
    name="aslflash",
    version=version,
    description="ASL Flashcard Builder",
    author="Stephen Polcyn",
    url="spyn.us",
    packages=find_packages(),
)
