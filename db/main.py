from db.base import engine, Base
from db.models import MastersMake, Country, BrandPresence, RevvFeedback, RevvRequest, RevvRanking

def create_tables():
    print("Initiating DB Tables Creation on engine: ", engine.url)
    # Import all models to ensure they are registered with Base.metadata
    
    # Explicitly reference the models to ensure they are registered
    _ = [MastersMake, Country, BrandPresence, RevvFeedback, RevvRequest, RevvRanking]
    print(Base.metadata)
    print("Tables found in metadata:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Done. If using SQLite, local_db.sqlite should now exist.")


if __name__=="__main__":
    create_tables()