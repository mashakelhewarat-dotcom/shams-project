# -*- coding: utf-8 -*-
"""
intent_engine.py — محرك اكتشاف النية
═══════════════════════════════════════════════════════════════════
المصدر: شمس المعارف الكبرى + المخطط النهائي (Gemini + ChatGPT + DeepSeek)

الوظيفة:
- تحليل النص (أو غيابه) لاستنتاج النية الروحانية.
- إرجاع: نوع النية، شدتها، وضوحها، وجود تعارض.
- هو أول خطوة في Intent-Driven Pipeline.

⚠️ المستخدم لا يختار النية — النظام يستنتجها.
═══════════════════════════════════════════════════════════════════
"""

import re
from typing import Dict, List, Tuple

# ============================================================================
# 1. قواميس الكلمات المفتاحية لكل نوع نية
# ============================================================================
INTENT_KEYWORDS = {
    "attraction": {
        "ar": "جذب ومحبة",
        "keywords": [
            "حب", "محبة", "جذب", "ألفة", "ود", "قبول", "هيبة", "جاه",
            "تأثير", "إعجاب", "زواج", "خطبة", "صداقة", "يحبني", "تحبني",
            "قريب", "ألفة", "مودة", "غرام", "هوى", "عاطفة",
        ],
        "weight": 1.0,
    },
    "control": {
        "ar": "سيطرة وقهر",
        "keywords": [
            "سيطرة", "قهر", "تسخير", "أمر", "طاعة", "إجبار", "كسر",
            "تدمير", "انتقام", "غلبة", "نصر", "ردع", "أسحق", "أذل",
            "أقهر", "خضع", "أسيطر",
        ],
        "weight": 1.2,
    },
    "separation": {
        "ar": "تفريق وعزل",
        "keywords": [
            "تفريق", "قطع", "عزل", "بغض", "كراهية", "خصومة", "فرقة",
            "طلاق", "هجر", "إبعاد", "تباعد", "نفور",
        ],
        "weight": 1.1,
    },
    "protection": {
        "ar": "حماية وتحصين",
        "keywords": [
            "حماية", "تحصين", "حفظ", "درع", "دفع", "أذى", "شر",
            "عين", "حسد", "سحر", "كيد", "مكر", "خوف", "تهديد",
            "خايف", "أخشى", "تحصّن", "وقاية",
        ],
        "weight": 0.9,
    },
    "knowledge": {
        "ar": "كشف ومعرفة",
        "keywords": [
            "كشف", "معرفة", "علم", "رؤية", "خبر", "حقيقة", "سر",
            "غيب", "مستقبل", "حيرة", "فهم", "تفسير", "أعرف", "أفهم",
            "يحدث", "ماذا", "لماذا", "كيف", "ضائع",
        ],
        "weight": 0.8,
    },
    "wealth": {
        "ar": "رزق وثروة",
        "keywords": [
            "رزق", "مال", "ثروة", "بركة", "وفرة", "فقر", "ضيق",
            "كسب", "توسعة", "غنى", "نجاح", "تجارة", "ربح",
        ],
        "weight": 1.0,
    },
    "chaos": {
        "ar": "فوضى (نية غير واضحة)",
        "keywords": [],
        "weight": 0.5,
    },
}

CONFLICT_INDICATORS = [
    "لكن", "متردد", "حائر", "لا أعرف", "ربما", "أو", "بين",
    "تارة", "أشك", "مش عارف", "مش متأكد",
]

VAGUE_INDICATORS = [
    "شيء", "كذا", "موضوع", "أمر", "هذا", "ذلك", "ربما", "يمكن",
]

# ============================================================================
# 2. دوال مساعدة
# ============================================================================

def tokenize(text: str) -> List[str]:
    cleaned = re.sub(r'[،؛؟!ـ"\'\(\)\[\]\{\}]', ' ', text)
    return cleaned.split()


def detect_intent_from_text(text: str) -> Tuple[str, float]:
    if not text or len(text.strip()) < 2:
        return "chaos", 0.0
    words = tokenize(text)
    scores = {k: 0.0 for k in INTENT_KEYWORDS}
    for word in words:
        for intent, data in INTENT_KEYWORDS.items():
            for kw in data["keywords"]:
                if kw in word:
                    scores[intent] += data["weight"]
    if len(words) < 3 and max(scores.values()) < 0.5:
        scores["chaos"] += 1.0
    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score <= 0:
        return "chaos", 0.5
    return best, best_score


def calculate_intensity(score: float, text_length: int) -> float:
    length_factor = min(0.3, text_length / 200.0)
    return round(min(1.0, (score / 3.0) + length_factor), 2)


def calculate_clarity(text: str) -> float:
    if not text or len(text) < 3:
        return 0.1
    words = tokenize(text)
    vague = sum(1 for w in words if any(v in w for v in VAGUE_INDICATORS))
    clarity = 1.0 - (vague / max(1, len(words))) * 0.7
    if len(words) > 50:
        clarity *= 0.8
    return round(max(0.1, min(1.0, clarity)), 2)


def detect_conflict(text: str) -> bool:
    if not text:
        return False
    return any(ind in text for ind in CONFLICT_INDICATORS)


def handle_silence() -> dict:
    return {
        "intent_type":  "chaos",
        "intensity":    0.7,
        "clarity":      0.05,
        "conflict":     False,
        "is_silence":   True,
        "raw_text":     "",
        "message":      "⚠️ لم يتم اكتشاف إدخال — جارٍ استخراج الإشارة المتبقية... (مسار الفوضى)",
    }

# ============================================================================
# 3. الدالة الرئيسية
# ============================================================================

def analyze_intent(user_input: str, silence_detected: bool = False) -> Dict:
    """
    تحلّل النص وتُرجع نوع النية وشدّتها ووضوحها ووجود تعارض.
    هي أول خطوة في Intent-Driven Pipeline.
    """
    if silence_detected or not user_input or not user_input.strip():
        return handle_silence()

    text = user_input.strip()
    intent, score = detect_intent_from_text(text)
    intensity = calculate_intensity(score, len(text))
    clarity   = calculate_clarity(text)
    conflict  = detect_conflict(text)

    intent_ar = INTENT_KEYWORDS.get(intent, {}).get("ar", intent)
    msg = f"✅ تم تحليل النية: {intent_ar} (شدة {intensity:.2f}، وضوح {clarity:.2f})"
    if conflict:
        msg += " ⚠️ يوجد تعارض داخلي في النية."

    return {
        "intent_type": intent,
        "intent_ar":   intent_ar,
        "intensity":   intensity,
        "clarity":     clarity,
        "conflict":    conflict,
        "is_silence":  False,
        "raw_text":    text[:200],
        "message":     msg,
    }


if __name__ == "__main__":
    tests = [
        "أريد أن يحبني فلان",
        "عايز أقهر عدوي",
        "خايف من الحسد",
        "أريد أن أعرف مستقبلي",
        "عايز رزق ومال",
        "",
    ]
    for t in tests:
        r = analyze_intent(t, silence_detected=(not t))
        print(f"'{t[:30]}' → {r['intent_type']} (شدة {r['intensity']})")
