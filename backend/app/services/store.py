from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine("sqlite:///backend/app/data/app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Business(Base):
    __tablename__ = "business"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    entity_type = Column(String)
    vat_registered = Column(Boolean, default=False)
    periods = relationship("Period", back_populates="business")
    transactions = relationship("Txn", back_populates="business")

class Period(Base):
    __tablename__ = "period"
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    business = relationship("Business", back_populates="periods")

class Txn(Base):
    __tablename__ = "txn"
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    date = Column(Date)
    description = Column(String)
    amount = Column(Float)
    account = Column(String)
    business = relationship("Business", back_populates="transactions")

Base.metadata.create_all(engine)

class Store:
    def __init__(self):
        self.db = SessionLocal()

    def create_business(self, name: str, entity_type: str, vat_registered: bool) -> int:
        b = Business(name=name, entity_type=entity_type, vat_registered=vat_registered)
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return b.id

    def create_period(self, business_id: int, start_date: str, end_date: str) -> int:
        from datetime import datetime
        p = Period(
            business_id=business_id,
            start_date=datetime.fromisoformat(start_date).date(),
            end_date=datetime.fromisoformat(end_date).date()
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p.id

    def add_transactions(self, business_id: int, rows):
        from datetime import datetime
        count = 0
        for r in rows:
            t = Txn(
                business_id=business_id,
                date=datetime.fromisoformat(r["date"]).date(),
                description=r["description"],
                amount=r["amount"],
                account=r["account"]
            )
            self.db.add(t)
            count += 1
        self.db.commit()
        return count

    def build_context(self, business_id: int):
        b = self.db.query(Business).filter(Business.id == business_id).first()
        txns = self.db.query(Txn).filter(Txn.business_id == business_id).all()
        periods = self.db.query(Period).filter(Period.business_id == business_id).all()
        last_period = periods[-1] if periods else None
        return {
            "business": b,
            "transactions": txns,
            "period": last_period
        }
