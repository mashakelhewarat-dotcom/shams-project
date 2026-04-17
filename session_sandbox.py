# -*- coding: utf-8 -*-
"""
session_sandbox.py — نظام العزل والحماية (Sandbox & Kill-Switch)
═══════════════════════════════════════════════════════════════════
كل جلسة معزولة — المستخدم لا يستطيع تغيير مساره بعد الدخول.
زر "أمر الإصراف" يمسح الجلسة ويمنع أي طلب جديد منها.
═══════════════════════════════════════════════════════════════════
"""

import uuid
import time
from typing import Dict, Optional

# ============================================================================
# كلاس الجلسة
# ============================================================================

class RitualSession:
    """جلسة عمل معزولة."""

    def __init__(self, session_id: str, user_name: str, mother_name: str,
                 intent: str = '', path: str = ''):
        self.session_id    = session_id
        self.user_name     = user_name
        self.mother_name   = mother_name
        self.intent        = intent         # النية — مقفولة بعد البدء
        self.path          = path           # المسار — مقفول بعد البدء
        self.created_at    = time.time()
        self.last_activity = time.time()
        self.is_active     = True
        self.data: Dict    = {}

    def terminate(self, reason: str = 'user_request'):
        """أمر الإصراف — ينهي الجلسة ويمسح بياناتها."""
        self.is_active = False
        self.data.clear()
        self.termination_reason = reason

    def touch(self):
        self.last_activity = time.time()

    def to_dict(self) -> Dict:
        return {
            'session_id':    self.session_id,
            'user_name':     self.user_name,
            'intent':        self.intent,
            'path':          self.path,
            'created_at':    self.created_at,
            'last_activity': self.last_activity,
            'is_active':     self.is_active,
            'age_seconds':   round(time.time() - self.created_at),
        }

# ============================================================================
# مدير الجلسات
# ============================================================================

class SessionManager:
    """يُدير جميع الجلسات النشطة."""

    def __init__(self, timeout_seconds: int = 3600):
        self.sessions: Dict[str, RitualSession] = {}
        self.timeout = timeout_seconds

    def create_session(self, user_name: str, mother_name: str,
                       intent: str = '', path: str = '') -> str:
        session_id = str(uuid.uuid4())[:8].upper()
        self.sessions[session_id] = RitualSession(
            session_id, user_name, mother_name, intent, path
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[RitualSession]:
        s = self.sessions.get(session_id)
        if not s:
            return None
        if not s.is_active:
            return None
        if time.time() - s.last_activity > self.timeout:
            self.kill_session(session_id, reason='timeout')
            return None
        s.touch()
        return s

    def kill_session(self, session_id: str, reason: str = 'user_request'):
        """أمر الإصراف الرقمي."""
        s = self.sessions.get(session_id)
        if s:
            s.terminate(reason)
            del self.sessions[session_id]

    def cleanup_expired(self):
        expired = [
            sid for sid, s in self.sessions.items()
            if time.time() - s.last_activity > self.timeout
        ]
        for sid in expired:
            self.kill_session(sid, reason='timeout')

    def active_count(self) -> int:
        return sum(1 for s in self.sessions.values() if s.is_active)


# مثيل عالمي — يُستخدم في app.py
session_manager = SessionManager(timeout_seconds=3600)


if __name__ == "__main__":
    sm = SessionManager()
    sid = sm.create_session("محمد", "فاطمة", "attraction", "influence")
    print(f"Session created: {sid}")
    s = sm.get_session(sid)
    print(f"Active: {s.is_active}  intent={s.intent}")
    sm.kill_session(sid)
    print(f"After kill: {sm.get_session(sid)}")
