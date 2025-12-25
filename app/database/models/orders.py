from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = 'orders'

    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    items = Column(JSONB)
    total_price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates='products', foreign_keys=[user_id])

    def to_dict(self):
        return {'id': self.id,
                'user_id': self.user_id,
                'items': self.items,
                'total_price': self.total_price,
                'status': self.status.value,
                'created_at': self.created_at.isoformat()}