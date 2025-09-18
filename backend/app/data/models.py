from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.data.database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    entity_type = Column(String)
    vat_registered = Column(String)

    periods = relationship("Period", back_populates="business")
    transactions = relationship("Transaction", back_populates="business")


class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(String)
    end_date = Column(String)
    business_id = Column(Integer, ForeignKey("businesses.id"))

    business = relationship("Business", back_populates="periods")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    description = Column(String)
    amount = Column(Float)
    category = Column(String)
    business_id = Column(Integer, ForeignKey("businesses.id"))

    business = relationship("Business", back_populates="transactions")