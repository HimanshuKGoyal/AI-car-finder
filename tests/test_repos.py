# reco_service/db/test_repos.py
from db.base import SessionLocal
from db.repositories.masters_make_repo import bulk_ensure_names, get_by_name, ensure_name

def main():
    session = SessionLocal()
    try:
        mapping = bulk_ensure_names(session, ["Maruti", "Hyundai", "Mahindra", "Hyundai", ""])
        print("Bulk mapping:", mapping)

        mm = ensure_name(session, "Tata")
        print("Single ensure:", mm)

        exists = get_by_name(session, "Hyundai")
        print("Get by name:", exists)
    finally:
        session.close()

if __name__ == "__main__":
    main()
