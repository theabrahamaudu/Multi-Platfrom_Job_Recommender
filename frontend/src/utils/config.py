import yaml


# load config yaml file
with open("./config/config.yaml", "r") as stream:
    config = yaml.safe_load(stream)


test_server = config["server"]["local"]
deployment_server = config["server"]["docker"]

admin_username = config["admin"]["username"]
admin_password = config["admin"]["hash"]

deployment = config["deployment"]

# server url
if deployment is True:
    server = deployment_server
else:
    server = test_server
