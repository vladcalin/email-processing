import datetime

from sqlalchemy import create_engine, Column, Integer, Binary, Text, String, ForeignKey, DateTime, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/email_processing")
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class Inbox(Base):
    __tablename__ = "inbox"

    id = Column(String, unique=True, primary_key=True)

    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String)
    use_ssl = Column(Boolean, default=False)

    username = Column(Text())
    password = Column(Text())


class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(Integer, Sequence("email_messages_id_seq"), primary_key=True)
    inbox = Column(String, ForeignKey("inbox.id"))
    fetched = Column(DateTime, default=datetime.datetime.now)
    content = Column(Text)
    from_task = Column(Text, nullable=False)


class InboxProcessing(Base):
    __tablename__ = "inbox_processing"

    id = Column(Integer, Sequence("inbox_processing_id_seq"), primary_key=True)
    inbox = Column(String, ForeignKey("inbox.id"))
    started = Column(DateTime, default=datetime.datetime.now)
    finished = Column(DateTime, nullable=True)
    messages_fetched = Column(Integer, default=0)


def assure_tables():
    """
    Creates all tables if not exists
    :return:
    """
    Base.metadata.create_all()

assure_tables()
