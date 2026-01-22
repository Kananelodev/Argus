from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    users = relationship("User", back_populates="department")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String) # Simple hash for demo
    full_name = Column(String)
    role = Column(String) # "TRADER", "RISK_OFFICER", "AUDITOR"
    department_id = Column(Integer, ForeignKey('departments.id'))
    did = Column(String) # Decentralized ID
    
    department = relationship("Department", back_populates="users")
    requests = relationship("VerificationRequest", back_populates="requester")

class VerificationRequest(Base):
    __tablename__ = 'verification_requests'
    id = Column(Integer, primary_key=True)
    req_uuid = Column(String, unique=True) # Public UUID
    requester_id = Column(Integer, ForeignKey('users.id'))
    model_name = Column(String)
    input_context = Column(String) # e.g. "Loan Application #999"
    status = Column(String, default="PENDING") # PENDING, VERIFIED, FLAGGED
    proof_cid = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", back_populates="requests")

# Database Setup (SQLite for Hackathon)
engine = create_engine('sqlite:///silverlock.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # SEED DATA
    db = SessionLocal()
    if not db.query(Department).first():
        deps = ["High Frequency Trading", "Risk Management", "HR", "IT Security"]
        for d in deps:
            db.add(Department(name=d))
        db.commit()
        
        # Seed Users
        risk_dept = db.query(Department).filter_by(name="Risk Management").first()
        trading_dept = db.query(Department).filter_by(name="High Frequency Trading").first()
        
        # Default password for everyone: "password123"
        # In real app: use bcrypt
        default_pw = "password123" 
        
        users = [
            User(username="alice_risk", password_hash=default_pw, full_name="Alice Chen", role="RISK_OFFICER", department=risk_dept, did="did:key:z6Mk...Alice"),
            User(username="bob_trader", password_hash=default_pw, full_name="Bob Smith", role="TRADER", department=trading_dept, did="did:key:z6Mk...Bob"),
            User(username="charlie_audit", password_hash=default_pw, full_name="Charlie Davis", role="AUDITOR", department=risk_dept, did="did:key:z6Mk...Charlie")
        ]
        db.add_all(users)
        db.commit()
    db.close()
