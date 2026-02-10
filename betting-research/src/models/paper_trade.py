"""
Paper Trade Model

Stores paper trading records for testing strategies without real money.
All trades are tracked with full audit trail.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Numeric, Boolean
from sqlalchemy.sql import func
from ..models import Base


class PaperTrade(Base):
    """Paper trading record for strategy testing"""

    __tablename__ = 'paper_trades'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Row-level security
    account_id = Column(Integer, nullable=False, index=True)

    # User who initiated this trade
    user_id = Column(Integer, nullable=False, index=True)

    # Trade identification
    trade_id = Column(String(255), unique=True, nullable=False, index=True)

    # Market information
    market_type = Column(String(50), nullable=False, index=True)  # e.g., "nfl_superbowl"
    market_id = Column(String(255), nullable=False)
    market_title = Column(String(255))

    # Trade details
    action = Column(String(20), nullable=False)  # "BUY", "SELL"
    amount = Column(Numeric(10, 2), nullable=False)  # Trade amount
    contracts = Column(Integer, default=0)

    # Pricing
    price_per_contract = Column(Numeric(10, 4), nullable=False)
    total_cost = Column(Numeric(10, 2))

    # Status
    status = Column(String(20), default='PENDING', nullable=False, index=True)  # "PENDING", "FILLED", "CANCELLED"

    # Settlement (when applicable)
    settlement_price = Column(Numeric(10, 4))
    pnl = Column(Numeric(10, 2))
    settlement_at = Column(DateTime(timezone=True))

    # Metadata
    notes = Column(Text)
    is_analyzer_mode = Column(Boolean, default=False, nullable=False)  # True if paper trading

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (f"<PaperTrade(trade_id='{self.trade_id}', action='{self.action}', "
                f"amount={self.amount}, status='{self.status}')>")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'user_id': self.user_id,
            'trade_id': self.trade_id,
            'market_type': self.market_type,
            'market_id': self.market_id,
            'market_title': self.market_title,
            'action': self.action,
            'amount': float(self.amount) if self.amount else None,
            'contracts': self.contracts,
            'price_per_contract': float(self.price_per_contract) if self.price_per_contract else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'status': self.status,
            'settlement_price': float(self.settlement_price) if self.settlement_price else None,
            'pnl': float(self.pnl) if self.pnl else None,
            'settlement_at': self.settlement_at.isoformat() if self.settlement_at else None,
            'notes': self.notes,
            'is_analyzer_mode': self.is_analyzer_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
