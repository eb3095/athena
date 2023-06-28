from setuptools import setup, find_packages
from version import __version__

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="athena",
    packages=find_packages(),
    entry_points={"console_scripts": ["athena=athena_client:main"]},
    version=__version__,
    license="Reserved",
    description="A module to provide AI an AI personal assistant",
    author="eb3095",
    install_requires=required,
)
