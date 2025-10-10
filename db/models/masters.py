from db.base import Base
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index, event
from sqlalchemy.orm import relationship
from urllib.parse import urljoin

def now_utc():
    return datetime.now(timezone.utc)

class MastersMake(Base):
    __tablename__ = "masters_make"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=False, nullable=False)
    name_ci = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    url_link = Column(String(255))
    created_at = Column(DateTime, index=True, default=now_utc)
    updated_at = Column(DateTime, index=True, default=now_utc, onupdate=now_utc)
    status = Column(Boolean, nullable=False, default=True)

    # Relationships
    models = relationship("MastersModel", back_populates="make", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"MastersMake(id={self.id}, name={self.name!r}, updated_at={self.updated_at!r})"

# Event listener to generate slug and url_link before insert/update
@event.listens_for(MastersMake, 'before_insert')
@event.listens_for(MastersMake, 'before_update')
def generate_make_slug_and_url(mapper, connection, target):
    if target.name:
        # Generate slug from name if not already set
        if not target.slug:
            target.slug = target.name.lower().replace(" ", "-")
        # Generate url_link if not already set
        if not target.url_link:
            base_url = "https://www.carwale.com"
            target.url_link = urljoin(base_url, f"{target.slug}-cars/")


class MastersModel(Base):
    __tablename__ = "masters_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=False, nullable=False)
    name_ci = Column(String(255), unique=True, nullable=False, index=True)
    make_id = Column(Integer, ForeignKey("masters_make.id"), nullable=False)
    created_at = Column(DateTime, index=True, default=now_utc)
    updated_at = Column(DateTime, index=True, default=now_utc, onupdate=now_utc)
    status = Column(Boolean, nullable=False, default=True)

    # Relationships
    make = relationship("MastersMake", back_populates="models")
    variants = relationship("MastersVariant", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"MastersModel(make_id={self.make_id!r}, id={self.id}, name={self.name!r}, updated_at={self.updated_at!r})"


class MastersVariant(Base):
    __tablename__ = "masters_variant"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=False, nullable=False)
    name_ci = Column(String(255), unique=True, nullable=False, index=True)
    launch_year = Column(Integer, nullable=False)
    model_id = Column(Integer, ForeignKey("masters_model.id"), nullable=False)
    created_at = Column(DateTime, index=True, default=now_utc)
    updated_at = Column(DateTime, index=True, default=now_utc, onupdate=now_utc)
    status = Column(Boolean, nullable=False, default=True)

    # Relationships
    model = relationship("MastersModel", back_populates="variants")

# Optional additional indexes for performance
Index("ix_masters_model_make_id_name_ci", MastersModel.make_id, MastersModel.name_ci, unique=True)
Index("ix_masters_variant_model_id_name_ci", MastersVariant.model_id, MastersVariant.name_ci, unique=True)
