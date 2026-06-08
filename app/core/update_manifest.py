"""Update manifest data model."""
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class UpdateManifest:
    """Represents a structured update manifest from remote."""
    version: str
    package_url: str
    sha256: str
    published_at: str
    notes_url: Optional[str] = None
    signature_algorithm: str = "ed25519"

    @classmethod
    def from_json(cls, json_bytes: bytes) -> 'UpdateManifest':
        """Parse JSON bytes into UpdateManifest."""
        data = json.loads(json_bytes.decode('utf-8'))
        
        # Mandatory fields
        required = ["version", "package_url", "sha256", "published_at"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing mandatory field in manifest: {field}")
        
        return cls(
            version=data["version"],
            package_url=data["package_url"],
            sha256=data["sha256"],
            published_at=data["published_at"],
            notes_url=data.get("notes_url"),
            signature_algorithm=data.get("signature_algorithm", "ed25519")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "package_url": self.package_url,
            "sha256": self.sha256,
            "published_at": self.published_at,
            "notes_url": self.notes_url,
            "signature_algorithm": self.signature_algorithm
        }
