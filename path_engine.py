# -*- coding: utf-8 -*-
"""
path_engine.py — نظام المسارات الأربعة
═══════════════════════════════════════════════════════════════════
يحدد المسار الإلزامي بناءً على (نية + شدة + حالة مصفوفة + تعارض).
المستخدم لا يختار المسار — النظام يفرضه.

المسارات:
  🟥 Influence  (تأثير)  — جذب، سيطرة، تفريق
  🟦 Insight    (كشف)    — معرفة، رؤية
  🟩 Shielding  (حماية)  — حفظ، إبطال سحر
  ⬛ Chaos      (فوضى)   — نية غير واضحة أو تعارض شديد
═══════════════════════════════════════════════════════════════════
"""

from typing import Dict

# ============================================================================
# تعريف المسارات
# ============================================================================
PATHS = {
    "influence": {
        "name": "تأثير", "name_en": "Influence",
        "color": "#ff4444", "icon": "⚡",
        "allowed_intents":  ["attraction", "control", "separation", "wealth"],
        "forbidden_intents":["knowledge", "protection"],
        "min_intensity":     0.35,
        "allowed_states":   ["stable", "repetition"],
        "allowed_modules":  ["kings", "wafq", "asma", "talisman"],
        "forbidden_modules":["geomancy_deep", "zairja_deep"],
        "description":      "تغيير الواقع — جلب، قهر، محبة. يُسمح بالملوك والأوفاق.",
    },
    "insight": {
        "name": "كشف", "name_en": "Insight",
        "color": "#00f2ff", "icon": "🔍",
        "allowed_intents":  ["knowledge"],
        "forbidden_intents":["attraction", "control", "separation"],
        "min_intensity":     0.2,
        "allowed_states":   ["stable", "repetition", "conflict"],
        "allowed_modules":  ["geomancy", "zairja", "jafr", "calculations"],
        "forbidden_modules":["kings", "talisman_execution"],
        "description":      "تحليل وفهم الحالة. لا ملوك ولا أوفاق تأثير.",
    },
    "shielding": {
        "name": "حماية", "name_en": "Shielding",
        "color": "#44ff88", "icon": "🛡️",
        "allowed_intents":  ["protection"],
        "forbidden_intents":["attraction", "control", "separation", "knowledge"],
        "min_intensity":     0.25,
        "allowed_states":   ["conflict", "repetition", "stable"],
        "allowed_modules":  ["gates_4_9_11", "ayat_kursi", "protection_talismans"],
        "forbidden_modules":["kings_influence", "wafq_offensive"],
        "description":      "تحصين ودفع أذى وإبطال سحر. لا تأثير مباشر.",
    },
    "chaos": {
        "name": "فوضى", "name_en": "Chaos",
        "color": "#888888", "icon": "🌀",
        "allowed_intents":  ["chaos"],
        "forbidden_intents":[],
        "min_intensity":     0.0,
        "allowed_states":   ["conflict"],
        "allowed_modules":  ["sandbox", "exploration"],
        "forbidden_modules":["kings", "wafq", "geomancy_full"],
        "description":      "نية غير واضحة — وضع تجريبي محدود. النتائج غير معتمدة.",
    },
}

PATH_MESSAGES = {
    "influence": "🟥 تم تفعيل مسار التأثير. الملك المناسب سيُستدعى تلقائياً.",
    "insight":   "🟦 تم تفعيل مسار الكشف. سيتم استخدام الرمل والزايرجة للتحليل.",
    "shielding": "🟩 تم تفعيل مسار الحماية. سيتم توليد رموز دفاعية.",
    "chaos":     "⬛ تم تفعيل مسار الفوضى. النية غير واضحة — النتائج غير معتمدة.",
}

# ============================================================================
# منطق تحديد المسار
# ============================================================================

def determine_path(intent_type: str, intensity: float,
                   state: str, conflict: bool = False) -> Dict:
    # فوضى صريحة
    if intent_type == "chaos" or (conflict and intensity < 0.3):
        return PATHS["chaos"].copy()

    # بحث طبيعي
    for path_id, path in PATHS.items():
        if intent_type in path["allowed_intents"]:
            if intensity >= path["min_intensity"]:
                if state in path["allowed_states"]:
                    return path.copy()

    # توسيع بدون شرط الحالة
    for path_id, path in PATHS.items():
        if intent_type in path["allowed_intents"]:
            if intensity >= path["min_intensity"]:
                return path.copy()

    return PATHS["chaos"].copy()


def resolve_path(intent_result: Dict, matrix_state: str) -> Dict:
    """الواجهة الرئيسية — تُستدعى من app.py."""
    intent_type = intent_result.get("intent_type", "chaos")
    intensity   = intent_result.get("intensity", 0.5)
    conflict    = intent_result.get("conflict", False)

    path    = determine_path(intent_type, intensity, matrix_state, conflict)
    message = PATH_MESSAGES.get(path["name_en"].lower(), "مسار غير معروف.")

    return {
        "path":         path,
        "message":      message,
        "intent_type":  intent_type,
        "intensity":    intensity,
        "conflict":     conflict,
        "matrix_state": matrix_state,
    }


def is_module_allowed(path: Dict, module: str) -> bool:
    return module in path.get("allowed_modules", [])


if __name__ == "__main__":
    scenarios = [
        ("attraction", 0.7, "stable",    False),
        ("control",    0.9, "conflict",  False),
        ("knowledge",  0.4, "stable",    False),
        ("protection", 0.6, "conflict",  True),
        ("chaos",      0.2, "conflict",  True),
    ]
    for intent, intensity, state, conflict in scenarios:
        p = determine_path(intent, intensity, state, conflict)
        print(f"{intent:12} i={intensity} s={state:12} → {p['name']} {p['icon']}")
