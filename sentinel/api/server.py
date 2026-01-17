import json
import time

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from sentinel.storage.ipfs import IPFSStorage
from sentinel.core.proof import ProofGenerator

app = FastAPI(title="Argus API")
storage = IPFSStorage()

# In-memory event log for live feed (Last 5 proofs)
latest_events = []

# Ensure web directory exists
web_dir = Path(__file__).parent.parent / "web"
if not web_dir.exists():
    web_dir.mkdir(parents=True)

@app.get("/")
async def read_root():
    return FileResponse(web_dir / "index.html")

@app.post("/api/broadcast")
async def broadcast_proof(data: dict):
    """
    Receive a new proof/CID from the CLI and add it to the live feed.
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
    """
    Return the latest broadcasted events.
    """
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
