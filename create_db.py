from database.connection import engine, SessionLocal
from database.models import Base, Department, User, ModelRegistry
# Import all models so Base.metadata can find them

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def seed_data():
    db = SessionLocal()
    
    # Check if data already exists to avoid duplicates
    if db.query(Department).count() > 0:
        print("Data already exists. Skipping seed.")
        db.close()
        return

    print("Seeding data...")
    
    # 1. Departments
    dept_trading = Department(name="High Frequency Trading")
    dept_risk = Department(name="Risk Management")
    dept_hr = Department(name="Human Resources")
    dept_it = Department(name="IT Security")
    
    db.add_all([dept_trading, dept_risk, dept_hr, dept_it])
    db.commit()
    
    # 2. Users
    user_trader = User(name="Alice Trader", role="Trader", department=dept_trading, did="did:eth:0x123...")
    user_risk = User(name="Bob Officer", role="Risk Officer", department=dept_risk, did="did:eth:0x456...")
    user_dev = User(name="Charlie Dev", role="Developer", department=dept_it, did="did:eth:0x789...")
    
    db.add_all([user_trader, user_risk, user_dev])
    db.commit()
    
    # 3. Models
    model_loan = ModelRegistry(name="Credit Scoring Model", version="v1.0", ipfs_hash="QmHash1...", required_privacy_level="High")
    model_fraud = ModelRegistry(name="Fraud Detection", version="v2.1", ipfs_hash="QmHash2...", required_privacy_level="Standard")
    
    db.add_all([model_loan, model_fraud])
    db.commit()
    
    print("Database seeded with initial data!")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
