import json
import requests
from typing import Dict, Any, Optional

class IPFSStorage:
    def __init__(self, host: str = "http://127.0.0.1:5001"):
        self.host = host.rstrip('/')
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        try:
            # Simple check to see if IPFS API is up
            requests.post(f"{self.host}/api/v0/version", timeout=1)
            return True
        except:
            return False

    def save_proof(self, proof: Dict[str, Any]) -> str:
        """
        Saves the proof to IPFS and returns the CID.
        If IPFS is not available, returns a mock CID.
        """
        if self.available:
            try:
                files = {
                    'file': ('proof.json', json.dumps(proof))
                }
                res = requests.post(f"{self.host}/api/v0/add", files=files)
                res.raise_for_status()
                return res.json()['Hash']
            except Exception as e:
                print(f"Failed to upload to IPFS: {e}")
                return self._mock_save(proof)
        else:
            return self._mock_save(proof)

    def _mock_save(self, proof: Dict[str, Any]) -> str:
        # For development/demo without a running node
        import hashlib
        import os
        from pathlib import Path
        
        content = json.dumps(proof).encode('utf-8')
        mock_cid = "QmMock" + hashlib.sha256(content).hexdigest()[:40]
        
        # Save to local mock storage
        storage_dir = Path("sentinel_storage")
        storage_dir.mkdir(exist_ok=True)
        with open(storage_dir / f"{mock_cid}.json", "w") as f:
            f.write(json.dumps(proof))
            
        return mock_cid

    def get_proof(self, cid: str) -> Optional[Dict[str, Any]]:
        # Check mock storage first
        if cid.startswith("QmMock"):
            import os
            from pathlib import Path
            try:
                storage_path = Path(f"sentinel_storage/{cid}.json")
                if storage_path.exists():
                    with open(storage_path, "r") as f:
                        return json.load(f)
            except Exception as e:
                print(f"Mock storage error: {e}")
                return None
                
        if self.available:
            try:
                # Use the cat endpoint
                params = {'arg': cid}
                res = requests.post(f"{self.host}/api/v0/cat", params=params)
                res.raise_for_status()
                return res.json()
            except Exception as e:
                print(f"Failed to fetch from IPFS: {e}")
                return None
        return None
