from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.0.1',
    description='Attempt to quantify Duckworth Lewis Stern accuracy',
    author='Johan Coetzee',
    license='',
    install_requires=[
    'matplotlib==3.4.2',
    'pandas==1.2.4',
    'tqdm==4.60.0',
    'ruamel.yaml==0.17.4',
    ]
)
