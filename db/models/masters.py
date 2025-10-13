from db.base import Base
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, event, Float, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from urllib.parse import urljoin

def now_utc():
    return datetime.now(timezone.utc)

class MastersMake(Base):
    __tablename__ = "masters_make"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    name_ci: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active_india: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    brand_perception_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1–10
    brand_resale_score: Mapped[int | None] = mapped_column(Integer, nullable=True)      # 1–10

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), onupdate=func.now())

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    make_id: Mapped[int] = mapped_column(ForeignKey("masters_make.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_ci: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    launch_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_active_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ncap_rating: Mapped[float | None] = mapped_column(Float, nullable=True)  # e.g., 0–5 stars
    body_type: Mapped[str] = mapped_column(String(40), nullable=False)       # "Hatchbacks" | "SUV" | etc.

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    make = relationship("MasterMake", backref="models", lazy="joined")

# Event listener to generate slug and url_link before insert/update
@event.listens_for(MastersModel, 'before_insert')
@event.listens_for(MastersModel, 'before_update')
def generate_model_slug(mapper, connection, target):
    if target.name:
        # Generate slug from name if not already set
        if not target.slug:
            target.slug = target.name.lower().replace(" ", "-")


class MastersVariant(Base):
    __tablename__ = "masters_variant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("masters_model.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    name_ci: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    launch_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discontinue_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)  # optional: source url/descriptor

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    model = relationship("MasterModel", backref="variants", lazy="joined")

# Event listener to generate slug and url_link before insert/update
@event.listens_for(MastersVariant, 'before_insert')
@event.listens_for(MastersVariant, 'before_update')
def generate_variant_slug(mapper, connection, target):
    if target.name:
        # Generate slug from name if not already set
        if not target.slug:
            target.slug = target.name.lower().replace(" ", "-")


class VariantSpecs(Base):
    __tablename__ = "variant_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("master_variant.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Static technical + feature fields
    cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(20), nullable=True)    # Petrol/Diesel/CNG/Electric/LPG
    transmission_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # MT/AMT/CVT/DCT/AT
    mileage_kmpl: Mapped[float | None] = mapped_column(Float, nullable=True)

    engine_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    airbags: Mapped[int | None] = mapped_column(Integer, nullable=True)

    length_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ground_clearance_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    power_hp: Mapped[float | None] = mapped_column(Float, nullable=True)
    torque_nm: Mapped[float | None] = mapped_column(Float, nullable=True)

    cabin_ergonomics_text: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Colors and features as JSON for flexibility (TEXT in SQLite, JSON/JSONB in Postgres)
    colors_available: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # e.g., {"colors": ["white","blue"]}
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)          # flags: rear_camera, esc, aeb, etc.
    reliability_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1–5 proxy

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    variant = relationship("MasterVariant", backref="specs", lazy="joined")


class VariantPriceHistory(Base):
    __tablename__ = "variant_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("master_variant.id", ondelete="CASCADE"), nullable=False)

    ex_showroom_price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_date: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)  # when price became effective
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)  # optional: city-specific pricing

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variant = relationship("MasterVariant", backref="price_history")



class VariantQualScore(Base):
    __tablename__ = "variant_qual_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("master_variant.id", ondelete="CASCADE"), nullable=False)

    # category: infotainment | driver_assistance | telematics | lighting | active_safety | performance_params | known_issues
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # e.g., {"responsiveness":4,"wireless_stability":3}
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variant = relationship("MasterVariant", backref="qual_scores")



# Optional additional indexes for performance
Index("ix_masters_model_make_id_name_ci", MastersModel.make_id, MastersModel.name_ci, unique=True)
Index("ix_masters_variant_model_id_name_ci", MastersVariant.model_id, MastersVariant.name_ci, unique=True)
