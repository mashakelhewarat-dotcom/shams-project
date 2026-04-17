# -*- coding: utf-8 -*-
"""
mandal_engine.py
═══════════════════════════════════════════════════════════════════
نظام الكشف في الكأس والمرآة – الفصل الرابع من شمس المعارف الكبرى
المصدر: شمس المعارف الكبرى، الفصل الرابع (تصاريف الكشوفات الروحية)، ص 32
═══════════════════════════════════════════════════════════════════
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================================
# 1. حروف النور (للكتابة حول الكأس أو المرآة)
# ============================================================================
NOORANI_LETTERS = ['ا', 'ه', 'ط', 'م', 'ف', 'ش', 'ذ', 'ب', 'و', 'ك', 'ص', 'ق', 'ر', 'ت']

# ============================================================================
# 2. أنواع أدوات الكشف
# ============================================================================
MANDAL_TOOLS = {
    "الكأس": {
        "name": "الكأس البلوري",
        "description": "كأس من بلور أو زجاج صافي، يملأ بالماء النقي.",
        "preparation": "يملأ الكأس بالماء، وتكتب حروف النور حول حافته الخارجية بقلم مداد أحمر أو أسود.",
        "reference": "الفصل الرابع، ص32"
    },
    "المرآة": {
        "name": "المرآة المعدنية",
        "description": "مرآة من نحاس مصقول أو فضة، تواجه الناظور.",
        "preparation": "تُبخَّر المرآة بلبان ذكر، وتُكتب حولها حروف النور على إطارها.",
        "reference": "الفصل الرابع، ص32"
    }
}

# ============================================================================
# 3. تفسير الرؤى
# ============================================================================
VISION_INTERPRETATION = {
    "نور أبيض": "خادم مسلم طيب – الرؤية صادقة.",
    "نور أحمر": "خادم ناري – يحتاج إلى تلاوة آية الكرسي.",
    "راية سوداء": "خادم كافر – اصرفه بقراءة المعوذات والإخلاص 3 مرات.",
    "رمز X": "خادم شرير – لا ينفع العمل، أعد الاستنزال.",
    "وجه يضحك": "بشارة خير، وعلامة قبول العمل.",
    "وجه عابس": "تحذير من خطأ في العزيمة أو الوقت.",
    "سيف مسلول": "قوة ونصر وحماية.",
    "كتاب مفتوح": "علم ومعرفة، أو إجابة عن سؤال.",
    "خاتم أو طلسم": "إشارة إلى وجود عمل روحاني أو سحر.",
    "ماء جار": "رزق وفير وتيسير أمور.",
    "نار مشتعلة": "غضب أو عداوة، يُنصح بالصبر.",
    "نجمة سداسية": "حماية وقوة روحانية عالية.",
}

# ============================================================================
# 4. شروط الناظور
# ============================================================================
OBSERVER_CONDITIONS = {
    "purification": "يتوضأ الناظور وضوء الصلاة، ويستقبل القبلة، ويجلس متربعاً.",
    "direction": "يتجه نحو الشرق في هذا الباب.",
    "mental_state": "خالي الذهن، صادق النية، غير مشغول.",
    "physical_state": "طاهر الجسد والثياب، غير متعب.",
    "age_gender": "يفضل طفلاً لم يبلغ الحلم، أو امرأة طاهرة، أو رجل ذو نفس زكية.",
    "avoid": "لا ينفع من به مس، أو من يشرب الخمر، أو من يكثر الكلام."
}

# ============================================================================
# 5. خواتم الكشف
# ============================================================================
MANDAL_SEALS = {
    "كشف_الغائب": {
        "name": "خاتم كشف الغائب",
        "shape": "دائرة حولها حروف النور، وفي الوسط اسم المطلوب واسم أمه.",
        "inscription": "بسم الله الرحمن الرحيم، يا فتاح يا عليم، أظهر لي فلان بن فلانة بحق هذه الحروف.",
        "purpose": "الكشف عن شخص غائب أو مفقود."
    },
    "رؤية_الخادم": {
        "name": "خاتم استنزال خادم اليوم",
        "shape": "مربع بداخله نجمة سداسية، وحوله أسماء الخدام الأربعة.",
        "inscription": "بسم الله الرحمن الرحيم، أظهر لي أيها الخادم الملك فلان بحق هذه الأسماء.",
        "purpose": "رؤية خادم الملك المختار."
    }
}

# ============================================================================
# 6. الدوال الرئيسية
# ============================================================================

def draw_noorani_circle(canvas_context, center_x, center_y, radius, letters=NOORANI_LETTERS):
    """إرجاع إحداثيات حروف النور حول دائرة لرسمها في Canvas."""
    points = []
    num_letters = len(letters)
    for i, letter in enumerate(letters):
        angle = 2 * math.pi * i / num_letters
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append({"letter": letter, "x": x, "y": y, "angle": angle})
    return points

def check_observer_compatibility(observer_name: str, observer_mother: str) -> dict:
    """فحص صلاحية الناظور بناءً على اسمه واسم أمه."""
    from data import ABJAD_VALUES
    jummal = sum(ABJAD_VALUES.get(c, 0) for c in observer_name) + sum(ABJAD_VALUES.get(c, 0) for c in observer_mother)
    score = 50
    if 100 <= jummal <= 500:
        score += 30
    if score >= 70:
        status = "مناسب جداً"
        advice = "يُتوقع أن يرى بوضوح."
    elif score >= 50:
        status = "متوسط"
        advice = "قد يرى خيالات، يحتاج إلى تكرار التجربة."
    else:
        status = "غير مناسب"
        advice = "لا يُنصح باستخدام هذا الناظور."
    return {"name": observer_name, "mother": observer_mother, "jummal": jummal, "status": status, "score": score, "advice": advice, "conditions": OBSERVER_CONDITIONS}

def get_best_mandal_time() -> dict:
    """تحديد الوقت المناسب للكشف (محاكاة مبسطة)."""
    now = datetime.now()
    weekday = now.strftime("%A")
    day_ar = {"Sunday":"الأحد","Monday":"الاثنين","Tuesday":"الثلاثاء","Wednesday":"الأربعاء","Thursday":"الخميس","Friday":"الجمعة","Saturday":"السبت"}.get(weekday, "الأحد")
    if day_ar in ["الجمعة", "السبت"]:
        return {"suitable": False, "reason": f"يوم {day_ar} غير مناسب للكشف.", "recommended": "اختر الأحد أو الاثنين أو الأربعاء"}
    return {"suitable": True, "reason": f"يوم {day_ar} مناسب – يُفضل بعد العشاء.", "recommended": "الساعات 1، 2، 8، 9، 10 مناسبة"}

def summon_mandal(tool_type: str, observer_name: str, observer_mother: str, king_name: str = None, target_name: str = None, target_mother: str = None) -> dict:
    """استدعاء المندل والكشف (محاكاة مع توصيات)."""
    observer_check = check_observer_compatibility(observer_name, observer_mother)
    if observer_check["status"] == "غير مناسب":
        return {"success": False, "message": f"الناظور غير مناسب: {observer_check['advice']}", "observer_check": observer_check}
    time_check = get_best_mandal_time()
    if not time_check["suitable"]:
        return {"success": False, "message": f"الوقت غير مناسب: {time_check['reason']}", "time_check": time_check}
    if target_name and target_mother:
        seal = MANDAL_SEALS["كشف_الغائب"]
        purpose = f"الكشف عن {target_name} بن/ت {target_mother}"
        inscription = seal["inscription"].replace("فلان بن فلانة", f"{target_name} بن/ت {target_mother}")
    else:
        seal = MANDAL_SEALS["رؤية_الخادم"]
        purpose = f"رؤية خادم الملك {king_name if king_name else 'المختار'}"
        inscription = seal["inscription"].replace("الملك فلان", king_name if king_name else "الموكل")
    possible_symbols = list(VISION_INTERPRETATION.keys())
    random_symbols = random.sample(possible_symbols, min(3, len(possible_symbols)))
    interpretation = "\n".join([f"{sym}: {VISION_INTERPRETATION[sym]}" for sym in random_symbols])
    tool = MANDAL_TOOLS.get(tool_type, MANDAL_TOOLS["الكأس"])
    return {
        "success": True,
        "tool": tool,
        "seal": seal,
        "purpose": purpose,
        "inscription": inscription,
        "observer_check": observer_check,
        "time_check": time_check,
        "vision": {"symbols": random_symbols, "interpretation": interpretation},
        "recommendation": f"استخدم {tool['name']}، {tool['preparation']}، ثم اقرأ العزيمة: '{inscription}'. تأكد من طهارة الناظور واتجاهه نحو الشرق."
    }

def interpret_vision(symbols: List[str]) -> str:
    """تفسير الرموز المرئية."""
    return "\n".join([f"{sym}: {VISION_INTERPRETATION.get(sym, 'رمز غير معروف')}" for sym in symbols])