from setuptools import setup, find_packages

with open("VERSION") as f:
    version = float(f.read())

setup(
    name="aslflash",
    version=str(version),
    description="ASL Flashcard Builder",
    author="Stephen Polcyn",
    url="spyn.us",
    packages=find_packages()
)
