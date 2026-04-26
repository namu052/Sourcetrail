"""Phase 0 sample project used by PoC 1 and smoke tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass(slots=True)
class Session:
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_active: datetime = field(default_factory=lambda: datetime.now(UTC))
    timeout_seconds: int = 1800

    def touch(self) -> None:
        self.last_active = datetime.now(UTC)

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return current - self.last_active > timedelta(seconds=self.timeout_seconds)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(self, user_id: str) -> Session:
        session = Session(user_id=user_id)
        self._sessions[user_id] = session
        return session

    def get_session(self, user_id: str) -> Session | None:
        session = self._sessions.get(user_id)
        if session is not None:
            session.touch()
        return session

    def cleanup_expired(self) -> list[str]:
        expired_users: list[str] = []
        for user_id, session in list(self._sessions.items()):
            if session.is_expired():
                expired_users.append(user_id)
                del self._sessions[user_id]

        if expired_users:
            missing_cleanup_handler(expired_users)  # noqa: F821
        return expired_users


def count_active_sessions(manager: SessionManager) -> int:
    return len(manager._sessions)


def build_demo_manager() -> SessionManager:
    manager = SessionManager()
    manager.create_session("alice")
    manager.create_session("bob")
    return manager
