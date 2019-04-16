from setuptools import setup

setup(
    name='walby-gym',
    version='0.0.1',
    packages=['walby_gym'],
    install_requires=[
        'pyserial',
        'enum34',
        'numpy',
        'gym',
    ]
)