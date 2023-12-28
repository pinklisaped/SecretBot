'''
Present models for db telegram bot
'''
import bot_settings
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

# Simple driver dict for short connect strings
drivers = {
    'sqlite': 'sqlite',
    'mysql': 'mysql+pymysql',
    'postgresql': 'postgresql+psycopg2',
    'oracle': 'oracle+pyodbc',
    'mssql': 'mssql+pyodbc'
}


class Base(DeclarativeBase):
    '''Parent class for orm models'''
    pass


class Secret(Base):
    '''Table secrets for send users'''
    __tablename__ = 'Secrets'
    id = Column(INTEGER(unsigned=True), primary_key=True)
    user_id_from = Column(Integer, nullable=False)
    user_id_to = Column(Integer, nullable=True)
    service_name = Column(String, nullable=False)
    service_secret = Column(String, nullable=False)
    secret_hash = Column(String, nullable=False, index=True)
    created = Column(DateTime(timezone=True), nullable=False,
                     server_default=func.now())
    expired = Column(DateTime(timezone=True), nullable=True)


class Message(Base):
    '''Table messages sent to users, needs for auto delete'''
    __tablename__ = 'Messages'
    id = Column(INTEGER(unsigned=True), primary_key=True)
    user_id_chat = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=True)
    created = Column(DateTime(timezone=True), nullable=False,
                     server_default=func.now())


# Base create db
db_uri = bot_settings.DB_URI
db_type = db_uri.split(':', 2)[0]
db_uri = db_uri.replace(db_type, drivers.get(db_type, ''), 1)
db_engine = create_engine(db_uri)
if not database_exists(db_engine.url):
    create_database(db_engine.url)

Base.metadata.create_all(bind=db_engine)
