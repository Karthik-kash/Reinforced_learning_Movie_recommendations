import json
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.auth.password import hash_password


class JsonAuthStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.RLock()
        self.data = self._load()
        self._ensure_demo_user()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"by_email": {}, "by_id": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return {"by_email": data.get("by_email", {}), "by_id": data.get("by_id", {})}
        except (OSError, json.JSONDecodeError):
            return {"by_email": {}, "by_id": {}}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=self.path.parent, suffix=".tmp") as handle:
            json.dump(self.data, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, self.path)

    def _ensure_demo_user(self) -> None:
        if self.get_by_id("guest_user") is None:
            with self._lock:
                self.data["by_id"]["guest_user"] = {
                    "user_id": "guest_user",
                    "email": "demo@movieverse.local",
                    "username": "Demo Viewer",
                    "is_demo": True,
                }
                self.data["by_email"]["demo@movieverse.local"] = self.data["by_id"]["guest_user"]
                self._save()

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        return self.data["by_email"].get(email.strip().lower())

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self.data["by_id"].get(user_id)

    def create_user(self, email: str, username: str, password: str) -> dict[str, Any]:
        normalized_email = email.strip().lower()
        if self.get_by_email(normalized_email):
            raise ValueError("An account with this email already exists")
        user = {
            "user_id": f"usr_{uuid.uuid4().hex[:12]}",
            "email": normalized_email,
            "username": username.strip(),
            "password_hash": hash_password(password),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        }
        with self._lock:
            self.data["by_email"][normalized_email] = user
            self.data["by_id"][user["user_id"]] = user
            self._save()
        return user
