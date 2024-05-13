import string
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.config import Config as StarletteConfig
from starlette.datastructures import Secret
from typing import Union, Literal


class LoadEnvConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")


class AppConfigs(LoadEnvConfigs):
    # 环境变量
    app_name: str = "Awesome API"
    admin_email: str="0"
    items_per_user: int = 50


class DatabaseConfigs(LoadEnvConfigs):
    # 环境变量
    database_url_dev: str = "0"
    database_url_test: str = "0"
    database_url_preview: str = "0"
    database_url_main: str = "0"

    def get_database_url(
        self, environment: Union[Literal["dev", "preview", "test", "main"], None] = None
    ) -> str:

        db_url_env = {
            "dev": self.database_url_dev,
            # "preview": cls.database_url_dev,
            # "test": cls.database_url_dev,
            # "main": cls.database_url_dev,
        }

        if environment and environment in db_url_env:
            db_url = db_url_env[environment]
        else:
            print(f"提供的环境 '{environment}' 无效。")

        return db_url


app_configs = AppConfigs()

db_configs = DatabaseConfigs()
