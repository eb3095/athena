from setuptools import setup, find_packages
from version import __version__

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="athena-server",
    packages=find_packages(),
    entry_points={"console_scripts": ["athena-server=athena_server:main"]},
    version=__version__,
    license="Reserved",
    description="A module to provide AI services for Athena",
    author="eb3095",
    install_requires=required,
)
