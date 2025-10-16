from db.base import Base
from typing import Optional, List
from sqlalchemy import String, Integer, event, CheckConstraint, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from urllib.parse import urljoin
from datetime import date
# from sqlalchemy.dialects.postgresql import DATERANGE

class MastersMake(Base):
    __tablename__ = "masters_make"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    url_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_perception_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1–10
    brand_resale_score: Mapped[int | None] = mapped_column(Integer, nullable=True)      # 1–10

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    presences: Mapped[List["BrandPresence"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )

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

class Country(Base):
    __tablename__ = "country"
    id: Mapped[int] = mapped_column(primary_key=True)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    presences: Mapped[List["BrandPresence"]] = relationship(
        back_populates="country", cascade="all, delete-orphan"
    )

class BrandPresence(Base):
    __tablename__ = "brand_presence"
    id: Mapped[int] = mapped_column(primary_key=True)

    brand_id: Mapped[int] = mapped_column(ForeignKey("masters_make.id", ondelete="CASCADE"), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id", ondelete="CASCADE"), nullable=False)

    active_start: Mapped[date] = mapped_column(nullable=False)
    active_end: Mapped[Optional[date]] = mapped_column(nullable=True)  # NULL means ongoing

    # Postgres daterange generated from start/end, half-open [start, end)
    # active_range: Mapped[object] = mapped_column(
    #     DATERANGE,
    #     nullable=False,
    #     server_default=text("daterange(active_start, active_end, '[)')"),
    # )

    brand: Mapped["MastersMake"] = relationship(back_populates="presences")
    country: Mapped["Country"] = relationship(back_populates="presences")

    __table_args__ = (
        CheckConstraint("active_end IS NULL OR active_end > active_start", name="chk_dates"),
        # Exclusion constraint prevents overlapping ranges per brand+country.
        # Requires btree_gist extension. SQLAlchemy passes this straight through.
        # {
        #     "postgresql_exclude": "(brand_id WITH =, country_id WITH =, active_range WITH &&)"
        # },
    )
