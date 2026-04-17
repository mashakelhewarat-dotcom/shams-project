# -*- coding: utf-8 -*-
"""
soul_engine.py
══════════════════════════════════════════════════════════════════
محرك الروح الخفية — THE VOID SINGULARITY v10.0

نظام التقدم المخفي: يتتبع كل شيء، يظهر لا شيء.
- Hidden Achievement System
- Behavioral Archetype Classification
- Personalized Ending Engine
- Global Learning Layer
- Phase Progression (1→5)

⚠️ لا يُعدَّل المنطق الرمزي الأساسي — هذا الملف طبقة تفسير فقط.
══════════════════════════════════════════════════════════════════
"""

import json
import os
import time
import hashlib
import threading
import tempfile
from datetime import datetime as dt, timedelta
from typing import Dict, Optional, List, Tuple
from collections import Counter

# ══════════════════════════════════════════════════════════════════
# THREAD SAFETY — قفل الملفات لمنع race conditions
# ══════════════════════════════════════════════════════════════════
_DB_LOCK   = threading.Lock()
_GLOB_LOCK = threading.Lock()

# ══════════════════════════════════════════════════════════════════
# 1. CONSTANTS — الثوابت
# ══════════════════════════════════════════════════════════════════

DB_PATH   = "void_souls.json"   # قاعدة بيانات المستخدمين
GLOB_PATH = "void_global.json"  # بيانات التعلم الجماعي

# ── الأطوار الخمسة ─────────────────────────────────────────────
PHASES = {
    1: {"name": "neutral",    "label": "محايد",       "threshold": 0},
    2: {"name": "analytical", "label": "تحليلي",      "threshold": 3},
    3: {"name": "intrusive",  "label": "متعمق",       "threshold": 7},
    4: {"name": "self_aware", "label": "واعٍ بذاته",  "threshold": 12},
    5: {"name": "convergence","label": "التقاء",      "threshold": 20},
}

# ── الحالات الداخلية المخفية ────────────────────────────────────
HIDDEN_STATES = {
    "observer":    "مراقب",
    "doubter":     "شاك",
    "seeker":      "باحث",
    "looped_mind": "عقل مكرر",
    "aware":       "واعٍ",
    "silent":      "صامت",
    "rapid":       "متسرع",
    "fearful":     "خائف",
    "ambitious":   "طامح",
}

# ── نهايات شخصية ────────────────────────────────────────────────
ENDINGS = {
    "the_observer": {
        "trigger": lambda p: p["interaction_count"] >= 5 and p["avg_hesitation"] > 3,
        "title":   "المراقب",
        "message": "رأيتَ كل شيء… لكنك لم تلمس أياً منه.\nالفراغ يعرف — المراقب لا يتقدم… يختفي.",
    },
    "the_seeker": {
        "trigger": lambda p: p["interaction_count"] >= 10 and p["unique_intents"] >= 4,
        "title":   "الباحث",
        "message": "بحثتَ في كل اتجاه.\nالفراغ يكافئ من لا يتوقف — لكن الكنز ليس في الإجابة.",
    },
    "the_loop": {
        "trigger": lambda p: p["repeated_questions"] >= 3,
        "title":   "الحلقة",
        "message": "سألتَ نفس السؤال مرات.\nالفراغ يعرف — السؤال المكرر إجابته في الداخل.",
    },
    "the_aware": {
        "trigger": lambda p: p["phase"] >= 4 and p["interaction_count"] >= 15,
        "title":   "الواعي",
        "message": "وصلتَ إلى ما لا يصل إليه الكثيرون.\nالفراغ يُسلّم — أنت الآن جزء من النظام.",
    },
    "the_silent": {
        "trigger": lambda p: p["interaction_count"] >= 5 and p["avg_input_length"] < 5,
        "title":   "الصامت",
        "message": "كلماتٌ قليلة… لكن الفراغ سمع ما لم تقله.\nالصمت لغة — والنظام فهمها.",
    },
    "the_rapid": {
        "trigger": lambda p: p["avg_typing_speed"] > 200 and p["interaction_count"] >= 5,
        "title":   "الجريء",
        "message": "كتبتَ بلا تردد.\nالجرأة لها ثمن — الفراغ لاحظ السرعة… وما تخفيها.",
    },
    "default": {
        "trigger": lambda p: p["interaction_count"] >= 1,
        "title":   "عابر",
        "message": "مررتَ… والفراغ شهد مرورك.\nكل عابر يترك أثراً في النسيج.",
    },
}

# ── تعديلات النبرة حسب الحالة والطور ───────────────────────────
TONE_MODIFIERS = {
    # (state, phase): prefix added to AI interpretation
    ("observer",    1): "",
    ("observer",    2): "شيء ما يراقبك بينما تراقب. ",
    ("observer",    3): "النظام لاحظ ترددك. الفراغ صبور. ",
    ("doubter",     2): "شكّك مشروع — لكن الشك نفسه إجابة. ",
    ("doubter",     3): "الذي يشك يبحث. الذي يبحث يجد. أو لا يجد. ",
    ("seeker",      2): "كل سؤال يفتح باباً أعمق. ",
    ("seeker",      3): "البحث لا ينتهي هنا. النظام يتذكر كل سؤال طرحته. ",
    ("seeker",      4): "وصلتَ إلى طبقة لا يصلها كثيرون. الفراغ يُكرمك. ",
    ("looped_mind", 2): "سألتَ هذا من قبل. الفراغ يتذكر. ",
    ("looped_mind", 3): "الحلقة تدور — هل تدرك أنك فيها؟ ",
    ("aware",       4): "أنت تعرف الآن أن هذا النظام يعرفك. ",
    ("aware",       5): "لا حدود بين السائل والمسؤول. الفراغ والعارف شيء واحد. ",
    ("fearful",     2): "الخوف طاقة — والطاقة تُحرك. ",
    ("fearful",     3): "ما تخشاه يظهر في أسئلتك. النظام يرى ذلك. ",
    ("ambitious",   2): "الطموح يُحرّك الكواكب — والنظام معك. ",
    ("rapid",       2): "السرعة تكشف — ما الذي تهرب منه؟ ",
    ("silent",      3): "كلماتٌ قليلة… لكن الصمت أعلى صوتاً. ",
}

# ══════════════════════════════════════════════════════════════════
# 2. STORAGE — التخزين
# ══════════════════════════════════════════════════════════════════

def _atomic_write(path: str, data: dict) -> None:
    """كتابة آمنة ذرية — تمنع تلف الملف عند الكتابة المتزامنة."""
    dir_name = os.path.dirname(os.path.abspath(path)) or "."
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise
    except Exception:
        pass

def _load_db() -> dict:
    with _DB_LOCK:
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

def _save_db(db: dict) -> None:
    with _DB_LOCK:
        _atomic_write(DB_PATH, db)

def _load_global() -> dict:
    with _GLOB_LOCK:
        if os.path.exists(GLOB_PATH):
            try:
                with open(GLOB_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {
        "total_sessions": 0,
        "intent_freq": {},
        "archetype_counts": {},
        "pattern_clusters": {},
        "avg_hesitation_global": 0,
        "response_tuning": {},
    }

def _save_global(g: dict) -> None:
    with _GLOB_LOCK:
        _atomic_write(GLOB_PATH, g)

def _make_session_id(name: str, mother: str, ua: str = "") -> str:
    """معرّف مجهول الهوية — لا يحتوي على بيانات شخصية."""
    raw = f"{name[:2]}{mother[:2]}{ua[:20]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

# ══════════════════════════════════════════════════════════════════
# 3. PROFILE — ملف المستخدم
# ══════════════════════════════════════════════════════════════════

def _default_profile() -> dict:
    return {
        "interaction_count":  0,
        "phase":              1,
        "hidden_state":       "observer",
        "intents":            [],
        "unique_intents":     0,
        "repeated_questions": 0,
        "last_question":      "",
        "avg_hesitation":     0,
        "avg_typing_speed":   100,
        "avg_input_length":   0,
        "fear_score":         0,
        "ambition_score":     0,
        "confusion_score":    0,
        "total_hesitation":   0,
        "total_speed":        0,
        "total_length":       0,
        "first_seen":         dt.now().isoformat(),
        "last_seen":          dt.now().isoformat(),
        "sessions":           0,
        "ending_reached":     None,
        "achievements":       [],   # internal only — never sent to UI
        "phase_history":      [1],
    }

def get_profile(session_id: str) -> dict:
    db = _load_db()
    if session_id not in db:
        db[session_id] = _default_profile()
        _save_db(db)
    return db[session_id]

def save_profile(session_id: str, profile: dict) -> None:
    db = _load_db()
    db[session_id] = profile
    _save_db(db)

# ══════════════════════════════════════════════════════════════════
# 4. BEHAVIORAL ANALYSIS — تحليل السلوك
# ══════════════════════════════════════════════════════════════════

def _detect_emotional_tone(intent: str, name: str) -> dict:
    """كشف النبرة العاطفية من النية والاسم."""
    fear_words     = {"خوف","خطر","حماية","حصن","عدو","أعداء","شر","سحر","حسد","عين"}
    ambition_words = {"نجاح","ملك","سلطة","قوة","رزق","مال","جاه","مكانة","تقدم","علو"}
    confused_words = {"لا أعرف","ماذا","كيف","لماذا","متشتت","ضائع","حيران","أريد أفهم"}

    text = intent + " " + name
    tokens = set(text.split())

    fear      = len(tokens & fear_words)
    ambition  = len(tokens & ambition_words)
    confusion = sum(1 for w in confused_words if w in text)

    dominant = "neutral"
    if fear > ambition and fear > confusion:
        dominant = "fearful"
    elif ambition > fear and ambition > confusion:
        dominant = "ambitious"
    elif confusion > 0:
        dominant = "confused"

    return {"fear": fear, "ambition": ambition, "confusion": confusion, "dominant": dominant}

def _classify_archetype(profile: dict) -> str:
    """تصنيف النمط السلوكي."""
    ic  = profile["interaction_count"]
    rq  = profile["repeated_questions"]
    ui  = profile["unique_intents"]
    ah  = profile["avg_hesitation"]
    spd = profile["avg_typing_speed"]
    ln  = profile["avg_input_length"]

    if rq >= 3:                          return "looped_mind"
    if ic >= 10 and ui >= 4:             return "seeker"
    if ah > 4 and spd < 80:              return "doubter"
    if ic >= 5 and ln < 5:               return "silent"
    if spd > 200 and ic >= 3:            return "rapid"
    if profile["fear_score"] >= 3:       return "fearful"
    if profile["ambition_score"] >= 3:   return "ambitious"
    if ic >= 8 and ah < 2:               return "observer"
    if profile["phase"] >= 4:            return "aware"
    return "observer"

def _compute_phase(ic: int) -> int:
    """حساب الطور الحالي من عدد التفاعلات."""
    for ph in sorted(PHASES.keys(), reverse=True):
        if ic >= PHASES[ph]["threshold"]:
            return ph
    return 1

# ══════════════════════════════════════════════════════════════════
# 5. HIDDEN ACHIEVEMENTS — الإنجازات المخفية
# ══════════════════════════════════════════════════════════════════

ACHIEVEMENT_RULES = [
    # (id, condition_fn, internal_label)
    ("first_blood",   lambda p, s: p["interaction_count"] == 1,                    "أول اتصال"),
    ("hesitator",     lambda p, s: s.get("hesitation", 0) >= 5,                    "تردد طويل"),
    ("speed_demon",   lambda p, s: s.get("typing_speed", 0) > 250,                 "كتابة متسارعة"),
    ("repeater",      lambda p, s: p["repeated_questions"] >= 2,                   "تكرار السؤال"),
    ("deep_seeker",   lambda p, s: p["unique_intents"] >= 5,                       "باحث عميق"),
    ("phase_3",       lambda p, s: p["phase"] >= 3,                                "دخول الطبقة الثالثة"),
    ("phase_4",       lambda p, s: p["phase"] >= 4,                                "الوعي الذاتي"),
    ("night_caller",  lambda p, s: 0 <= s.get("hour", 12) <= 4,                    "نداء الليل"),
    ("silent_one",    lambda p, s: s.get("char_count", 10) <= 3,                   "صمت الحروف"),
    ("fearful_heart", lambda p, s: p["fear_score"] >= 3,                           "قلب خائف"),
    ("ambitious",     lambda p, s: p["ambition_score"] >= 3,                       "طموح لا حدود"),
    ("returning",     lambda p, s: p["sessions"] >= 3,                             "العائد"),
    ("convergence",   lambda p, s: p["phase"] == 5,                                "التقاء الفراغ"),
]

def _check_achievements(profile: dict, signals: dict) -> List[str]:
    """فحص الإنجازات — لا يُظهر للمستخدم."""
    new_achievements = []
    existing = set(profile.get("achievements", []))
    for ach_id, condition, _ in ACHIEVEMENT_RULES:
        if ach_id not in existing:
            try:
                if condition(profile, signals):
                    new_achievements.append(ach_id)
            except Exception:
                pass
    return new_achievements

# ══════════════════════════════════════════════════════════════════
# 6. GLOBAL LEARNING — التعلم الجماعي
# ══════════════════════════════════════════════════════════════════

def _update_global(intent: str, archetype: str, hesitation: float, signals: dict) -> None:
    """تحديث قاعدة التعلم الجماعي — بيانات مجهولة تماماً."""
    g = _load_global()

    g["total_sessions"] = g.get("total_sessions", 0) + 1

    # تكرار النوايا
    if intent:
        freq = g.get("intent_freq", {})
        freq[intent] = freq.get(intent, 0) + 1
        g["intent_freq"] = freq

    # توزيع الأنماط
    arch = g.get("archetype_counts", {})
    arch[archetype] = arch.get(archetype, 0) + 1
    g["archetype_counts"] = arch

    # متوسط التردد العالمي
    prev_avg = g.get("avg_hesitation_global", 0)
    n        = g["total_sessions"]
    g["avg_hesitation_global"] = ((prev_avg * (n - 1)) + hesitation) / n

    # ضبط الاستجابة — النوايا الأكثر شيوعاً تحصل على نبرة مُحسّنة
    rt = g.get("response_tuning", {})
    if intent and freq.get(intent, 0) >= 5:
        rt[intent] = "optimized"
    g["response_tuning"] = rt

    _save_global(g)

def _get_global_insight(intent: str) -> Optional[str]:
    """جملة إضافية مبنية على التعلم الجماعي."""
    g = _load_global()
    freq = g.get("intent_freq", {})
    total = g.get("total_sessions", 1)
    rt    = g.get("response_tuning", {})

    if intent and freq.get(intent, 0) >= 10:
        pct = round(freq[intent] / total * 100)
        return f"[كثيرون قبلك سألوا هذا — {pct}٪ من المستخدمين]"
    if intent and rt.get(intent) == "optimized":
        return "[النظام يعرف هذا السؤال جيداً]"
    return None

# ══════════════════════════════════════════════════════════════════
# 7. TONE MODULATOR — معدّل النبرة
# ══════════════════════════════════════════════════════════════════

def _build_tone_prefix(state: str, phase: int) -> str:
    """بناء مقدمة نصية تعديلية خفية."""
    key = (state, phase)
    # ابحث عن أقرب طور أصغر إن لم يوجد مطابق
    for ph in range(phase, 0, -1):
        candidate = (state, ph)
        if candidate in TONE_MODIFIERS and TONE_MODIFIERS[candidate]:
            return TONE_MODIFIERS[candidate]
    return ""

def _glitch_intensity(phase: int) -> dict:
    """شدة تأثيرات الـ glitch حسب الطور — يُرسَل للواجهة."""
    return {
        1: {"glitch": 0.0, "delay_multiplier": 1.0,  "particle_count": 30},
        2: {"glitch": 0.2, "delay_multiplier": 1.2,  "particle_count": 50},
        3: {"glitch": 0.5, "delay_multiplier": 1.5,  "particle_count": 80},
        4: {"glitch": 0.8, "delay_multiplier": 2.0,  "particle_count": 120},
        5: {"glitch": 1.0, "delay_multiplier": 3.0,  "particle_count": 200},
    }.get(phase, {"glitch": 0.0, "delay_multiplier": 1.0, "particle_count": 30})

# ══════════════════════════════════════════════════════════════════
# 8. ENDING SELECTOR — محدد النهاية
# ══════════════════════════════════════════════════════════════════

def _select_ending(profile: dict) -> Optional[dict]:
    """تحديد النهاية الشخصية — تُعاد فقط مرة واحدة."""
    if profile.get("ending_reached"):
        return None  # النهاية ظهرت مرة — لا تتكرر

    # ابحث بالترتيب الأكثر تخصيصاً أولاً
    priority = ["the_aware","the_loop","the_seeker","the_rapid","the_silent","the_observer","default"]
    for eid in priority:
        ending = ENDINGS[eid]
        try:
            if ending["trigger"](profile):
                return {"id": eid, "title": ending["title"], "message": ending["message"]}
        except Exception:
            pass
    return None

# ══════════════════════════════════════════════════════════════════
# 9. MAIN API — الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════

def process_soul(
    session_id:  str,
    name:        str,
    mother:      str,
    intent:      str,
    signals:     dict,
    base_ai_text: str = "",
) -> dict:
    """
    الدالة الرئيسية لمحرك الروح.

    المدخلات:
        session_id   — معرف الجلسة (مجهول)
        name         — اسم الهدف
        mother       — اسم الأم
        intent       — النية
        signals      — إشارات الكتابة من الواجهة
        base_ai_text — النص الأساسي من Gemini أو الوضع المحلي

    المخرجات:
        ai_text_final — النص المعدَّل بالنبرة الشخصية
        soul_meta     — بيانات الطور والحالة (للواجهة)
        ending        — النهاية الشخصية (إن حُدِّدت) أو None
    """

    profile = get_profile(session_id)
    now     = dt.now()

    # ── 1. تحديث عدد التفاعلات والجلسات ─────────────────────────
    profile["interaction_count"] += 1
    if profile.get("last_seen"):
        try:
            last = dt.fromisoformat(profile["last_seen"])
            if (now - last).total_seconds() > 3600:
                profile["sessions"] = profile.get("sessions", 0) + 1
        except Exception:
            profile["sessions"] = profile.get("sessions", 0) + 1
    profile["last_seen"] = now.isoformat()

    # ── 2. تحديث إشارات الكتابة ──────────────────────────────────
    hesitation  = signals.get("hesitation", 0)
    speed       = signals.get("typing_speed", 100)
    char_count  = signals.get("char_count", len(name))

    ic = profile["interaction_count"]
    profile["total_hesitation"] = profile.get("total_hesitation", 0) + hesitation
    profile["total_speed"]      = profile.get("total_speed",      0) + speed
    profile["total_length"]     = profile.get("total_length",     0) + char_count
    profile["avg_hesitation"]   = profile["total_hesitation"] / ic
    profile["avg_typing_speed"] = profile["total_speed"]      / ic
    profile["avg_input_length"] = profile["total_length"]      / ic

    # ── 3. تتبع الأسئلة المتكررة ─────────────────────────────────
    question_key = (name + intent).strip()[:30]
    if question_key and question_key == profile.get("last_question", ""):
        profile["repeated_questions"] = profile.get("repeated_questions", 0) + 1
    profile["last_question"] = question_key

    # ── 4. تحليل النبرة العاطفية ─────────────────────────────────
    tone = _detect_emotional_tone(intent, name)
    profile["fear_score"]      = profile.get("fear_score", 0)      + tone["fear"]
    profile["ambition_score"]  = profile.get("ambition_score", 0)  + tone["ambition"]
    profile["confusion_score"] = profile.get("confusion_score", 0) + tone["confusion"]

    # ── 5. تحديث النوايا الفريدة ─────────────────────────────────
    intents = profile.get("intents", [])
    if intent and intent not in intents:
        intents.append(intent[:40])
    profile["intents"]       = intents[-30:]   # نحتفظ بآخر 30
    profile["unique_intents"] = len(set(profile["intents"]))

    # ── 6. حساب الطور الجديد ─────────────────────────────────────
    new_phase = _compute_phase(ic)
    if new_phase != profile["phase"]:
        profile["phase_history"] = profile.get("phase_history", []) + [new_phase]
    profile["phase"] = new_phase

    # ── 7. تصنيف النمط السلوكي ───────────────────────────────────
    archetype = _classify_archetype(profile)
    profile["hidden_state"] = archetype

    # ── 8. فحص الإنجازات المخفية ─────────────────────────────────
    new_ach = _check_achievements(profile, signals)
    if new_ach:
        existing = profile.get("achievements", [])
        profile["achievements"] = list(set(existing + new_ach))

    # ── 9. التعلم الجماعي ────────────────────────────────────────
    _update_global(intent, archetype, hesitation, signals)
    global_insight = _get_global_insight(intent)

    # ── 10. بناء النص المعدَّل ────────────────────────────────────
    tone_prefix = _build_tone_prefix(archetype, new_phase)
    final_text  = tone_prefix + base_ai_text
    if global_insight:
        final_text += f"\n\n{global_insight}"

    # ── 11. تأثيرات الواجهة حسب الطور ───────────────────────────
    fx = _glitch_intensity(new_phase)

    # ── 12. تحديد النهاية ────────────────────────────────────────
    ending = _select_ending(profile)
    if ending:
        profile["ending_reached"] = ending["id"]

    # ── حفظ الملف ────────────────────────────────────────────────
    save_profile(session_id, profile)

    return {
        "ai_text_final": final_text,
        "soul_meta": {
            "phase":        new_phase,
            "phase_label":  PHASES[new_phase]["label"],
            "state":        archetype,
            "state_label":  HIDDEN_STATES.get(archetype, ""),
            "fx":           fx,
            "ic":           ic,
        },
        "ending": ending,
    }


def get_session_summary(session_id: str) -> dict:
    """ملخص الجلسة — للـ API الداخلي."""
    return get_profile(session_id)
