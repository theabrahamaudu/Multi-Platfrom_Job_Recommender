import yaml


# load config yaml file
with open("./config/config.yaml", "r") as stream:
    config = yaml.safe_load(stream)


test_server = config["server"]["test"]
deployment_server = config["server"]["deployment"]
