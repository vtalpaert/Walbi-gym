import os.path

from ruamel.yaml import YAML
yaml = YAML()   # typ='safe', if not specfied, is 'rt' (round-trip)

config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')

def read_config(filepath):
    with open(filepath) as f:
        return yaml.load(f)

config = read_config(config_file)


if __name__ == '__main__':
    from pprint import pprint
    pprint(config)
