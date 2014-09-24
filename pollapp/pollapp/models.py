import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Text,
    TIMESTAMP,
    )
from sqlalchemy.ext.declarative import (
    declared_attr,
    declarative_base
    )
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension

class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(cls=Base)

class Poll(Base):
    name = Column(Text)
    created_on = Column(TIMESTAMP(timezone=False))

    def __init__(self, **kwargs):
        self.created_on = datetime.datetime.utcnow()
        super(Poll, self).__init__(**kwargs)

class Choice(Base):
    text = Column(Text)
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship("Poll", backref=backref("choices",
        lazy="dynamic"))

class Response(Base):
    ip_address = Column(Text)
    voted_on = Column(TIMESTAMP(timezone=False))
    choice_id = Column(Integer, ForeignKey("choice.id"))
    choice = relationship("Choice", backref=backref("choice",
        lazy="dynamic"))

    def __init__(self, **kwargs):
        self.voted_on = datetime.datetime.utcnow()
        super(Response, self).__init__(**kwargs)

#Index('my_index', MyModel.name, unique=True, mysql_length=255)
