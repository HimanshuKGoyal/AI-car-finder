from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models.masters_make import MastersMake

def normalize(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s2 = s.strip()
    return s2.lower() if s2 else None

def ensure_make(db: Session, name: str, slug: Optional[str] = None, url: Optional[str] = None) -> MastersMake:
    name_norm = normalize(name)
    if not name_norm:
        raise ValueError("Make name is required")

    q = select(MastersMake).where(MastersMake.slug == name_norm)
    existing = db.execute(q).scalars().first()
    if existing:
        # Optionally update URL/active status
        if url and existing.url_link != url:
            existing.url = url
        
        db.commit()
        db.refresh(existing)
        return existing
    obj = MastersMake(name=name, url_link=url)
    db.add(obj)
    db.flush()
    return obj

# def ensure_model(
#     db: Session,
#     make_id: int,
#     name: str,
#     body_type: str,
#     launch_year: Optional[int] = None,
#     last_active_year: Optional[int] = None,
#     ncap_rating: Optional[float] = None,
# ) -> MastersModel:
#     name_norm = normalize(name)
#     if not name_norm:
#         raise ValueError("Model name is required")

#     # Find existing for this make
#     q = select(MastersModel).where(MastersModel.make_id == make_id, MastersModel.name_ci == name_norm)
#     existing = db.execute(q).scalar_one_or_none()
#     if existing:
#         # Update mutable fields
#         updated = False
#         for attr, val in [
#             ("body_type", body_type),
#             ("launch_year", launch_year),
#             ("last_active_year", last_active_year),
#             ("ncap_rating", ncap_rating),
#         ]:
#             if val is not None and getattr(existing, attr) != val:
#                 setattr(existing, attr, val)
#                 updated = True
#         if updated:
#             db.commit()
#             db.refresh(existing)
#         return existing
#     obj = MastersModel(
#         make_id=make_id,
#         name=name,
#         body_type=body_type,
#         launch_year=launch_year,
#         last_active_year=last_active_year,
#         ncap_rating=ncap_rating,
#     )
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj


# def ensure_variant(
#     db: Session,
#     model_id: int,
#     name: str,
#     launch_year: Optional[int] = None,
#     discontinue_year: Optional[int] = None,
# ) -> MastersVariant:
#     name_norm = normalize(name)
#     if not name_norm:
#         raise ValueError("Variant name is required")

#     q = select(MastersVariant).where(MastersVariant.model_id == model_id, MastersVariant.name_ci == name_norm)
#     existing = db.execute(q).scalar_one_or_none()
#     if existing:
#         updated = False
#         for attr, val in [
#             ("launch_year", launch_year),
#             ("discontinue_year", discontinue_year),
#         ]:
#             if val is not None and getattr(existing, attr) != val:
#                 setattr(existing, attr, val)
#                 updated = True
#         if updated:
#             db.commit()
#             db.refresh(existing)
#         return existing
#     obj = MastersVariant(model_id=model_id, name=name, launch_year=launch_year, discontinue_year=discontinue_year)
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj

# def upsert_variant_specs(
#     db: Session,
#     variant_id: int,
#     *,
#     cc: Optional[int] = None,
#     fuel_type: Optional[str] = None,
#     transmission_type: Optional[str] = None,
#     mileage_kmpl: Optional[float] = None,
#     engine_text: Optional[str] = None,
#     airbags: Optional[int] = None,
#     length_mm: Optional[int] = None,
#     width_mm: Optional[int] = None,
#     height_mm: Optional[int] = None,
#     ground_clearance_mm: Optional[int] = None,
#     power_hp: Optional[float] = None,
#     torque_nm: Optional[float] = None,
#     cabin_ergonomics_text: Optional[str] = None,
#     colors_available: Optional[Dict[str, Any]] = None,
#     features: Optional[Dict[str, Any]] = None,
#     reliability_score: Optional[int] = None,
# ) -> VariantSpecs:
#     q = select(VariantSpecs).where(VariantSpecs.variant_id == variant_id)
#     existing = db.execute(q).scalar_one_or_none()
#     if existing:
#         # Update any provided field
#         updates = {
#             "cc": cc,
#             "fuel_type": fuel_type,
#             "transmission_type": transmission_type,
#             "mileage_kmpl": mileage_kmpl,
#             "engine_text": engine_text,
#             "airbags": airbags,
#             "length_mm": length_mm,
#             "width_mm": width_mm,
#             "height_mm": height_mm,
#             "ground_clearance_mm": ground_clearance_mm,
#             "power_hp": power_hp,
#             "torque_nm": torque_nm,
#             "cabin_ergonomics_text": cabin_ergonomics_text,
#             "colors_available": colors_available,
#             "features": features,
#             "reliability_score": reliability_score,
#         }
#         changed = False
#         for k, v in updates.items():
#             if v is not None and getattr(existing, k) != v:
#                 setattr(existing, k, v)
#                 changed = True
#         if changed:
#             db.commit()
#             db.refresh(existing)
#         return existing
#     obj = VariantSpecs(
#         variant_id=variant_id,
#         cc=cc,
#         fuel_type=fuel_type,
#         transmission_type=transmission_type,
#         mileage_kmpl=mileage_kmpl,
#         engine_text=engine_text,
#         airbags=airbags,
#         length_mm=length_mm,
#         width_mm=width_mm,
#         height_mm=height_mm,
#         ground_clearance_mm=ground_clearance_mm,
#         power_hp=power_hp,
#         torque_nm=torque_nm,
#         cabin_ergonomics_text=cabin_ergonomics_text,
#         colors_available=colors_available,
#         features=features,
#         reliability_score=reliability_score,
#     )
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj

# def add_price_snapshot(
#     db: Session,
#     variant_id: int,
#     ex_showroom_price_inr: int,
#     effective_date: Optional[datetime] = None,
#     city: Optional[str] = None,
#     source: Optional[str] = None,
# ) -> VariantPriceHistory:
#     snap = VariantPriceHistory(
#         variant_id=variant_id,
#         ex_showroom_price_inr=ex_showroom_price_inr,
#         effective_date=effective_date or datetime.utcnow(),
#         city=city,
#         source=source,
#     )
#     db.add(snap)
#     db.commit()
#     db.refresh(snap)
#     return snap

# def get_latest_price(db: Session, variant_id: int) -> Optional[int]:
#     q = (
#         select(VariantPriceHistory.ex_showroom_price_inr)
#         .where(VariantPriceHistory.variant_id == variant_id)
#         .order_by(desc(VariantPriceHistory.effective_date))
#         .limit(1)
#     )
#     return db.execute(q).scalar_one_or_none()


# # Older SQL ALchemy 1.0 function. ZRevisit if needed them
# # Convenience functions for read access
# def get_make_by_name_ci(session, name: str) -> Optional[MastersMake]:
#     name_norm = normalize(name)
#     if not name_norm:
#         return None
#     return session.execute(select(MastersMake).where(MastersMake.name_ci == name_norm)).scalars().first()

# def get_model_by_name_ci(session, make_id: int, model_name: str) -> Optional[MastersModel]:
#     name_norm = normalize(model_name)
#     if not name_norm:
#         return None
#     return session.execute(
#         select(MastersModel).where(
#             (MastersModel.make_id == make_id) & (MastersModel.name_ci == name_norm)
#         )
#     ).scalars().first()

# def get_variant_by_name_ci(session, model_id: int, variant_name: str) -> Optional[MastersVariant]:
#     name_norm = normalize(variant_name)
#     if not name_norm:
#         return None
#     return session.execute(
#         select(MastersVariant).where(
#             (MastersVariant.model_id == model_id) & (MastersVariant.name_ci == name_norm)
#         )
#     ).scalars().first()


# if __name__ == "__main__":
#     # Quick manual verification
#     session = SessionLocal()
#     try:
#         m = ensure_make(session, "Hyundai")
#         print("Make:", m)

#         mdl = ensure_model(session, "Hyundai", "i20", launch_year=2010)
#         print("Model:", mdl)

#         var = ensure_variant(session, "Hyundai", "i20", "Sportz")
#         print("Variant:", var)

#         # Case-insensitive checks
#         mdl2 = ensure_model(session, "HYUNDAI", "I20", launch_year=2010)
#         print("Model CI:", mdl2)

#         var2 = ensure_variant(session, "hyundai", "i20", "sportz")
#         print("Variant CI:", var2)
#     finally:
#         session.close()
