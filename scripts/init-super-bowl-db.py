# Database Initialization Script for Super Bowl System

import psycopg2
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, Numeric, Float
from sqlalchemy.ext.declarative import declarative_base
import os

# Get environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5433")
db_name = os.getenv("DB_NAME", "betting_markets")
db_user = os.getenv("DB_USER", "betting_user")
db_password = os.getenv("DB_PASSWORD", "betting_password")

# Connection string
database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create engine
engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=100,
    pool_timeout=30,
    pool_recycle=3600,
    echo=True  # Log SQL queries
)

# Create base class
Base = declarative_base()

# Define tables
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='func.now()')
    is_active = Column(Boolean, default=True)

class SuperBowlProp(Base):
    __tablename__ = 'super_bowl_props'
    id = Column(Integer, primary_key=True)
    kalshi_ticker = Column(String(50), nullable=False)
    market_type = Column(String(20), nullable=False)
    prop_type = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    value = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)
    probability = Column(Float, nullable=False)
    edge = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='func.now()')

class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    prop_id = Column(Integer, ForeignKey('super_bowl_props.id'), nullable=False)
    signal_type = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # "BUY", "SELL", "PASS"
    confidence = Column(String(10), nullable=False)  # "HIGH", "MEDIUM", "LOW"
    edge = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='func.now()')

class PaperTrade(Base):
    __tablename__ = 'paper_trades'
    id = Column(Integer, primary_key=True)
    prop_id = Column(Integer, ForeignKey('super_bowl_props.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('users.id'), default=1)  # Default to main user
    action = Column(String(10), nullable=False)  # "BUY", "SELL"
    amount = Column(Numeric(10,2), nullable=False)
    status = Column(String(20), nullable=False)  # "PENDING", "WON", "LOST", "VOIDED"
    is_analyzer_mode = Column(Boolean, default=True)  # Paper trading mode
    created_at = Column(DateTime(timezone=True), server_default='func.now()')

def init_db():
    """Initialize database with all tables"""
    # Create metadata
    metadata = MetaData()
    metadata.bind = engine

    # Create all tables
    Base.metadata.create_all(engine)

    print("✅ Database initialized successfully")
    print("   Tables created: users, super_bowl_props, signals, paper_trades")
    print(f"   Connection: {db_user}@{db_host}:{db_port}/{db_name}")
    print("")
    print("🎯 Super Bowl system ready!")

if __name__ == '__main__':
    init_db()
