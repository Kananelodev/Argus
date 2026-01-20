import base64
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

class DIDManager:
    def __init__(self, key_path: str = "sentinel_key.pem"):
        self.key_path = Path(key_path)
        self.private_key, self.public_key = self._load_or_generate_keys()
        self.did = self._derive_did()

    def _load_or_generate_keys(self) -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
        if self.key_path.exists():
            with open(self.key_path, "rb") as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
                return private_key, private_key.public_key()
        
        # Generate new Ed25519 key (fast, secure, standard for DIDs)
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Save to disk (In prod, use HSM/Vault)
        with open(self.key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        return private_key, private_key.public_key()

    def _derive_did(self) -> str:
        """
        Derives a did:key method identifier from the public key.
        This provides a self-certifying identifier without a blockchain registry.
        """
        # Get raw bytes
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        # Multicodec prefix for Ed25519-pub is 0xed01
        # We simulate a did:key construction here for the hackathon
        # Real did:key requires multibase encoding (base58btc)
        # For simplicity/readability, we use hex
        did_fingerprint = pub_bytes.hex()
        return f"did:key:z{did_fingerprint}"

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Signs a JSON payload and returns the signature as a hex string.
        """
        # Canonicalize JSON
        message = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = self.private_key.sign(message)
        return signature.hex()

    def get_verification_method(self) -> str:
        return f"{self.did}#keys-1"
