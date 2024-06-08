import string
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.config import Config as StarletteConfig
from starlette.datastructures import Secret
from typing import Union, Literal
from lib.model import Environments


class LoadEnvConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../../.env")


class AppConfigs(LoadEnvConfigs):
    # 环境变量
    app_name: str = "Awesome API"
    admin_email: str="0"
    items_per_user: int = 50


class ApiConfigs(LoadEnvConfigs):
    dashscope_api_key: str = "0"
    pinecone_api_key: str = "0"

class DatabaseConfigs(LoadEnvConfigs):
    # 环境变量
    database_url_dev: str = "0"
    database_url_testing: str = "0"
    database_url_preview: str = "0"
    database_url_main: str = "0"

    def get_database_url(
        self, environment: Union[Environments, None] = None
    ) -> str:

        db_url_env = {
            Environments.dev: self.database_url_dev,
            # "preview": cls.database_url_dev,
            Environments.test: self.database_url_testing,
            Environments.main: self.database_url_main,
        }

        if environment and environment in db_url_env:
            db_url = db_url_env[environment]
        else:
            print(f"提供的环境 '{environment}' 无效。")

        return db_url


app_configs = AppConfigs()

api_configs = ApiConfigs()

db_configs = DatabaseConfigs()

