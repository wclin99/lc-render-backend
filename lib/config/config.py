import logging
import os
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
    oss_region_endpoint: str = "0"
    oss_bucket_name: str = "0"

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




class LoggerConfig:
    def __init__(self, log_file_path="app_log.log"):
        self.log_file_path = log_file_path
        self._ensure_log_file_exists()
        self.logger = self._configure_logger()

    def _ensure_log_file_exists(self):
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w'):
                pass

    def _configure_logger(self):
        logger = logging.getLogger("progress_logger")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(self.log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def get_logger(self):
        return self.logger
    



app_configs = AppConfigs()

api_configs = ApiConfigs()

db_configs = DatabaseConfigs()

logger_config = LoggerConfig()
