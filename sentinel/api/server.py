import json
import time
import uuid
from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from sqlalchemy.orm import Session
from sentinel.storage.ipfs import IPFSStorage
from sentinel.core.proof import ProofGenerator
from sentinel.models import init_db, SessionLocal, User, VerificationRequest, Department

# Initialize DB on startup
init_db()

app = FastAPI(title="Argus API")

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = IPFSStorage()

# In-memory event log for live feed (Legacy support)
latest_events = []

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure web directory exists
web_dir = Path(__file__).parent.parent / "web"
if not web_dir.exists():
    web_dir.mkdir(parents=True)

# --- Pydantic Schemas ---
class RequestCreate(BaseModel):
    username: str
    model_name: str
    input_context: str

class LoginRequest(BaseModel):
    username: str
    password: str

# --- API Routes ---

@app.get("/")
async def read_root():
    return FileResponse(web_dir / "portal.html")

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse(web_dir / "index.html")

@app.get("/portal")
async def read_portal_alias():
     return FileResponse(web_dir / "portal.html")

@app.post("/api/login")
async def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple password check (In prod use bcrypt.checkpw)
    if user.password_hash != login_req.password:
         raise HTTPException(status_code=401, detail="Invalid credentials")
         
    return {"id": user.id, "username": user.username, "role": user.role, "full_name": user.full_name, "department": user.department.name}

@app.post("/api/request")
async def create_request(req: RequestCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_req = VerificationRequest(
        req_uuid=str(uuid.uuid4()),
        requester_id=user.id,
        model_name=req.model_name,
        input_context=req.input_context,
        status="PENDING"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return {"status": "created", "uuid": new_req.req_uuid}

@app.get("/api/requests")
async def get_my_requests(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # RBAC Logic
    if user.role == "RISK_OFFICER":
        # Risk Officers see everything
        reqs = db.query(VerificationRequest).all()
    else:
        # Traders see only their own
        reqs = db.query(VerificationRequest).filter(VerificationRequest.requester_id == user.id).all()
        
    return reqs

@app.get("/api/queue")
async def get_pending_queue(db: Session = Depends(get_db)):
    """
    Endpoint for the Sentinel Node to fetch pending verification requests.
    """
    # Fetch all PENDING requests
    reqs = db.query(VerificationRequest).filter(VerificationRequest.status == "PENDING").all()
    return reqs

class CompletionRequest(BaseModel):
    req_uuid: str
    proof_cid: str
    status: str = "VERIFIED"

@app.post("/api/complete")
async def complete_request(data: CompletionRequest, db: Session = Depends(get_db)):
    """
    Endpoint for Sentinel Node to report completion.
    """
    req = db.query(VerificationRequest).filter(VerificationRequest.req_uuid == data.req_uuid).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req.status = data.status
    req.proof_cid = data.proof_cid
    db.commit()
    return {"status": "updated"}

@app.post("/api/broadcast")
async def broadcast_proof(data: dict):
    """
    Receive a new proof/CID from the CLI and add it to the live feed.
    Legacy endpoint specific to CLI integration.
    """
    global latest_events
    # Add timestamp server-side for sorting/filtering
    data["server_time"] = time.time()
    latest_events.insert(0, data)
    # Keep only last 10
    latest_events = latest_events[:10]
    return {"status": "broadcasted"}

@app.get("/api/feed")
async def get_feed():
    return latest_events

@app.get("/api/proof/{cid}")
async def get_proof(cid: str):
    proof = storage.get_proof(cid)
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    # Verify it on the fly
    is_valid = ProofGenerator.verify_proof(proof)
    return {
        "proof": proof,
        "is_valid": is_valid
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
