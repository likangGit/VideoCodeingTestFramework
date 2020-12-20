from module.core import Exec
import yaml
with open('config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(config)
Exec(config)