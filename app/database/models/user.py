from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)

    refresh_token = relationship("RefreshTokenList", back_populates='user')
    products = relationship("Order", back_populates='user')

    def to_dict(self):
        return {'id': self.id,
                'username': self.username,
                'email': self.email,
                'hashed_password': self.hashed_password}
