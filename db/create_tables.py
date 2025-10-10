from db.base import engine, Base

def main():
    print("Initiating DB Tables Creation on engine: ", engine.url)
    Base.metadata.create_all(bind=engine)
    print("Done. If using SQLite, local_db.sqlite should now exist.")


if __name__=="__main__":
    main()