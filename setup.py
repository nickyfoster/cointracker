from setuptools import find_packages
import os

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

dir_path = os.path.dirname(os.path.realpath(__file__))


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)


setup(
    name='cointracker',
    url='https://github.com/nickyfoster/cointracker.git',
    description='Cointracker',
    keywords='tracker crypto portfolio',
    packages=find_packages(exclude=['test', 'test.*']),
    package_dir={'tracker': 'tracker'},
    install_requires=[
        "python-telegram-bot==20.0a4",
        "PyYAML==6.0",
        "redis==4.3.4",
        "requests==2.28.1"
    ],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    }
)
