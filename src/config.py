from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    debug: bool = False

    time_zone: str = 'UTC'
    use_tz: bool = True

    app_host: str = '127.0.0.1'
    app_port: int = 8000

    postgres_driver: str = 'postgresql+psycopg2'
    postgres_host: str = '127.0.0.1'
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_driver: str = 'redis'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_db: str = '0'
    redis_user: str = ''
    redis_password: str = ''

    broker_driver: str = 'amqp'
    broker_username: str
    broker_password: str
    broker_host: str = '127.0.0.1'
    broker_port: int = 5672
    broker_db: str

    wb_authorizev3: str = ''
    wb_wbx_validation_key: str = ''

    @computed_field
    @property
    def postgres_url(self) -> str:
        return URL.create(
            drivername=self.postgres_driver,
            database=self.postgres_db,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
        ).render_as_string(hide_password=False)

    @computed_field
    @property
    def redis_url(self) -> str:
        return URL.create(
            drivername=self.redis_driver,
            database=self.redis_db,
            username=self.redis_user,
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
        ).render_as_string(hide_password=False)

    @computed_field
    @property
    def broker_url(self) -> str:
        return URL.create(
            drivername=self.broker_driver,
            database=self.broker_db,
            username=self.broker_username,
            password=self.broker_password,
            host=self.broker_host,
            port=self.broker_port,
        ).render_as_string(hide_password=False)
