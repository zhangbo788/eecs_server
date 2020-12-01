import os
import sys

import yaml


class ImproperlyConfigured(Exception):
    """Server is somehow improperly configured"""

    pass


CONFIG_PATH = "/opt/web/eecs_config.yaml"
# 从配置文件更新
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config_dict = yaml.load(f.read(), Loader=yaml.FullLoader)
else:
    sys.stderr.write(f"请确认配置文件{CONFIG_PATH}是否存在!! 配置文件信息请见 README.MD#Configuration\n")


def _get_config(field, default=None):
    if field in config_dict.keys():
        return config_dict[field]
    else:
        if default is None:
            raise ImproperlyConfigured(f"缺失必须的配置信息 {field}")
        else:
            sys.stderr.write(f"缺失配置信息{field}，现使用默认值{default}.\n")
            return default


# ALLOWED_HOSTS = _get_config("ALLOWED_HOSTS", ["*"])
# database
POSTGRES_HOST = _get_config("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = _get_config("POSTGRES_PORT", 5432)
POSTGRES_DATABASE = _get_config("POSTGRES_DATABASE", "eecs")
POSTGRES_USERNAME = _get_config("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = _get_config("POSTGRES_PASSWORD", "eecs123456")
POSTGRES_URI = f"postgres://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PASSWORD}/{POSTGRES_DATABASE}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["database.ps.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

