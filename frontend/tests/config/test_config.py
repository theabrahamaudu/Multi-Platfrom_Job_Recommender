from src.utils.config import LoadConfig


def test_server_config_local():
    config = LoadConfig(
        config_path="./tests/test_files/test_local_config.yaml"
    )
    assert config.get_server() == "http://localhost:28000"
    assert config.get_admin() == (
        "admin",
        "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")


def test_server_config_docker():
    config = LoadConfig(
        config_path="./tests/test_files/test_docker_config.yaml"
    )
    assert config.get_server() == "http://backend:28000"
    assert config.get_admin() == (
        "admin",
        "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")
