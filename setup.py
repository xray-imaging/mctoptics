from setuptools import setup, find_packages

setup(
    name='mctoptics',
    version=open('VERSION').read().strip(),
    author='Viktor Nikitin, Francesco De Carlo',
    url='https://github.com/nikitinvv/mctoptics',
    packages=find_packages(),
    include_package_data = True,
    description='Module to control TXM optics at sector 32id',
    zip_safe=False,
)