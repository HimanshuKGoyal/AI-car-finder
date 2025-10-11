from db.base import engine, Base
from db.seed import seed_makes_if_empty

def create_tables():
    print("Initiating DB Tables Creation on engine: ", engine.url)
    Base.metadata.create_all(bind=engine)
    print("Done. If using SQLite, local_db.sqlite should now exist.")


if __name__=="__main__":
    create_tables()
    seed_tables()