# -*- coding: utf-8 -*-
"""
knowledge_loader.py — شمس المعارف v17
══════════════════════════════════════════════════════
محمّل قاعدة المعرفة المستخرجة من مخطوطة البوني

يحمّل البيانات المستخرجة من الملفات الخمسة ويوفرها
لبقية المحركات بشكل منظم وسريع.
══════════════════════════════════════════════════════
"""

import json
import os
from typing import Dict, List, Optional, Any

# ── المسار الأساسي ─────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_KB_DIR   = os.path.join(_BASE_DIR, 'knowledge_base')

# ── تحميل مرة واحدة عند الاستيراد ─────────────────────
def _load(filename: str) -> Any:
    path = os.path.join(_KB_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}

LETTERS:      Dict[str, dict] = _load('letters.json')
DIVINE_NAMES: Dict[str, dict] = _load('divine_names.json')
PLANETS:      Dict[str, dict] = _load('planets.json')
RULES:        List[dict]       = _load('rules.json')
RITUALS:      List[dict]       = _load('rituals.json')
WAFQ_RULES:   List[dict]       = _load('wafq_rules.json')

# ══════════════════════════════════════════════════════
# واجهات البحث
# ══════════════════════════════════════════════════════

def get_letter(char: str) -> Optional[dict]:
    """خصائص الحرف من المخطوطة"""
    return LETTERS.get(char)


def get_divine_name(name: str) -> Optional[dict]:
    """بيانات الاسم الحسنى من المخطوطة"""
    # بحث مباشر
    if name in DIVINE_NAMES:
        return DIVINE_NAMES[name]
    # بحث جزئي
    for k, v in DIVINE_NAMES.items():
        if name in k or k in name:
            return v
    return None


def get_planet(name: str) -> Optional[dict]:
    """بيانات الكوكب"""
    return PLANETS.get(name)


def get_planet_by_day(day_num: int) -> Optional[dict]:
    """
    الكوكب الحاكم ليوم معين
    day_num: 0=الأحد، 1=الاثنين...6=السبت
    """
    for name, data in PLANETS.items():
        if data.get('day_num') == day_num:
            return {'name': name, **data}
    return None


def get_rules_by_category(category: str) -> List[dict]:
    """القواعد حسب الفئة: element / time / ritual / wafq / intent / compatibility"""
    return [r for r in RULES if r.get('category') == category]


def get_rituals_by_purpose(keyword: str) -> List[dict]:
    """الطقوس المناسبة لغرض معين"""
    results = []
    for r in RITUALS:
        if keyword in r.get('purpose', '') or keyword in r.get('name', ''):
            results.append(r)
    return results


def get_wafq_size_for_element(element: str) -> str:
    """حجم الوفق المناسب للطبع"""
    for rule in WAFQ_RULES:
        if element in rule.get('elements', []) or 'كل الطبائع' in rule.get('elements', []):
            return rule['size']
    return '4x4'  # افتراضي


def get_letters_by_element(element: str) -> List[str]:
    """
    الحروف التي طبعها = element
    element: ناري / مائي / هوائي / ترابي
    """
    return [char for char, data in LETTERS.items()
            if data.get('element') == element]


def get_letters_by_type(letter_type: str) -> List[str]:
    """
    الحروف حسب نوعها نوراني / ظلماني
    """
    return [char for char, data in LETTERS.items()
            if data.get('type') == letter_type]


def get_dominant_element(name: str) -> str:
    """
    الطبع الغالب في الاسم بناءً على جدول المخطوطة
    يُعيد: ناري / مائي / هوائي / ترابي
    """
    counts: Dict[str, int] = {'ناري': 0, 'مائي': 0, 'هوائي': 0, 'ترابي': 0}
    for char in name:
        info = LETTERS.get(char)
        if info:
            elem = info.get('element', '')
            if elem in counts:
                counts[elem] += 1
    return max(counts, key=counts.get) if any(counts.values()) else 'ناري'


def get_abjad_from_kb(name: str) -> Optional[int]:
    """
    قيمة الجمل من قاعدة البيانات (للأسماء المسجلة)
    """
    data = DIVINE_NAMES.get(name)
    return data.get('abjad') if data else None


def search_divine_names(query: str) -> List[Dict]:
    """
    بحث نصي في الأسماء وخصائصها
    """
    results = []
    q = query.strip()
    for name, data in DIVINE_NAMES.items():
        if (q in name or
                q in data.get('property', '') or
                q in data.get('suitable', '')):
            results.append({'name': name, **data})
    return results


def get_compatible_elements(element: str) -> Dict[str, str]:
    """
    التوافق العنصري بناءً على قانون الطبائع
    يُعيد: {'ally': ..., 'neutral': ..., 'enemy': ...}
    """
    compatibility = {
        'ناري':  {'ally': 'هوائي',  'neutral': 'ترابي', 'enemy': 'مائي'},
        'مائي':  {'ally': 'ترابي',  'neutral': 'هوائي', 'enemy': 'ناري'},
        'هوائي': {'ally': 'ناري',   'neutral': 'مائي',  'enemy': 'ترابي'},
        'ترابي': {'ally': 'مائي',   'neutral': 'ناري',  'enemy': 'هوائي'},
    }
    return compatibility.get(element, {})


def validate_timing(
    intent_element: str,
    planet_name: str,
    is_forbidden_hour: bool,
    mansion_ruling: str,
) -> Dict[str, Any]:
    """
    التحقق من صحة التوقيت بناءً على قواعد المخطوطة
    يُعيد dict يحتوي على: valid, score, warnings
    """
    warnings = []
    score = 100

    planet = PLANETS.get(planet_name, {})
    planet_element = planet.get('element', '')

    # R02: التوقيت الكوكبي
    if planet_element and intent_element:
        compat = get_compatible_elements(intent_element)
        if planet_element == compat.get('enemy'):
            warnings.append(f'⚠️ الكوكب الحالي ({planet_name}) معادٍ لطبع العمل ({intent_element})')
            score -= 40
        elif planet_element == intent_element:
            score += 10  # توافق تام

    # R03: المنزلة القمرية
    if 'نحسة' in mansion_ruling:
        warnings.append(f'⚠️ المنزلة القمرية نحسة — يُفضَّل التأجيل')
        score -= 25
    elif 'سعيدة' in mansion_ruling:
        score += 15

    # R14: الساعات المذمومة
    if is_forbidden_hour:
        warnings.append('⚠️ هذه الساعة مذمومة — تجنبها في الأعمال الكبيرة')
        score -= 20

    return {
        'valid':    score >= 60,
        'score':    max(0, min(100, score)),
        'warnings': warnings,
    }


def get_summary() -> Dict[str, int]:
    """ملخص قاعدة المعرفة"""
    return {
        'letters':      len(LETTERS),
        'divine_names': len(DIVINE_NAMES),
        'planets':      len(PLANETS),
        'rules':        len(RULES),
        'rituals':      len(RITUALS),
        'wafq_rules':   len(WAFQ_RULES),
    }


# سجّل عند التحميل
try:
    import logger_system
    s = get_summary()
    logger_system.log('INFO', 'knowledge_loader',
                      f'📚 قاعدة المعرفة محملة: {s}')
except Exception:
    pass
