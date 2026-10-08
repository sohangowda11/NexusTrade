from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True)
    cash_balance = Column(Float, default=100000.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    ticker = Column(String, nullable=False)
    shares = Column(Float, default=0)
    avg_price = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    portfolio = relationship("Portfolio", back_populates="holdings")


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)  # buy / sell
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    portfolio = relationship("Portfolio", back_populates="trades")


class AIVote(Base):
    __tablename__ = "ai_votes"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"))
    model_name = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # up / down
    confidence = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    reasoning = Column(Text)
    discussion_round = Column(Integer, default=1)
    was_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    final_direction = Column(String)
    final_confidence = Column(Float)
    final_risk = Column(String)
    consensus_score = Column(Float)
    aggregated_reasoning = Column(Text)
    price_at_analysis = Column(Float)
    price_24h_later = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    votes = relationship("AIVote", backref="session", cascade="all, delete-orphan")


class ModelPerformance(Base):
    __tablename__ = "model_performance"
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    ticker = Column(String, nullable=True)
    correct_predictions = Column(Integer, default=0)
    total_predictions = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
