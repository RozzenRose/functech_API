from app.database.engine import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class RefreshTokenList(Base):
    __tablename__ = 'refresh_token_list'

    owner_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False, unique=True)
    refresh_token = Column(String, nullable=False)

    user = relationship("User", back_populates='refresh_token', foreign_keys=[owner_id])


    def to_dict(self):
        return {'owner_id': self.owner_id,
                'refresh_token': self.refresh_token}
