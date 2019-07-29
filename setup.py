from setuptools import setup

extras = {
  'bluetooth': ['pybluez'],  # requires libbluetooth-dev
}

# Meta dependency groups.
all_deps = []
for group_name in extras:
    all_deps += extras[group_name]
extras['all'] = all_deps

setup(
    name='walbi-gym',
    url='https://github.com/vtalpaert/Walbi-gym',
    version='0.1.4',
    description='Gym interface for Walbi robot',
    long_description='Walbi Gym interacts with the Walbi robot following the OpenAI gym API.',
    install_requires=[
        'pyserial',
        'enum34',
        'numpy',
        'gym',
        'ruamel.yaml',
    ],
    extras_require=extras,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
