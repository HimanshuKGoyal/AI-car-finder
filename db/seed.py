# reco_service/db/seed.py
from typing import List
from db.base import SessionLocal
from db.models.masters import MastersMake
from db.repositories.masters_repo import ensure_make

DEFAULT_MAKES: List[str] = [
            "Bugatti", "Chevrolet", "Daewoo", "Datsun", "Ford", 
            "Hindustan Motors", "Hummer", "ICML", "Mahindra Renault",
            "Mitsubishi", "Opel", "Premier", "San", "Ssangyong",
            "Aston Martin", "Audi", "Bentley", "BMW", "BYD",
            "Citroen", "Ferrari", "Fiat", "Fisker", "Force Motors",
            "Honda", "Hyundai", "Isuzu", "Jaguar", "Jeep",
            "Kia", "Lamborghini", "Land Rover", "Leapmotor", "Lexus",
            "Lotus", "Mahindra", "Maruti Suzuki", "Maserati", "Maybach",
            "McLaren", "Mercedes-Benz", "MG", "Mini", "Nissan",
            "Ola", "Porsche", "Pravaig", "Renault", "Rolls-Royce",
            "Skoda", "Tata", "Tesla", "Toyota", "Vinfast",
            "Volkswagen", "Volvo"
        ]

def is_table_empty(session) -> bool:
    # Efficient emptiness check
    return session.query(MastersMake.id).limit(1).first() is None

def seed_makes_if_empty():
    session = SessionLocal()
    try:
        # Ensure tables are created if they don't exist
        
        if is_table_empty(session):
            print("masters_make is empty. Seeding default makes...")
            for make in DEFAULT_MAKES:
                # ensure_make handles case-insensitivity and slug creation
                ensure_make(session, make)
            print("Seeding complete.")
        else:
            print("masters_make already has data. Skipping seeding.")
    finally:
        session.close()

if __name__ == "__main__":
    seed_makes_if_empty()
