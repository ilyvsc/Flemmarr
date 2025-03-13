import os
from typing import Optional

import yaml
from dotenv import load_dotenv
from manager import APIManager

load_dotenv()


def get_env_variable(key: str, default=None, raise_error: bool = True) -> Optional[str]:
    """Get the environment variable or return exception."""
    try:
        value = os.environ[key]
    except KeyError:
        if default is not None:
            value = default
        else:
            if raise_error:
                raise ValueError(f"Environment variable {key} is not set.")
            return None
    return value


CONFIG_PATH = get_env_variable(key="CONFIG_PATH", default="/config/flemmarr/config.yaml")


def load_configs(config_path):
    """Load configurations from a YAML file."""
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise


def main():
    configs = load_configs(CONFIG_PATH)

    print(configs)

    for key, config in configs.items():
        if key.startswith("alias_"):
            continue

        server = config.pop("server")
        address, port = server["address"], server["port"]

        api_manager = APIManager(address, port)

        print(f"Trying to connect to {key} at {address}:{port}")
        try:
            api_manager.initialize()
            print("Successfully connected!")
        except Exception as e:
            print(f"Failed to initialize connection for {key}: {e}")
            continue

        print(f"Starting to apply configuration for {key}")
        try:
            api_manager.apply(config)
            print(f"Configuration successfully applied for {key}.")
        except Exception as e:
            print(f"Failed to apply configuration for {key}: {e}")

    print("Finished applying all configurations.")


if __name__ == "__main__":
    main()
