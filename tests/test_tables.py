# reco_service/db/inspect_tables.py
from db.base import SessionLocal
from db.models.masters_table import MastersMake  # change imports for other tables

def print_all_master_make():
    session = SessionLocal()
    try:
        rows = session.query(MastersMake).order_by(MastersMake.id).all()
        for r in rows:
            print(f"id={r.id}, name={r.name}, url={r.url_link}")
    finally:
        session.close()

if __name__ == "__main__":
    print_all_master_make()