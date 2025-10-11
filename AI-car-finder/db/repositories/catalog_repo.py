from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, aliased

from app.db.models.master_make import MasterMake
from app.db.models.master_model import MasterModel
from app.db.models.master_variant import MasterVariant
from app.db.models.variant_specs import VariantSpecs
from app.db.models.variant_price_history import VariantPriceHistory

def get_latest_price_subquery():
    """
    Subquery to get latest price per variant (by effective_date).
    Returns columns: variant_id, ex_showroom_price_inr, effective_date
    """
    vph = aliased(VariantPriceHistory)

    # Find max effective_date per variant
    max_dates = (
        select(vph.variant_id, func.max(vph.effective_date).label("max_date"))
        .group_by(vph.variant_id)
        .subquery()
    )

    latest = (
        select(vph.variant_id, vph.ex_showroom_price_inr, vph.effective_date)
        .join(max_dates, (vph.variant_id == max_dates.c.variant_id) & (vph.effective_date == max_dates.c.max_date))
        .subquery()
    )
    return latest

def fetch_active_variants_with_specs(
    db: Session,
    *,
    allowed_body_types: Optional[Sequence[str]] = None,
    allowed_fuel_types: Optional[Sequence[str]] = None,
    max_budget_inr: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch active make/model/variants joined with specs and latest price.
    Filters:
      - model.body_type ∈ allowed_body_types (if provided)
      - specs.fuel_type ∈ allowed_fuel_types (if provided)
      - latest_price.ex_showroom_price_inr ≤ max_budget_inr (if provided)
      - make.is_active_india = True
      - model.last_active_year IS NULL OR model.last_active_year >= current year
      - variant.discontinue_year IS NULL OR variant.discontinue_year >= current year
    Returns CarSpec-like dicts for ranking consumption.
    """
    latest_price_sq = get_latest_price_subquery()

    # Current year logic for "active" constraint
    from datetime import datetime
    current_year = datetime.utcnow().year

    stmt = (
        select(
            MasterMake.id.label("make_id"),
            MasterMake.name.label("make"),
            MasterMake.is_active_india.label("make_active"),
            MasterMake.brand_perception_score,
            MasterMake.brand_resale_score,
            MasterModel.id.label("model_id"),
            MasterModel.name.label("model"),
            MasterModel.body_type.label("body_type"),
            MasterModel.launch_year,
            MasterModel.last_active_year,
            MasterModel.ncap_rating,
            MasterVariant.id.label("variant_id"),
            MasterVariant.name.label("variant"),
            MasterVariant.launch_year,
            MasterVariant.discontinue_year,
            VariantSpecs.fuel_type,
            VariantSpecs.mileage_kmpl,
            VariantSpecs.airbags,
            VariantSpecs.power_hp,
            VariantSpecs.torque_nm,
            VariantSpecs.features,
            VariantSpecs.colors_available,
            latest_price_sq.c.ex_showroom_price_inr.label("price_inr"),
        )
        .join(MasterModel, MasterModel.make_id == MasterMake.id)
        .join(MasterVariant, MasterVariant.model_id == MasterModel.id)
        .join(VariantSpecs, VariantSpecs.variant_id == MasterVariant.id)
        .join(latest_price_sq, latest_price_sq.c.variant_id == MasterVariant.id)
        .where(MasterMake.is_active_india)
        .where((MasterModel.last_active_year.is_(None)) | (MasterModel.last_active_year >= current_year))
        .where((MasterVariant.discontinue_year.is_(None)) | (MasterVariant.discontinue_year >= current_year))
        .order_by(desc(latest_price_sq.c.ex_showroom_price_inr))
        .limit(limit)
    )

    if allowed_body_types:
        stmt = stmt.where(MasterModel.body_type.in_(allowed_body_types))
    if allowed_fuel_types:
        stmt = stmt.where(VariantSpecs.fuel_type.in_(allowed_fuel_types))
    if max_budget_inr is not None:
        stmt = stmt.where(latest_price_sq.c.ex_showroom_price_inr <= max_budget_inr)

    rows = db.execute(stmt).mappings().all()

    # Map DB rows to CarSpec dict consumed by ranking_engine
    specs: List[Dict[str, Any]] = []
    for r in rows:
        mmv = f"{r['make']} {r['model']} {r['variant']}".strip()
        features_obj = r["features"] or {}
        colors_obj = r["colors_available"] or {}

        specs.append(
            {
                "mmv": mmv,
                "make": r["make"],
                "model": r["model"],
                "variant": r["variant"],
                "bodyType": r["body_type"],  # model-level body type
                "fuelType": r["fuel_type"],
                "price": int(r["price_inr"]) if r["price_inr"] is not None else None,  # ex-showroom INR
                "mileage_kmpl": float(r["mileage_kmpl"]) if r["mileage_kmpl"] is not None else None,
                "safety_airbags": int(r["airbags"]) if r["airbags"] is not None else 0,
                "has_esp": bool(features_obj.get("esc") or features_obj.get("esp", False)),
                "features": {
                    "rear_camera": bool(features_obj.get("rear_camera", False)),
                    "cruise_control": bool(features_obj.get("cruise_control", False)),
                    "wireless_android_auto": bool(features_obj.get("wireless_android_auto", False)),
                    "wireless_carplay": bool(features_obj.get("wireless_carplay", False)),
                    "tpms": bool(features_obj.get("tpms", False)),
                    "sunroof": bool(features_obj.get("sunroof", False)),
                    "isofix": bool(features_obj.get("isofix", False)),
                    "abs": bool(features_obj.get("abs_ebd", False) or features_obj.get("abs", False)),
                    "esc": bool(features_obj.get("esc", False)),
                    "traction_control": bool(features_obj.get("traction_control", False)),
                    "aeb": bool(features_obj.get("aeb", False)),
                },
                "performance_power_hp": float(r["power_hp"]) if r["power_hp"] is not None else None,
                "torque_nm": float(r["torque_nm"]) if r["torque_nm"] is not None else None,
                "colors": colors_obj.get("colors", []),
                # Optional propagation of brand attributes (if you want in ranking):
                "brand_value": r["brand_perception_score"] or 0,
            }
        )
    return specs
