import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    error_messages = config["error_messages"]

print(error_messages[5])
