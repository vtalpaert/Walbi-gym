from setuptools import setup

setup(
    name='walbi-gym',
    url='https://github.com/vtalpaert/Walbi-gym',
    version='0.1.2',
    description='Gym interface for Walbi robot',
    long_description='Walbi Gym interacts with the Walbi robot following the OpenAI gym API.',
    install_requires=[
        'pyserial',
        'enum34',
        'numpy',
        'gym',
        'pybluez',  # requires libbluetooth-dev
    ]
)
