import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig()
logging.getLogger('sqlalchemy.engine.Engine.myengine').setLevel(logging.WARNING)


def get_sqlalchemy_engine(url):
    return create_engine(url, echo=False, logging_name='myengine')

def get_sqlalchemy_async_engine(url):
    return create_async_engine(url, echo=False, pool_size=10, max_overflow=5, logging_name='myengine')

def init_sqlalchemy_session(url):
    endine = get_sqlalchemy_engine(url)

    return sessionmaker(bind=endine)

def init_sqlalchemy_async_session(url):
    endine = get_sqlalchemy_async_engine(url)

    return sessionmaker(bind=endine, class_=AsyncSession, expire_on_commit=False)
