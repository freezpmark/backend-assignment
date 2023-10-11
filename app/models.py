from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DBAccount(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)  # index=True
    name = Column(String)
    email = Column(String)
    _balance = Column(Integer)
    withdrawed = Column(Integer)
    withdraw_notify_limit = Column(Integer)

    bank_id = Column(Integer, ForeignKey("banks.id"))

    bank = relationship("DBBank", back_populates="accounts")
    cards = relationship("DBCard", back_populates="account")


class DBCard(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer)
    card_num = Column(String)

    account_id = Column(Integer, ForeignKey("accounts.id"))

    account = relationship("DBAccount", back_populates="cards")


class DBBank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    accounts = relationship("DBAccount", back_populates="bank")
