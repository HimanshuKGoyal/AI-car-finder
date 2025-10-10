# reco_service/db/repositories/masters_repo.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.base import SessionLocal
from db.models.masters import MastersMake, MastersModel, MastersVariant
from datetime import datetime

def normalize(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s2 = s.strip()
    return s2.lower() if s2 else None

def ensure_make(session, name: str, slug: Optional[str] = None, url_link: Optional[str] = None) -> MastersMake:
    """
    Case-insensitive ensure for MastersMake.
    If slug is not provided, derive from normalized name.
    """
    name_norm = normalize(name)
    if not name_norm:
        raise ValueError("Make name is required")

    # Try to find existing by name_ci
    stmt = select(MastersMake).where(MastersMake.name_ci == name_norm)
    existing = session.execute(stmt).scalars().first()
    if existing:
        return existing

    row = MastersMake(name=name.strip(), name_ci=name_norm, slug=slug, url_link=url_link)
    session.add(row)
    try:
        session.commit()
        session.refresh(row)
        return row
    except IntegrityError:
        session.rollback()
        # Race or existing slug/name_ci; re-fetch by name_ci
        existing = session.execute(stmt).scalars().first()
        if existing:
            return existing

def ensure_model(session, make_name: str, model_name: str, launch_year: int) -> MastersModel:
    """
    Ensure a model exists under a make, case-insensitive.
    Uses composite uniqueness: (make_id, name_ci).
    """
    current_year = datetime.now().year

    if not isinstance(launch_year, int) or launch_year <current_year-20 or launch_year > current_year+2:
        raise ValueError("launch_year seems invalid")

    make = ensure_make(session, make_name)
    model_name_norm = normalize(model_name)
    if not model_name_norm:
        raise ValueError("Model name is required")

    # Find existing for this make
    stmt = select(MastersModel).where(
        (MastersModel.make_id == make.id) & (MastersModel.name_ci == model_name_norm)
    )
    existing = session.execute(stmt).scalars().first()
    if existing:
        return existing

    row = MastersModel(
        name=model_name.strip(),
        name_ci=model_name_norm,
        launch_year=launch_year,
        make_id=make.id,
    )
    session.add(row)
    try:
        session.commit()
        session.refresh(row)
        return row
    except IntegrityError:
        session.rollback()
        existing = session.execute(stmt).scalars().first()
        if existing:
            return existing
        raise

def ensure_variant(session, make_name: str, model_name: str, variant_name: str) -> MastersVariant:
    """
    Ensure a variant exists under a specific model of a make, case-insensitive.
    Composite uniqueness: (model_id, name_ci).
    """
    model = ensure_model(session, make_name, model_name, launch_year=2000)  # default if not needed
    # If you require launch_year to be exact, you can change ensure_variant signature to accept it.

    variant_name_norm = normalize(variant_name)
    if not variant_name_norm:
        raise ValueError("Variant name is required")

    stmt = select(MastersVariant).where(
        (MastersVariant.model_id == model.id) & (MastersVariant.name_ci == variant_name_norm)
    )
    existing = session.execute(stmt).scalars().first()
    if existing:
        return existing

    row = MastersVariant(
        name=variant_name.strip(),
        name_ci=variant_name_norm,
        model_id=model.id,
    )
    session.add(row)
    try:
        session.commit()
        session.refresh(row)
        return row
    except IntegrityError:
        session.rollback()
        existing = session.execute(stmt).scalars().first()
        if existing:
            return existing
        raise

# Convenience functions for read access
def get_make_by_name_ci(session, name: str) -> Optional[MastersMake]:
    name_norm = normalize(name)
    if not name_norm:
        return None
    return session.execute(select(MastersMake).where(MastersMake.name_ci == name_norm)).scalars().first()

def get_model_by_name_ci(session, make_id: int, model_name: str) -> Optional[MastersModel]:
    name_norm = normalize(model_name)
    if not name_norm:
        return None
    return session.execute(
        select(MastersModel).where(
            (MastersModel.make_id == make_id) & (MastersModel.name_ci == name_norm)
        )
    ).scalars().first()

def get_variant_by_name_ci(session, model_id: int, variant_name: str) -> Optional[MastersVariant]:
    name_norm = normalize(variant_name)
    if not name_norm:
        return None
    return session.execute(
        select(MastersVariant).where(
            (MastersVariant.model_id == model_id) & (MastersVariant.name_ci == name_norm)
        )
    ).scalars().first()


if __name__ == "__main__":
    # Quick manual verification
    session = SessionLocal()
    try:
        m = ensure_make(session, "Hyundai")
        print("Make:", m)

        mdl = ensure_model(session, "Hyundai", "i20", launch_year=2010)
        print("Model:", mdl)

        var = ensure_variant(session, "Hyundai", "i20", "Sportz")
        print("Variant:", var)

        # Case-insensitive checks
        mdl2 = ensure_model(session, "HYUNDAI", "I20", launch_year=2010)
        print("Model CI:", mdl2)

        var2 = ensure_variant(session, "hyundai", "i20", "sportz")
        print("Variant CI:", var2)
    finally:
        session.close()
