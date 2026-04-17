# -*- coding: utf-8 -*-
"""
logger_system.py — شمس المعارف الكبرى v17 PRODUCTION
══════════════════════════════════════════════════════════════════
نظام السجلات الاحترافي — Thread-Safe بالكامل

✅ FIX (v10/v12): _id_counter منفصل عن _counters
   — يضمن ID فريداً حتى بعد clear_logs()
   — في v10/v12 كان 'id' = _counters['total'] + 1
     وبعد clear() يعود إلى 1 مما يُكرر IDs
✅ FIX: entry تُبنى داخل _lock لضمان الاتساق
✅ FIX: clear_logs لا تصفّر _id_counter (الفرادة مضمونة)
✅ إضافة: level_filter يدعم string فارغ كـ 'ALL'
✅ إضافة: Type hints كاملة
══════════════════════════════════════════════════════════════════
"""

import time
import threading
from datetime import datetime, timezone
from collections import deque
from typing import Optional, List, Dict

# ── إعدادات النظام ─────────────────────────────────────────────
MAX_LOGS   = 2000   # أقصى عدد سجلات في الذاكرة
DEBUG_MODE = False  # قابل للتبديل عبر /api/logs/debug

# ── تصنيفات السجلات ─────────────────────────────────────────────
LEVELS: Dict[str, int] = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
LEVEL_COLORS: Dict[str, str] = {
    'DEBUG':   '#00bcd4',
    'INFO':    '#4caf50',
    'WARNING': '#ff9800',
    'ERROR':   '#f44336',
}

# ── مخزن السجلات في الذاكرة ─────────────────────────────────────
_logs: deque = deque(maxlen=MAX_LOGS)
_lock = threading.Lock()
_counters: Dict[str, int] = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'total': 0}

# ✅ FIX الجوهري: counter منفصل يضمن ID فريداً حتى بعد clear_logs()
# في v10 و v12: id = _counters['total'] + 1 — بعد clear() يعود إلى 1 → IDs مكررة
# في v17: _id_counter يتزايد فقط ولا يُصفَّر أبداً
_id_counter: int = 0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def log(level: str, location: str, message: str, extra: Optional[dict] = None) -> None:
    """تسجيل حدث جديد — thread-safe بالكامل"""
    global _id_counter
    level = level.upper()
    if level not in LEVELS:
        level = 'INFO'
    if level == 'DEBUG' and not DEBUG_MODE:
        return

    with _lock:
        # ✅ بناء entry كاملاً داخل القفل لضمان الاتساق
        _id_counter += 1
        entry: dict = {
            'id':        _id_counter,
            'timestamp': _now_iso(),
            'level':     level,
            'color':     LEVEL_COLORS.get(level, '#ffffff'),
            'location':  location,
            'message':   message,
            'extra':     extra or {},
        }
        _logs.append(entry)
        _counters[level] = _counters.get(level, 0) + 1
        _counters['total'] += 1


def get_logs(
    level_filter: Optional[str] = None,
    search: Optional[str] = None,
    since_id: int = 0,
    limit: int = 200,
) -> List[dict]:
    """جلب السجلات مع فلترة وبحث — thread-safe"""
    with _lock:
        entries = list(_logs)

    if since_id:
        entries = [e for e in entries if e['id'] > since_id]

    # ✅ FIX: يدعم string فارغ '' كـ 'ALL' (لم يكن محسوباً في v10)
    if level_filter and level_filter.upper() not in ('ALL', ''):
        entries = [e for e in entries if e['level'] == level_filter.upper()]

    if search:
        s = search.lower()
        entries = [
            e for e in entries
            if s in e['message'].lower() or s in e['location'].lower()
        ]

    return entries[-limit:]


def get_stats() -> Dict[str, int]:
    """إحصائيات السجلات — thread-safe"""
    with _lock:
        return dict(_counters)


def set_debug_mode(enabled: bool) -> None:
    global DEBUG_MODE
    DEBUG_MODE = bool(enabled)


def clear_logs() -> None:
    """
    مسح السجلات — يصفّر _counters فقط.
    ✅ لا يُصفّر _id_counter لضمان فرادة IDs بعد المسح.
    """
    with _lock:
        _logs.clear()
        for k in list(_counters.keys()):
            _counters[k] = 0


# ── Decorator لتتبع دوال API ────────────────────────────────────
def trace(func_name: Optional[str] = None):
    """Decorator يسجل دخول ومخرجات الدالة — مفيد للـ debugging"""
    def decorator(fn):
        import functools

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            fname = func_name or fn.__name__
            t0 = time.perf_counter()
            log('DEBUG', fname, f'▶ استدعاء {fname}', {'args_count': len(args)})
            try:
                result  = fn(*args, **kwargs)
                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                log('DEBUG', fname, f'✅ اكتمل في {elapsed}ms')
                return result
            except Exception as e:
                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                log('ERROR', fname, f'❌ خطأ بعد {elapsed}ms: {e}')
                raise

        return wrapper
    return decorator


# سجّل بداية النظام
log('INFO', 'logger_system', f'🚀 نظام السجلات v17 تم تشغيله — MAX_LOGS={MAX_LOGS}')
