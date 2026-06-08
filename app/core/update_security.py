"""Security helpers for update verification."""
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature


# Public key for Ed25519 signature verification.
PUBLIC_KEY_HEX = "9ff92d0fe50ea7d754dc3707a129e55cafa46578f9cf2dd8e9bc612787465ac3"


def sha256_file(path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        # Read in 4KB chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_sha256(path: str, expected_hash: str) -> bool:
    """Verify file hash against expected SHA-256."""
    actual_hash = sha256_file(path)
    return actual_hash.lower() == expected_hash.lower()


def verify_manifest_signature(manifest_bytes: bytes, signature_bytes: bytes, public_key_hex: str = PUBLIC_KEY_HEX) -> bool:
    """Verify Ed25519 signature of manifest bytes."""
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        public_key.verify(signature_bytes, manifest_bytes)
        return True
    except (InvalidSignature, ValueError):
        return False
