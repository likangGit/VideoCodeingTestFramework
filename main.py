from modules.core import Exec
import yaml
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="config file ")
args = parser.parse_args()
with open(args.config, encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(config)
Exec(config)