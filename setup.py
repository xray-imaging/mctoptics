from setuptools import setup, find_packages

setup(
    name='mctoptics',
    version=open('VERSION').read().strip(),
    author='Viktor Nikitin, Francesco De Carlo',
    url='https://github.com/xray-imaging/mctoptics',
    packages=find_packages(),
    include_package_data = True,
    description='Module to control MicroCT optics at beamline 2-BM',
    zip_safe=False,
)