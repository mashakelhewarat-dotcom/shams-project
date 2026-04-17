# -*- coding: utf-8 -*-
"""
king_engine.py — محرك اختيار الملوك
═══════════════════════════════════════════════════════════════════
الملك يُستخرج تلقائياً من (نية + وزن + حالة مصفوفة).
المستخدم لا يختار الملك أبداً.
المصدر: شمس المعارف الكبرى، الفصول 13-25 (الاستنزال والعهود)
═══════════════════════════════════════════════════════════════════
"""

from typing import Dict, Optional, Tuple

# ============================================================================
# العهد القديم — نص التفويض الإلزامي
# ============================================================================
ANCIENT_COVENANT = (
    "باسم الله المحيط بملكوت السموات والأرض، وباسم القدوس الغالب على أمره، "
    "وبحق الأسماء التي إذا ذُكرت على الجبال دُكت، وعلى الصخور تفجرت، "
    "وعلى البحار غارت — أخذتُ عليكم العهد المأخوذ على سليمان بن داود عليهما السلام، "
    "وعزائم الله التامة، ومواثيقه الغليظة، أن لا تعصوا لي أمراً، "
    "ولا تخالفوا لي طاعة، وأن تجيبوا دعوتي، وتنفذوا حاجتي، "
    "بحق العهد القديم الذي بينكم وبين سائر الأنبياء، "
    "والاسم الذي له القوة والقدرة والبرهان. الوحا العجل الساعة."
)

# ============================================================================
# التهاطيل السبعة — الأسماء السريانية للتفعيل
# ============================================================================
TAHATIL_KINGS = {
    "mizhab":     {"tahateel": "لَجْهَطْطِيل",  "root_key": "أبْجَدْ",      "upper_king": "روقيائيل"},
    "murrah":     {"tahateel": "لَطَهْطْطِيل",   "root_key": "هَوَّزْ",      "upper_king": "جبرائيل"},
    "ahmar":      {"tahateel": "لَقَهْطْطِيل",   "root_key": "حُطِّي",       "upper_king": "سمسمائيل"},
    "burqan":     {"tahateel": "لَفَهْطْطِيل",   "root_key": "كَلَمُنْ",     "upper_king": "ميكائيل"},
    "shamhurish": {"tahateel": "لَنَهْطْطِيل",   "root_key": "سَعْفَصْ",     "upper_king": "صرفيائيل"},
    "zawba":      {"tahateel": "لَجْهَطْطِيل",   "root_key": "قَرَشَتْ",     "upper_king": "عنيائيل"},
    "maymun":     {"tahateel": "لَظَهْطْطِيل",   "root_key": "ثَخَذْ ضَظَغْ","upper_king": "كسفيائيل"},
}

# ============================================================================
# قاعدة بيانات الملوك السبعة
# ============================================================================
KINGS_DB = {
    "mizhab": {
        "name": "المذهب", "arabic": "مذهب",
        "planet": "الشمس", "day": "الأحد", "element": "نار",
        "power": "الجلب والمحبة والرزق والهيبة والظهور",
        "intents": ["attraction", "wealth"],
        "min_weight": 0.3, "max_weight": 0.8, "state_preference": "stable",
        "color": "#ffaa44",
    },
    "murrah": {
        "name": "مُرة", "arabic": "مُرة",
        "planet": "القمر", "day": "الاثنين", "element": "هواء",
        "power": "الكشف والإلهام والفراسة والسفر والحماية الليلية",
        "intents": ["knowledge", "protection"],
        "min_weight": 0.2, "max_weight": 0.7, "state_preference": "stable",
        "color": "#C8C8FF",
    },
    "ahmar": {
        "name": "الأحمر", "arabic": "الأحمر",
        "planet": "المريخ", "day": "الثلاثاء", "element": "نار",
        "power": "القهر والسيطرة والنصر والغلبة والحرب",
        "intents": ["control", "separation"],
        "min_weight": 0.5, "max_weight": 1.0, "state_preference": "conflict",
        "color": "#ff4444",
    },
    "burqan": {
        "name": "برقان", "arabic": "برقان",
        "planet": "عطارد", "day": "الأربعاء", "element": "ماء",
        "power": "الإخفاء والحماية والسر والذكاء والعلم",
        "intents": ["protection", "knowledge"],
        "min_weight": 0.2, "max_weight": 0.9, "state_preference": "repetition",
        "color": "#00C8FF",
    },
    "shamhurish": {
        "name": "شمهورش", "arabic": "شمهورش",
        "planet": "المشتري", "day": "الخميس", "element": "تراب",
        "power": "الرزق والتوسعة والبركة والقضاء والنمو",
        "intents": ["wealth", "attraction"],
        "min_weight": 0.4, "max_weight": 0.9, "state_preference": "stable",
        "color": "#AA00FF",
    },
    "zawba": {
        "name": "زوبعة", "arabic": "زوبعة",
        "planet": "الزهرة", "day": "الجمعة", "element": "هواء",
        "power": "المحبة والجمال والألفة والزواج والسرعة",
        "intents": ["attraction", "separation"],
        "min_weight": 0.1, "max_weight": 0.6, "state_preference": "repetition",
        "color": "#00f2ff",
    },
    "maymun": {
        "name": "ميمون", "arabic": "ميمون",
        "planet": "زحل", "day": "السبت", "element": "تراب",
        "power": "الكنوز والأسرار والدفائن والعزلة والتحصين الطويل",
        "intents": ["knowledge", "control"],
        "min_weight": 0.6, "max_weight": 1.0, "state_preference": "conflict",
        "color": "#888888",
    },
}

# ============================================================================
# دوال الاختيار
# ============================================================================

def select_king(intent_type: str, weight: float, state: str) -> Tuple[str, Dict]:
    """يختار الملك تلقائياً — لا تدخّل للمستخدم."""
    if intent_type == "chaos":
        kid = "burqan" if weight < 0.5 else "maymun"
        return kid, KINGS_DB[kid]

    # 1. بحث بالشروط الكاملة
    candidates = [
        (kid, d) for kid, d in KINGS_DB.items()
        if intent_type in d["intents"]
        and d["min_weight"] <= weight <= d["max_weight"]
        and (d["state_preference"] == state or state == "repetition")
    ]

    # 2. بدون شرط الحالة
    if not candidates:
        candidates = [
            (kid, d) for kid, d in KINGS_DB.items()
            if intent_type in d["intents"]
            and d["min_weight"] <= weight <= d["max_weight"]
        ]

    # 3. بدون شرط الوزن
    if not candidates:
        candidates = [
            (kid, d) for kid, d in KINGS_DB.items()
            if intent_type in d["intents"]
        ]

    if not candidates:
        return "burqan", KINGS_DB["burqan"]

    # أقرب وزن
    best = min(candidates,
               key=lambda x: abs((x[1]["min_weight"] + x[1]["max_weight"]) / 2 - weight))
    return best


def get_king_activation(king_id: str) -> Dict:
    """بيانات تفعيل الملك: العهد + التهطيل + مفتاح الجذر."""
    t = TAHATIL_KINGS.get(king_id, TAHATIL_KINGS["mizhab"])
    return {
        "ancient_covenant": ANCIENT_COVENANT,
        "tahateel":         t["tahateel"],
        "root_key":         t["root_key"],
        "upper_king":       t["upper_king"],
    }


def get_king_for_intent(intent_type: str,
                        weight: float = 0.5,
                        state: str = "stable") -> Dict:
    """الواجهة الرئيسية — تُستدعى من app.py و path_engine."""
    kid, data = select_king(intent_type, weight, state)
    activation = get_king_activation(kid)

    return {
        "king_id":          kid,
        "king_name":        data["name"],
        "king_arabic":      data["arabic"],
        "upper_king":       activation["upper_king"],
        "planet":           data["planet"],
        "day":              data["day"],
        "element":          data["element"],
        "power":            data["power"],
        "color":            data["color"],
        "intent_matched":   intent_type,
        "weight":           weight,
        "state":            state,
        "ancient_covenant": activation["ancient_covenant"],
        "tahateel":         activation["tahateel"],
        "root_key":         activation["root_key"],
    }


if __name__ == "__main__":
    tests = [
        ("attraction", 0.5, "stable"),
        ("control",    0.8, "conflict"),
        ("protection", 0.3, "repetition"),
        ("wealth",     0.6, "stable"),
        ("chaos",      0.2, "conflict"),
    ]
    for intent, w, s in tests:
        r = get_king_for_intent(intent, w, s)
        print(f"{intent:12} w={w} s={s:12} → {r['king_name']} ({r['upper_king']})")
