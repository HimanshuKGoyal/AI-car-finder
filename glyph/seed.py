# filename: app/seed_from_csv.py
from __future__ import annotations
import csv
from pathlib import Path
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.base import SessionLocal
from db.models import MastersMake, Country, BrandPresence
from db.repositories.masters_repo import ensure_make



CSV_PATH = Path(__file__).parent / "data" / "brand_presence_india.csv"

def parse_year(val: str | None) -> Optional[int]:
    v = (val or "").strip()
    if not v:
        return None
    try:
        y = int(v)
        if 1800 <= y <= 9999:
            return y
        return None
    except ValueError:
        return None

def year_to_start(y: int) -> date:
    return date(y, 1, 1)

def year_to_end_exclusive(y: int) -> date:
    # Exclusive end: Jan 1 of next year
    return date(y, 12, 31)

def upsert_country(db: Session, iso_code: str, name: str) -> Country:
    country = db.query(Country).filter(Country.iso_code == iso_code).one_or_none()
    if country is None:
        country = Country(iso_code=iso_code, name=name)
        db.add(country)
        db.flush()  # assign id
    return country

def upsert_brand(db: Session, name: str) -> MastersMake:
    brand = db.query(MastersMake).filter(MastersMake.name == name).one_or_none()
    if brand is None:
        brand = MastersMake(name=name)
        db.add(brand)
        db.flush()
    return brand  

def insert_presence_if_applicable(
    db: Session,
    brand_id: int,
    country_id: int,
    start_year: Optional[int],
    end_year: Optional[int],
) -> None:
    # Skip rows where both are None (not launched)
    if start_year is None and end_year is None:
        return

    # If only end_year exists but no start, skip (inconsistent)
    if start_year is None and end_year is not None:
        return

    start = year_to_start(start_year)
    end = None
    if end_year is not None:
        if end_year < start_year:
            # invalid interval; skip
            return
        end = year_to_end_exclusive(end_year)

    bp = BrandPresence(
        brand_id=brand_id,
        country_id=country_id,
        active_start=start,
        active_end=end,
    )
    db.add(bp)

def seed():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")

    db: Session = SessionLocal()
    try:
        # 1) Ensure India country exists
        india = upsert_country(db, iso_code="IN", name="India")

        # 2) Read CSV (auto-detect comma vs tab; your file is CSV so comma)
        with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
            sample = f.read(2048)
            delimiter = "," if sample.count(",") >= sample.count("\t") else "\t"
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)

            for row in reader:
                brand_name = (row.get("Brand") or "").strip()
                country_name = (row.get("Country") or "").strip()
                start_year = parse_year(row.get("Active Start"))
                end_year = parse_year(row.get("Active End"))
                print(brand_name, country_name, start_year, end_year)
                if not brand_name:
                    continue
                # Only seed India rows
                if country_name and country_name.lower() != "india":
                    continue

                brand = upsert_brand(db, brand_name)
                insert_presence_if_applicable(
                    db,
                    brand_id=brand.id,
                    country_id=india.id,
                    start_year=start_year,
                    end_year=end_year,
                )

        try:
            db.commit()
        except IntegrityError as e:
            # Overlaps or duplicates will raise here (due to constraints)
            db.rollback()
            raise e

        print("Seeding completed: Brands + India + presence intervals from CSV.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()





# # scripts/seed_catalog.py

# import csv
# import json
# from pathlib import Path
# from typing import Dict, Any, List, Optional
# from sqlalchemy.orm import Session
# from app.db.base import SessionLocal
# from app.db.repositories.makes_repo import ensure_make
# from app.db.repositories.models_repo import ensure_model
# from app.db.repositories.variants_repo import ensure_variant
# from app.db.repositories.specs_repo import upsert_variant_specs
# from app.db.repositories.prices_repo import add_price_snapshot

# # Configure your input files
# CSV_FILE = Path("data/catalog.csv")           # columns: make, model, variant, body_type, price_inr, fuel_type, mileage_kmpl, airbags, power_hp, torque_nm, features_json
# JSON_FILE = Path("data/qual_scores.json")     # optional qualitative scores per variant

# def parse_int(val: str) -> Optional[int]:
#     if val is None:
#         return None
#     s = str(val).strip().replace(",", "")
#     if not s:
#         return None
#     try:
#         return int(float(s))
#     except:
#         return None

# def parse_float(val: str) -> Optional[float]:
#     if val is None:
#         return None
#     s = str(val).strip().replace(",", "")
#     if not s:
#         return None
#     try:
#         return float(s)
#     except:
#         return None

# def load_features_json(val: str) -> Dict[str, Any]:
#     if not val:
#         return {}
#     try:
#         obj = json.loads(val)
#         if isinstance(obj, dict):
#             return obj
#         return {}
#     except:
#         return {}

# def seed_from_csv(db: Session, csv_path: Path):
#     with csv_path.open("r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             make_name = row.get("make", "").strip()
#             model_name = row.get("model", "").strip()
#             variant_name = row.get("variant", "").strip()
#             body_type = row.get("body_type", "").strip()  # required at model level

#             if not make_name or not model_name or not variant_name or not body_type:
#                 continue  # skip incomplete rows

#             # Ensure make/model/variant
#             make = ensure_make(db, name=make_name, is_active_india=True)
#             model = ensure_model(
#                 db,
#                 make_id=make.id,
#                 name=model_name,
#                 body_type=body_type,
#                 launch_year=parse_int(row.get("model_launch_year") or ""),
#                 last_active_year=parse_int(row.get("model_last_active_year") or ""),
#                 ncap_rating=parse_float(row.get("model_ncap_rating") or ""),
#             )
#             variant = ensure_variant(
#                 db,
#                 model_id=model.id,
#                 name=variant_name,
#                 launch_year=parse_int(row.get("variant_launch_year") or ""),
#                 discontinue_year=parse_int(row.get("variant_discontinue_year") or ""),
#             )

#             # Upsert specs
#             features = load_features_json(row.get("features_json") or "")
#             colors_list = [c.strip().lower() for c in (row.get("colors_available") or "").split("|") if c.strip()]
#             colors_obj = {"colors": colors_list} if colors_list else {}

#             upsert_variant_specs(
#                 db,
#                 variant_id=variant.id,
#                 cc=parse_int(row.get("cc") or ""),
#                 fuel_type=(row.get("fuel_type") or "").strip() or None,
#                 transmission_type=(row.get("transmission_type") or "").strip() or None,
#                 mileage_kmpl=parse_float(row.get("mileage_kmpl") or ""),
#                 engine_text=(row.get("engine") or "").strip() or None,
#                 airbags=parse_int(row.get("airbags") or ""),
#                 length_mm=parse_int(row.get("length_mm") or ""),
#                 width_mm=parse_int(row.get("width_mm") or ""),
#                 height_mm=parse_int(row.get("height_mm") or ""),
#                 ground_clearance_mm=parse_int(row.get("ground_clearance_mm") or ""),
#                 power_hp=parse_float(row.get("power_hp") or ""),
#                 torque_nm=parse_float(row.get("torque_nm") or ""),
#                 cabin_ergonomics_text=(row.get("cabin_ergonomics") or "").strip() or None,
#                 colors_available=colors_obj or None,
#                 features=features or None,
#                 reliability_score=parse_int(row.get("reliability_score") or ""),
#             )

#             # Price snapshot
#             price_inr = parse_int(row.get("price_inr") or row.get("ex_showroom_price_inr") or "")
#             if price_inr:
#                 add_price_snapshot(db, variant_id=variant.id, ex_showroom_price_inr=price_inr)

# def main():
#     db = SessionLocal()
#     try:
#         if CSV_FILE.exists():
#             seed_from_csv(db, CSV_FILE)
#             print("Seeded catalog from", CSV_FILE)
#         else:
#             print("CSV file not found:", CSV_FILE)
#     finally:
#         db.close()

# if __name__ == "__main__":
#     main()



# # scripts/seed_catalog_from_csv.py
# # Seeds: MasterMake, MasterModel, MasterVariant, VariantSpecs, VariantPriceHistory
# # Data source: a CSV of active cars (ex-showroom prices) as of 1 April 2025

# import csv
# import sys
# from pathlib import Path
# from datetime import datetime, timezone
# from typing import Optional

# from sqlalchemy.orm import Session

# # Import your app DB + repositories
# try:
#     from app.db.base import SessionLocal
#     from app.db.repositories.makes_repo import ensure_make
#     from app.db.repositories.models_repo import ensure_model
#     from app.db.repositories.variants_repo import ensure_variant
#     from app.db.repositories.specs_repo import upsert_variant_specs
#     from app.db.repositories.prices_repo import add_price_snapshot
# except ImportError as e:
#     print("Error importing app modules. Ensure PYTHONPATH includes project root and dependencies are installed.")
#     raise

# # 1 April 2025 snapshot timestamp (UTC)
# SNAPSHOT_DATE = datetime(2025, 4, 1, 0, 0, 0, tzinfo=timezone.utc)

# # Provide CSV path via CLI or default
# DEFAULT_CSV_PATH = Path("data/active_prices_2025_04_01.csv")


# def parse_price_inr(text: str) -> Optional[int]:
#     """
#     Convert price strings like:
#       - 'Rs. 46.99 Lakh' → 4699000
#       - 'Rs. 1.34 Crore' → 13400000
#       - 'Rs.  N/A' → None
#       - '' → None
#     Handles commas, extra spaces, and variants.
#     """
#     if not text:
#         return None
#     s = text.strip()
#     if s.lower().endswith("n/a") or "n/a" in s.lower():
#         return None
#     # Remove 'Rs.' and commas
#     s = s.replace("Rs.", "").replace(",", "").strip()

#     # Identify unit (Lakh or Crore); default assume plain INR if numeric
#     unit_multiplier = 1
#     if "lakh" in s.lower():
#         unit_multiplier = 100_000
#         s = s.lower().replace("lakh", "").strip()
#     elif "crore" in s.lower():
#         unit_multiplier = 10_000_000
#         s = s.lower().replace("crore", "").strip()

#     # Now s should be a float-ish number
#     try:
#         value = float(s)
#         return int(round(value * unit_multiplier))
#     except Exception:
#         # Some rows are empty or malformed—skip
#         return None


# def parse_int(text: str) -> Optional[int]:
#     if text is None:
#         return None
#     s = text.strip().replace(",", "")
#     if not s or s.lower() == "n/a":
#         return None
#     try:
#         return int(float(s))
#     except Exception:
#         return None


# def normalize_fuel_type(text: str) -> Optional[str]:
#     """
#     Normalize fuel type strings to consistent labels used in your enums.
#     Examples from the CSV:
#       - 'Petrol', 'Diesel', 'Electric'
#       - 'Hybrid (Electric + Petrol)', 'Mild Hybrid(Electric + Petrol)'
#       - 'Mild Hybrid (Electric + Diesel)', 'Plug-in Hybrid (Electric + Petrol)'
#     """
#     if not text:
#         return None
#     t = text.strip().lower()
#     if t in ("petrol", "diesel", "electric", "cng", "lpg"):
#         return t.capitalize() if t != "cng" and t != "lpg" else t.upper()
#     if "mild hybrid" in t and "diesel" in t:
#         return "Mild Hybrid (Electric + Diesel)"
#     if "mild hybrid" in t and "petrol" in t:
#         return "Mild Hybrid (Electric + Petrol)"
#     if "plug-in hybrid" in t or "phev" in t:
#         return "Plug-in Hybrid (Electric + Petrol)"
#     if "hybrid" in t and "petrol" in t:
#         return "Hybrid (Electric + Petrol)"
#     # Fallback to title-cased original
#     return text.strip()


# def normalize_transmission(text: str) -> Optional[str]:
#     """
#     Normalize transmission types:
#       - 'Manual' → 'Manual'
#       - 'Automatic (TC)' → 'Automatic (TC)'
#       - 'Automatic (DCT)' → 'Automatic (DCT)'
#       - 'Automatic (CVT)' → 'Automatic (CVT)'
#       - 'Clutchless Manual (IMT)' → 'Clutchless Manual (IMT)'
#       - 'Automatic' → 'Automatic' (no subtype)
#     """
#     if not text:
#         return None
#     return text.strip()


# def seed_csv(db: Session, csv_path: Path, default_body_type: str = "Unknown") -> int:
#     """
#     Seed the DB from the provided CSV.
#     Returns the number of rows successfully processed (with price).
#     """
#     count_seeded = 0
#     with csv_path.open("r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             brand = (row.get("Brand") or "").strip()
#             model_name = (row.get("Model Launch Names") or "").strip()
#             launch_year = parse_int(row.get("Launch Year") or "")
#             variant_name = (row.get("Variant Name") or "").strip()
#             price_text = (row.get("Ex-Showroom Price") or "").strip()
#             engine_cc = parse_int(row.get("Engine CC") or "")
#             fuel_type_raw = (row.get("Fuel Type") or "").strip()
#             transmission_raw = (row.get("Transmission Type") or "").strip()

#             # Skip incomplete rows
#             if not brand or not model_name or not variant_name:
#                 continue

#             price_inr = parse_price_inr(price_text)
#             if price_inr is None:
#                 # No price → we still ensure MMV/specs but skip price snapshot
#                 # You may choose to skip entirely; here we continue but don't count as seeded-price.
#                 pass

#             # Ensure Make
#             make = ensure_make(db, name=brand, is_active_india=True)

#             # Ensure Model (body_type unknown in this CSV—set placeholder)
#             model = ensure_model(
#                 db,
#                 make_id=make.id,
#                 name=model_name,
#                 body_type=default_body_type,
#                 launch_year=launch_year,
#                 last_active_year=None,  # treated active; update later if needed
#                 ncap_rating=None,
#             )

#             # Ensure Variant
#             variant = ensure_variant(
#                 db,
#                 model_id=model.id,
#                 name=variant_name,
#                 launch_year=launch_year,
#                 discontinue_year=None,  # active; update later if needed
#             )

#             # Upsert Specs (only known fields from CSV now)
#             upsert_variant_specs(
#                 db,
#                 variant_id=variant.id,
#                 cc=engine_cc,
#                 fuel_type=normalize_fuel_type(fuel_type_raw) or None,
#                 transmission_type=normalize_transmission(transmission_raw) or None,
#                 # We don’t have mileage/airbags/power etc. in this CSV → leave None
#             )

#             # Append price history snapshot (for rows that have price)
#             if price_inr is not None:
#                 add_price_snapshot(
#                     db,
#                     variant_id=variant.id,
#                     ex_showroom_price_inr=price_inr,
#                     effective_date=SNAPSHOT_DATE,
#                     city=None,    # could be expanded per-city later
#                     source="CSV: Active prices 2025-04-01",
#                 )
#                 count_seeded += 1

#     return count_seeded


# def main():
#     # CSV path from CLI or default
#     csv_arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV_PATH
#     if not csv_arg_path.exists():
#         print(f"CSV file not found at: {csv_arg_path}")
#         sys.exit(1)

#     db = SessionLocal()
#     try:
#         seeded = seed_csv(db, csv_arg_path, default_body_type="Unknown")
#         print(f"Seeding complete. Rows with price snapshots added: {seeded}")
#         print(f"Snapshot date: {SNAPSHOT_DATE.isoformat()}")
#     finally:
#         db.close()


# if __name__ == "__main__":
#     main()
