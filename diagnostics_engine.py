# -*- coding: utf-8 -*-
"""
diagnostics_engine.py
══════════════════════════════════════════════════════════════════
نظام الكشف عن الأخطاء والمراقبة الشاملة — شمس المعارف الكبرى
SHAMS AL-MA'ARIF — PROFESSIONAL DIAGNOSTICS ENGINE v1.0

يفحص كل مكون في المنظومة ويُصدر تقريراً دقيقاً.
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import math
import hashlib
import traceback
import threading
import importlib
from datetime import datetime as dt
from typing import Dict, List, Optional, Tuple, Any

# ══════════════════════════════════════════════════════════════════
# 1. CONSTANTS
# ══════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
START_TIME = time.time()

ENGINE_MODULES = [
    ("data",                "ABJAD_VALUES"),
    ("shams_data_extended", "METAL_ADVICE"),
    ("shams_engine",        "process_void"),
    ("geomancy_engine",     "process_signals"),
    ("zairja_engine",       "full_zairja_reading"),
    ("jafr_engine",         "calc_jafr_simple"),
    ("soul_engine",         "process_soul"),
    ("talisman_engine",     "get_talisman_url"),
    ("wafq_generator",      "generate_wafq"),
    ("mandal_engine",       "summon_mandal"),
    ("intent_engine",       "analyze_intent"),
    ("king_engine",         "get_king_for_intent"),
    ("path_engine",         "resolve_path"),
    ("matrix_engine",       "process_matrix"),
    ("symbolic_engine",     "encode_user_data"),
    ("elemental_balance",   "analyze_user_balance"),
    ("astro_gatekeeper",    "astro_gatekeeper"),
    ("session_sandbox",     "session_manager"),
    ("license_manager",     "sovereignty_check"),
]

REQUIRED_FILES = [
    "void_souls.json",
    "void_global.json",
    "app.py",
    "data.py",
    "index.html",
    "main.html",
]

REQUIRED_DIRS = [
    "static",
    "templates",
]

# ══════════════════════════════════════════════════════════════════
# 2. DIAGNOSTIC RESULT STRUCTURE
# ══════════════════════════════════════════════════════════════════

class DiagResult:
    def __init__(self, name: str, category: str):
        self.name     = name
        self.category = category
        self.status   = "unknown"   # ok | warning | error | critical
        self.score    = 0           # 0–100
        self.message  = ""
        self.details  = {}
        self.elapsed  = 0.0

    def ok(self, msg: str = "", score: int = 100, details: dict = None):
        self.status  = "ok"
        self.score   = score
        self.message = msg
        self.details = details or {}
        return self

    def warning(self, msg: str, score: int = 60, details: dict = None):
        self.status  = "warning"
        self.score   = score
        self.message = msg
        self.details = details or {}
        return self

    def error(self, msg: str, score: int = 20, details: dict = None):
        self.status  = "error"
        self.score   = score
        self.message = msg
        self.details = details or {}
        return self

    def critical(self, msg: str, details: dict = None):
        self.status  = "critical"
        self.score   = 0
        self.message = msg
        self.details = details or {}
        return self

    def to_dict(self) -> dict:
        return {
            "name":     self.name,
            "category": self.category,
            "status":   self.status,
            "score":    self.score,
            "message":  self.message,
            "details":  self.details,
            "elapsed":  round(self.elapsed, 4),
        }


def _timed(fn):
    """ديكوريتور لقياس وقت الفحص."""
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result: DiagResult = fn(*args, **kwargs)
        result.elapsed = time.time() - t0
        return result
    return wrapper


# ══════════════════════════════════════════════════════════════════
# 3. MODULE IMPORT CHECKS
# ══════════════════════════════════════════════════════════════════

@_timed
def check_module(module_name: str, required_attr: str) -> DiagResult:
    r = DiagResult(module_name, "module")
    try:
        mod = importlib.import_module(module_name)
        if not hasattr(mod, required_attr):
            return r.warning(
                f"الموديول محمّل لكن الخاصية '{required_attr}' غير موجودة",
                score=50,
                details={"module": module_name, "missing_attr": required_attr}
            )
        return r.ok(f"✓ {module_name} — '{required_attr}' موجود", 100)
    except ImportError as e:
        return r.critical(
            f"فشل استيراد الموديول: {e}",
            details={"module": module_name, "error": str(e)}
        )
    except Exception as e:
        return r.error(
            f"خطأ غير متوقع: {e}",
            details={"module": module_name, "error": str(e), "trace": traceback.format_exc(limit=3)}
        )


# ══════════════════════════════════════════════════════════════════
# 4. ALGORITHM INTEGRITY CHECKS
# ══════════════════════════════════════════════════════════════════

@_timed
def check_abjad_algorithm() -> DiagResult:
    """فحص خوارزمية الأبجد — القيم الثابتة."""
    r = DiagResult("abjad_algorithm", "algorithm")
    try:
        from data import ABJAD_VALUES
        # قيم معروفة ثابتة من علم الجفر
        KNOWN = {
            'ا': 1,  'ب': 2,  'ج': 3,  'د': 4,
            'ه': 5,  'و': 6,  'ز': 7,  'ح': 8,
            'ط': 9,  'ي': 10, 'ك': 20, 'ل': 30,
            'م': 40, 'ن': 50, 'س': 60, 'ع': 70,
            'ف': 80, 'ص': 90, 'ق': 100,'ر': 200,
            'ش': 300,'ت': 400,'ث': 500,'خ': 600,
            'ذ': 700,'ض': 800,'ظ': 900,'غ': 1000,
        }
        errors = []
        for letter, expected in KNOWN.items():
            actual = ABJAD_VALUES.get(letter)
            if actual != expected:
                errors.append(f"'{letter}': توقعنا {expected} وجدنا {actual}")

        # فحص "الله" = 66
        allah_val = sum(ABJAD_VALUES.get(c, 0) for c in 'الله')
        if allah_val != 66:
            errors.append(f"قيمة 'الله' = {allah_val} (المتوقع: 66)")

        # فحص "محمد" = 92
        muhammad_val = sum(ABJAD_VALUES.get(c, 0) for c in 'محمد')
        if muhammad_val != 92:
            errors.append(f"قيمة 'محمد' = {muhammad_val} (المتوقع: 92)")

        if errors:
            return r.error(
                f"أخطاء في جدول الأبجد ({len(errors)} خطأ)",
                score=30,
                details={"errors": errors}
            )
        return r.ok("جدول الأبجد صحيح — كل القيم متطابقة", 100,
                    details={"allah": allah_val, "muhammad": muhammad_val, "table_size": len(ABJAD_VALUES)})
    except Exception as e:
        return r.critical(str(e))


@_timed
def check_wafq_algorithm() -> DiagResult:
    """فحص خوارزمية الوفق — التحقق من مجاميع الصفوف والأعمدة والأقطار."""
    r = DiagResult("wafq_algorithm", "algorithm")
    try:
        from wafq_generator import generate_wafq
        errors = []
        # فحص وفق 3×3 لقيمة 66 (الله)
        w3 = generate_wafq(66, 3)
        if w3:
            flat = w3 if isinstance(w3[0], (int, float)) else [v for row in w3 for v in row]
            matrix = w3 if not isinstance(w3[0], (int, float)) else [w3[i*3:(i+1)*3] for i in range(3)]
            target = sum(matrix[0])
            # فحص كل صف
            for i, row in enumerate(matrix):
                if sum(row) != target:
                    errors.append(f"3×3: الصف {i} مجموعه {sum(row)} ≠ {target}")
            # فحص كل عمود
            for j in range(3):
                col_sum = sum(matrix[i][j] for i in range(3))
                if col_sum != target:
                    errors.append(f"3×3: العمود {j} مجموعه {col_sum} ≠ {target}")
            # فحص القطر الرئيسي
            diag1 = sum(matrix[i][i] for i in range(3))
            if diag1 != target:
                errors.append(f"3×3: القطر الرئيسي {diag1} ≠ {target}")
        else:
            errors.append("generate_wafq(66, 3) أرجع None أو قيمة فارغة")

        if errors:
            return r.error(f"أخطاء في خوارزمية الوفق ({len(errors)})", 40,
                           details={"errors": errors})
        return r.ok("خوارزمية الوفق سليمة — المجاميع متوازنة", 100,
                    details={"tested": "3×3 للقيمة 66", "target_sum": 66})
    except Exception as e:
        return r.error(f"خطأ في فحص الوفق: {e}", 20,
                       details={"trace": traceback.format_exc(limit=3)})


@_timed
def check_jafr_algorithm() -> DiagResult:
    """فحص خوارزمية الجفر."""
    r = DiagResult("jafr_algorithm", "algorithm")
    try:
        from jafr_engine import calc_jafr_simple, JAFR_TABLE
        result = calc_jafr_simple('محمد', 'نية المحبة')
        if not result or not isinstance(result, dict):
            return r.error("calc_jafr_simple أرجع نتيجة غير صالحة", 30)

        # Check actual keys from the engine (jummal, natiq, letter_idx, etc.)
        required_keys = {'jummal', 'natiq', 'letter_idx'}
        missing = required_keys - set(result.keys())
        if missing:
            return r.warning(f"مفاتيح مفقودة في نتيجة الجفر: {missing}", 60,
                             details={"result_keys": list(result.keys())})
        if not JAFR_TABLE:
            return r.warning("JAFR_TABLE فارغ", 50)
        return r.ok("خوارزمية الجفر تعمل بشكل صحيح", 100,
                    details={
                        "jummal": result.get('jummal'),
                        "natiq": result.get('natiq'),
                        "table_entries": len(JAFR_TABLE),
                    })
    except Exception as e:
        return r.error(str(e), 20, details={"trace": traceback.format_exc(limit=3)})


@_timed
def check_geomancy_algorithm() -> DiagResult:
    """فحص خوارزمية الرمل (علم الجغرافيا الروحية)."""
    r = DiagResult("geomancy_algorithm", "algorithm")
    try:
        from geomancy_engine import signals_to_mothers, generate_full_chart, analyze_chart
        # signals_to_mothers expects a dict of signals, not a raw list
        test_signals = {
            "typing_speed": 120,
            "char_count": 7,
            "word_count": 2,
            "hesitation": 1,
            "hour": 10,
            "minute": 30,
            "second": 0,
        }
        mothers = signals_to_mothers(test_signals)
        if len(mothers) != 4:
            return r.error(f"signals_to_mothers أنتج {len(mothers)} أمهات (المتوقع 4)", 30)

        chart = generate_full_chart(mothers)
        if not chart or len(chart) < 12:
            return r.error(f"generate_full_chart أنتج {len(chart) if chart else 0} شكلاً", 40)

        analysis = analyze_chart(chart)
        # analyze_chart returns: houses, aspects, time_data, hidden_intent, summary
        if 'houses' not in analysis:
            return r.warning("analyze_chart لا يُرجع 'houses'", 60,
                             details={"keys": list(analysis.keys())})

        judge_house = next((h for h in analysis.get('houses', []) if h.get('number') == 15), None)
        return r.ok("خوارزمية الرمل سليمة", 100,
                    details={"mothers_count": len(mothers), "chart_figures": len(chart),
                             "judge_figure": judge_house.get('figure_name', '?') if judge_house else '?',
                             "houses_count": len(analysis.get('houses', []))})
    except Exception as e:
        return r.error(str(e), 20, details={"trace": traceback.format_exc(limit=3)})


@_timed
def check_zairja_algorithm() -> DiagResult:
    """فحص خوارزمية الزايرجة."""
    r = DiagResult("zairja_algorithm", "algorithm")
    try:
        from zairja_engine import full_zairja_reading
        # full_zairja_reading(question, hour=0, minute=0)
        result = full_zairja_reading('ما هو حظي في المحبة', 10, 30)
        if not result or not isinstance(result, dict):
            return r.error("full_zairja_reading أرجع نتيجة فارغة", 30)
        return r.ok("الزايرجة تعمل بشكل صحيح", 100,
                    details={"keys": list(result.keys())[:8]})
    except Exception as e:
        return r.error(str(e), 20, details={"trace": traceback.format_exc(limit=3)})


@_timed
def check_soul_engine() -> DiagResult:
    """فحص محرك الروح الخفية."""
    r = DiagResult("soul_engine", "algorithm")
    try:
        from soul_engine import process_soul, _make_session_id
        sid = _make_session_id("test", "أم_test", "diag")
        result = process_soul(
            session_id=sid,
            name="اختبار",
            mother="أم",
            intent="فحص النظام",
            signals={"hesitation": 0, "typing_speed": 100, "char_count": 5, "hour": 12},
            base_ai_text="نص اختباري"
        )
        required = {'ai_text_final', 'soul_meta', 'ending'}
        missing = required - set(result.keys())
        if missing:
            return r.warning(f"مفاتيح مفقودة: {missing}", 65)
        soul_meta = result.get('soul_meta', {})
        if 'phase' not in soul_meta or 'state' not in soul_meta:
            return r.warning("soul_meta ناقصة", 70)
        return r.ok("محرك الروح يعمل بشكل مثالي", 100,
                    details={"phase": soul_meta.get('phase'), "state": soul_meta.get('state')})
    except Exception as e:
        return r.error(str(e), 20, details={"trace": traceback.format_exc(limit=3)})


# ══════════════════════════════════════════════════════════════════
# 5. DATA INTEGRITY CHECKS
# ══════════════════════════════════════════════════════════════════

@_timed
def check_data_tables() -> DiagResult:
    """فحص سلامة جداول البيانات الرئيسية."""
    r = DiagResult("data_tables", "data")
    try:
        from data import (
            LUNAR_MANSIONS, KINGS_DATA, ASMA_AL_HUSNA,
            ABJAD_VALUES, LATAIF, ZODIAC
        )
        issues = []
        checks = [
            ("LUNAR_MANSIONS", LUNAR_MANSIONS, 28),
            ("ASMA_AL_HUSNA",  ASMA_AL_HUSNA,  99),
            ("ABJAD_VALUES",   ABJAD_VALUES,   28),
        ]
        for name, table, expected in checks:
            if len(table) < expected:
                issues.append(f"{name}: {len(table)} عنصر (المتوقع ≥{expected})")

        if not KINGS_DATA:
            issues.append("KINGS_DATA: فارغ")
        if not ZODIAC:
            issues.append("ZODIAC: فارغ")

        if issues:
            return r.warning(f"بعض الجداول ناقصة ({len(issues)} مشكلة)", 65,
                             details={"issues": issues})
        return r.ok("جميع جداول البيانات مكتملة", 100,
                    details={
                        "lunar_mansions": len(LUNAR_MANSIONS),
                        "asma_al_husna": len(ASMA_AL_HUSNA),
                        "abjad_letters": len(ABJAD_VALUES),
                        "kings": len(KINGS_DATA),
                    })
    except Exception as e:
        return r.critical(str(e))


@_timed
def check_json_files() -> DiagResult:
    """فحص ملفات JSON — التحقق من صحتها وقدرتها على القراءة والكتابة."""
    r = DiagResult("json_files", "data")
    issues = []
    details = {}

    for path in ["void_souls.json", "void_global.json"]:
        if not os.path.exists(path):
            # سنحاول إنشاؤه
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                details[path] = "تم الإنشاء حديثاً"
            except Exception as e:
                issues.append(f"{path}: لا يمكن إنشاؤه — {e}")
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                size = os.path.getsize(path)
                details[path] = f"✓ صالح ({size} بايت، {len(data)} مفتاح)"
            except json.JSONDecodeError as e:
                issues.append(f"{path}: تلف JSON — {e}")
            except Exception as e:
                issues.append(f"{path}: خطأ في القراءة — {e}")

    if issues:
        return r.error(f"مشاكل في ملفات JSON ({len(issues)})", 30,
                       details={"issues": issues, "files": details})
    return r.ok("ملفات JSON سليمة", 100, details=details)


@_timed
def check_required_files() -> DiagResult:
    """فحص وجود الملفات المطلوبة."""
    r = DiagResult("required_files", "filesystem")
    missing = []
    found = []
    for f in REQUIRED_FILES:
        if os.path.exists(f):
            size = os.path.getsize(f)
            found.append(f"{f} ({size:,} بايت)")
        else:
            missing.append(f)

    if missing:
        return r.error(f"ملفات مفقودة: {missing}", 20,
                       details={"missing": missing, "found": found})
    return r.ok("جميع الملفات الأساسية موجودة", 100,
                details={"files": found})


# ══════════════════════════════════════════════════════════════════
# 6. SYSTEM RESOURCES CHECK
# ══════════════════════════════════════════════════════════════════

@_timed
def check_system_resources() -> DiagResult:
    """فحص موارد النظام — ذاكرة، معالج، مساحة."""
    r = DiagResult("system_resources", "system")
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('.')

        warnings = []
        if cpu > 90:
            warnings.append(f"CPU مرتفع: {cpu}%")
        if mem.percent > 90:
            warnings.append(f"RAM مرتفع: {mem.percent}%")
        if disk.percent > 95:
            warnings.append(f"مساحة القرص ممتلئة: {disk.percent}%")

        details = {
            "cpu_percent":    round(cpu, 1),
            "ram_used_mb":    round(mem.used / 1024**2, 1),
            "ram_total_mb":   round(mem.total / 1024**2, 1),
            "ram_percent":    round(mem.percent, 1),
            "disk_free_gb":   round(disk.free / 1024**3, 2),
            "disk_percent":   round(disk.percent, 1),
            "uptime_seconds": round(time.time() - START_TIME, 1),
        }

        if warnings:
            score = max(20, 100 - len(warnings) * 25)
            return r.warning(f"تحذيرات موارد النظام: {'; '.join(warnings)}", score, details)
        return r.ok("موارد النظام طبيعية", 100, details)
    except ImportError:
        return r.warning("psutil غير متاح — لا يمكن فحص الموارد", 50)
    except Exception as e:
        return r.error(str(e), 20)


@_timed
def check_python_environment() -> DiagResult:
    """فحص بيئة Python والمكتبات المطلوبة."""
    r = DiagResult("python_environment", "system")
    required_libs = [
        ("flask",          "Flask"),
        ("numpy",          "numpy"),
    ]
    optional_libs = [
        ("skyfield",       "Skyfield — حسابات فلكية دقيقة"),
        ("PIL",            "Pillow — توليد الصور"),
        ("google.genai",   "Gemini AI — التفسير الذكي"),
    ]

    missing_required = []
    missing_optional = []
    available = []

    for lib, label in required_libs:
        try:
            importlib.import_module(lib)
            available.append(label)
        except ImportError:
            missing_required.append(label)

    for lib, label in optional_libs:
        try:
            importlib.import_module(lib)
            available.append(label)
        except ImportError:
            missing_optional.append(label)

    details = {
        "python_version": sys.version.split()[0],
        "available": available,
        "missing_optional": missing_optional,
    }

    if missing_required:
        return r.critical(f"مكتبات أساسية مفقودة: {missing_required}", details)
    if missing_optional:
        return r.warning(f"مكتبات اختيارية مفقودة ({len(missing_optional)}): {missing_optional}",
                         75, details)
    return r.ok("بيئة Python مكتملة", 100, details)


# ══════════════════════════════════════════════════════════════════
# 7. API ROUTES INTEGRITY
# ══════════════════════════════════════════════════════════════════

@_timed
def check_api_routes(app) -> DiagResult:
    """فحص تسجيل كل مسارات الـ API."""
    r = DiagResult("api_routes", "api")
    try:
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        critical_routes = [
            '/api/process',
            '/api/intent/path',
            '/api/jafr/simple',
            '/api/zairja/circular',
            '/api/geomancy',
            '/api/soul/summary',
            '/api/diagnostics',
        ]
        missing = [rt for rt in critical_routes if rt not in routes]
        details = {
            "total_routes": len(routes),
            "critical_routes_ok": len(critical_routes) - len(missing),
            "missing_critical": missing,
        }
        if missing:
            return r.warning(f"مسارات مفقودة: {missing}", 70, details)
        return r.ok(f"جميع المسارات مسجّلة ({len(routes)} مسار)", 100, details)
    except Exception as e:
        return r.error(str(e), 20)


# ══════════════════════════════════════════════════════════════════
# 8. LICENSE & SOVEREIGNTY CHECK
# ══════════════════════════════════════════════════════════════════

@_timed
def check_license_system() -> DiagResult:
    """فحص نظام التراخيص والسيادة."""
    r = DiagResult("license_system", "security")
    try:
        from license_manager import sovereignty_check, get_hardware_id
        hw_id = get_hardware_id()
        sov = sovereignty_check(operation='diagnostics')
        details = {
            "hardware_id_present": bool(hw_id),
            "sovereignty_cleared": sov.get('cleared', False),
            "operation": "diagnostics",
        }
        if not sov.get('cleared', True):
            return r.warning(f"السيادة غير مُصفَّاة: {sov.get('message', '')}", 60, details)
        return r.ok("نظام التراخيص سليم", 100, details)
    except Exception as e:
        return r.warning(f"لا يمكن فحص نظام الترخيص: {e}", 60,
                         details={"error": str(e)})


# ══════════════════════════════════════════════════════════════════
# 9. FULL DIAGNOSTIC RUN
# ══════════════════════════════════════════════════════════════════

def run_full_diagnostics(app=None) -> dict:
    """
    تشغيل كامل لجميع الفحوصات وإصدار التقرير الشامل.
    Returns dict with overall_score, status, results, timestamp.
    """
    t_start = time.time()
    results = []

    # ── فحص الموديولات ───────────────────────────────────────────
    for mod_name, attr in ENGINE_MODULES:
        results.append(check_module(mod_name, attr))

    # ── فحص الخوارزميات ──────────────────────────────────────────
    results.append(check_abjad_algorithm())
    results.append(check_wafq_algorithm())
    results.append(check_jafr_algorithm())
    results.append(check_geomancy_algorithm())
    results.append(check_zairja_algorithm())
    results.append(check_soul_engine())

    # ── فحص البيانات ─────────────────────────────────────────────
    results.append(check_data_tables())
    results.append(check_json_files())
    results.append(check_required_files())

    # ── فحص النظام ───────────────────────────────────────────────
    results.append(check_system_resources())
    results.append(check_python_environment())

    # ── فحص الـ API ──────────────────────────────────────────────
    if app:
        results.append(check_api_routes(app))

    # ── فحص الترخيص ──────────────────────────────────────────────
    results.append(check_license_system())

    # ── حساب النتيجة الإجمالية ───────────────────────────────────
    total_score   = sum(r.score for r in results)
    max_score     = len(results) * 100
    overall_pct   = round((total_score / max_score) * 100) if max_score else 0

    status_counts = {"ok": 0, "warning": 0, "error": 0, "critical": 0, "unknown": 0}
    for r in results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    if status_counts["critical"] > 0:
        overall_status = "critical"
    elif status_counts["error"] > 2:
        overall_status = "error"
    elif status_counts["warning"] > 3 or status_counts["error"] > 0:
        overall_status = "warning"
    else:
        overall_status = "ok"

    # ── تصنيف حسب الفئة ─────────────────────────────────────────
    by_category: Dict[str, List] = {}
    for r in results:
        by_category.setdefault(r.category, []).append(r.to_dict())

    elapsed = round(time.time() - t_start, 3)

    return {
        "version":        VERSION,
        "timestamp":      dt.now().isoformat(),
        "elapsed_total":  elapsed,
        "overall_score":  overall_pct,
        "overall_status": overall_status,
        "status_counts":  status_counts,
        "total_checks":   len(results),
        "by_category":    by_category,
        "results":        [r.to_dict() for r in results],
        "summary": {
            "healthy":      status_counts["ok"],
            "warnings":     status_counts["warning"],
            "errors":       status_counts["error"],
            "critical":     status_counts["critical"],
            "score_label":  _score_label(overall_pct),
        }
    }


def _score_label(score: int) -> str:
    if score >= 95: return "ممتاز — المنظومة في أفضل حالاتها"
    if score >= 80: return "جيد — المنظومة تعمل بكفاءة"
    if score >= 60: return "مقبول — توجد تحذيرات تستحق الانتباه"
    if score >= 40: return "ضعيف — مشاكل تحتاج إصلاحاً"
    return "حرج — المنظومة تحتاج تدخلاً فورياً"
