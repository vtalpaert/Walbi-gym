from setuptools import setup, find_packages, Command
from distutils.dir_util import copy_tree
from os import getenv, walk
from pathlib import Path

extras = {
  'bluetooth': ['pybluez'],  # requires libbluetooth-dev
  'pid': ['pid_controller'],
}

# Meta dependency groups.
all_deps = []
for group_name in extras:
    all_deps += extras[group_name]
extras['all'] = all_deps


# Get Arduino libraries folder
def list_data_files():
    # for simplicity we hope for the complete env var instead of guessing paths
    ARDUINO_LIBRARIES_PATH = getenv('ARDUINO_LIBRARIES_PATH')
    data_files = []
    if ARDUINO_LIBRARIES_PATH:
        print('ARDUINO_LIBRARIES_PATH =', ARDUINO_LIBRARIES_PATH)
        libraries_dir = Path('arduino-board') / 'lib'
        for root, _, files in walk(libraries_dir):
            files = list(filter(lambda f: f != '.git', files))  # ignore .git
            if files:
                target_dir = str(Path(ARDUINO_LIBRARIES_PATH) / Path(root).relative_to(libraries_dir))  # path to Arduino libraries preserving folder hierarchy
                package_paths = [str(Path(root) / f) for f in files]  # local relative file paths
                data_files.append((target_dir, package_paths))  # The files in package_paths must go in target_dir
    return data_files

class LibrariesCopy(Command):
    description = 'Copy provided libraries to your Arduino folder'
    user_options = [
        ('arduino-library-path=', 'p', 'path to libraries folder of your Arduino installation'),
    ]

    def initialize_options(self):
        self.arduino_library_path = None
        self.target_arduino_dir = getenv('ARDUINO_LIBRARIES_PATH')

    def finalize_options(self):
        if self.arduino_library_path:
            assert Path(self.arduino_library_path).exists(), ('Path %s does not exist.' % self.arduino_library_path)
            self.target_arduino_dir = self.arduino_library_path
        if not self.target_arduino_dir:
            raise EnvironmentError('Please provide the directory for the Arduino libraries (either as option -p or in the environment variables ARDUINO_LIBRARIES_PATH)')

    def run(self):
        copy_tree(str(Path('arduino-board') / 'lib'), self.target_arduino_dir)
        print('Copied libraries to', self.target_arduino_dir)


setup(
    name='walbi-gym',
    url='https://github.com/vtalpaert/Walbi-gym',
    # TODO download_url='git+https://github.com/vtalpaert/Walbi-gym#egg=walbi-gym-dev',
    version='0.2.0',
    description='Gym interface for Walbi robot',
    long_description='Walbi Gym interacts with the Walbi robot following the OpenAI gym API.',
    install_requires=[
        'pyserial',
        'enum34',
        'numpy',
        'gym',
        'ruamel.yaml',
        'setuptools_git',
    ],
    data_files = list_data_files(),
    include_package_data=True,
    packages=find_packages(),
    # TODO zip_safe=False,  # force setuptools to install the package as a directory rather than an .egg
    extras_require=extras,
    cmdclass={
        'copy_libraries': LibrariesCopy,
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
