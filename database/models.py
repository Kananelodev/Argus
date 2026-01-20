import uuid
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID # Compatible with other dialects via generic types if careful, better to use standard type decorator for cross-compat if needed, but for now we'll use string or TypeDecorator for UUID in SQLite.
# For simplicity and cross-compatibility (SQLite doesn't have native UUID), we will use String for UUIDs in this implementation 
# or a custom TypeDecorator. Let's use standard String(36) for UUIDs to ensure it works on SQLite and MSSQL easily.

class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department(name='{self.name}')>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False) # e.g., "Trader", "Risk Officer"
    did = Column(String(200), unique=True, nullable=True) # Decentralized ID
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Relationships
    department = relationship("Department", back_populates="users")
    requests = relationship("VerificationRequest", back_populates="requester")

    def __repr__(self):
        return f"<User(name='{self.name}', role='{self.role}')>"

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    ipfs_hash = Column(String(200), nullable=False)
    required_privacy_level = Column(String(50), default="Standard")
    
    # Relationships
    verification_requests = relationship("VerificationRequest", back_populates="model")

    def __repr__(self):
        return f"<Model(name='{self.name}', version='{self.version}')>"

class VerificationRequest(Base):
    __tablename__ = "verification_requests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    input_context = Column(Text, nullable=False) # e.g. "Loan App #12345"
    status = Column(String(20), default="PENDING") # PENDING, VERIFIED, FLAGGED
    proof_cid = Column(String(200), nullable=True) # IPFS content ID of the proof
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    requester_id = Column(Integer, ForeignKey("users.id"))
    model_id = Column(Integer, ForeignKey("model_registry.id"))
    
    # Relationships
    requester = relationship("User", back_populates="requests")
    model = relationship("ModelRegistry", back_populates="verification_requests")

    def __repr__(self):
        return f"<Request(id='{self.id}', status='{self.status}')>"
