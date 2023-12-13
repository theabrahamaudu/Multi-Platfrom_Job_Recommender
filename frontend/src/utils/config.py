"""
This module contains config variables for frontend from `./config/config.yaml`
"""

import yaml


class LoadConfig:
    def __init__(self, config_path="./config/config.yaml"):
        # load config yaml file
        with open(config_path, "r") as stream:
            self.config = yaml.safe_load(stream)

    def get_server(self):
        """
        Fetches server url from config
        """
        test_server = self.config["server"]["local"]
        deployment_server = self.config["server"]["docker"]

        deployment = self.config["deployment"]

        # server url
        if deployment is True:
            server = deployment_server
        else:
            server = test_server

        return server

    def get_admin(self):
        """
        Fetches admin username and password from config
        """
        admin_username = self.config["admin"]["username"]
        admin_password = self.config["admin"]["hash"]

        return admin_username, admin_password
