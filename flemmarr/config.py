import os
from typing import Optional

from dotenv import load_dotenv

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
