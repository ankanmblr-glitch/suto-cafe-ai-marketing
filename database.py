"""SQLite database setup with SQLAlchemy for the PoC."""
import json
import os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from config import config


engine = create_engine(f"sqlite:///{config.DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    theme = Column(String(100))
    hero_items = Column(Text)           # JSON list
    channels = Column(Text)             # JSON list
    campaign_tone = Column(String(50))
    weather_condition = Column(String(50))
    festival_name = Column(String(100), nullable=True)
    copy_facebook = Column(Text, nullable=True)
    copy_instagram = Column(Text, nullable=True)
    copy_whatsapp = Column(Text, nullable=True)
    banner_path = Column(String(255), nullable=True)
    post_preview_path = Column(String(255), nullable=True)
    published = Column(Boolean, default=False)
    mock_reach = Column(Integer, default=0)
    mock_engagement = Column(Float, default=0.0)
    llm_source = Column(String(20), default="mock")  # "groq" or "mock"


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(50))
    status = Column(String(20))  # success | error
    duration_ms = Column(Integer)
    output_summary = Column(Text)


class DailySales(Base):
    __tablename__ = "daily_sales"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_date = Column(Date)
    footfall = Column(Integer)
    revenue_inr = Column(Float)
    top_item = Column(String(100))
    weather_condition = Column(String(50))
    had_festival = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(engine)
    _seed_sales_data()


def _seed_sales_data():
    """Seed 90 days of mock historical sales data if not present."""
    with SessionLocal() as session:
        if session.query(DailySales).count() > 0:
            return
        import random
        from datetime import timedelta
        items = ["Cold Coffee", "Suto Special Frappe", "Cappuccino",
                 "Tandoori Maggi", "Brownie Frappe", "Pizza", "Falafel Wrap"]
        for i in range(90):
            d = date.today() - timedelta(days=90 - i)
            is_weekend = d.weekday() >= 5
            base = random.randint(45, 80)
            if is_weekend:
                base = int(base * 1.4)
            footfall = random.randint(base - 10, base + 10)
            revenue = footfall * random.randint(180, 280)
            session.add(DailySales(
                sale_date=d,
                footfall=footfall,
                revenue_inr=float(revenue),
                top_item=random.choice(items),
                weather_condition=random.choice(["sunny", "cloudy", "rainy"]),
                had_festival=False
            ))
        session.commit()


def get_session() -> Session:
    return SessionLocal()
