# reco_service/jobs/scheduler_ap.py
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep
from db.base import SessionLocal
from db.repositories.masters_repo import ensure_make

REFRESH_MAKES = ["Maruti", "Hyundai", "Mahindra", "Tata", "Honda", "Toyota", "Kia"]

def refresh_makes_job():
    session = SessionLocal()
    try:
        print("[job] Refreshing makes...")
        for name in REFRESH_MAKES:
            ensure_make(session, name)
        print("[job] Done.")
    finally:
        session.close()

def main():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    # Run every day at 02:00
    scheduler.add_job(refresh_makes_job, "cron", hour=2, minute=0)
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()
