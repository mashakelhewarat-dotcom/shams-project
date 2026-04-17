# -*- coding: utf-8 -*-
"""
core_engine.py — شمس المعارف v17
══════════════════════════════════════════════════════
المحرك المركزي — العقل الذي يجمع كل المحركات

يستقبل Input (اسم / نية / وقت)
يقرر يروح لأنهي Engine
يدمج النتائج في استجابة واحدة متكاملة
══════════════════════════════════════════════════════
"""

import time
from datetime import datetime as dt, timezone
from typing import Dict, List, Optional, Any, Tuple

# ── قاعدة المعرفة + محرك القواعد ────────────────────
from knowledge_loader import (
    DIVINE_NAMES, PLANETS, LETTERS,
    get_dominant_element, get_compatible_elements,
    get_rituals_by_purpose, validate_timing, get_summary,
)
from rule_engine import (
    apply_all_rules, analyze_name_deep,
    check_elemental_law, select_best_divine_name,
    generate_ritual_instructions, analyze_arabic_text,
)

# ── المحركات الأصلية ─────────────────────────────────
try:
    from shams_engine import (
        process_void, check_elemental_compatibility,
        calculate_affinity_v11,
    )
    SHAMS_OK = True
except Exception:
    SHAMS_OK = False

try:
    from jafr_engine import calc_jafr_simple
    JAFR_OK = True
except Exception:
    JAFR_OK = False

try:
    import logger_system
    LOGGER_OK = True
except Exception:
    LOGGER_OK = False


def _log(level: str, msg: str) -> None:
    if LOGGER_OK:
        logger_system.log(level, 'core_engine', msg)


# ══════════════════════════════════════════════════════
# الـ Pipeline الرئيسي
# ══════════════════════════════════════════════════════

def process(
    target_name:  str,
    mother_name:  str,
    intent:       str  = '',
    hour_info:    Optional[Dict] = None,
    lunar_mansion: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    النقطة الوحيدة للدخول للمحرك المركزي.

    يُجري:
    1. تحليل الاسمين بقواعد المخطوطة
    2. تطبيق Rule Engine
    3. اختيار الاسم الحسنى المناسب
    4. توليد تعليمات الطقس
    5. دمج كل شيء في استجابة واحدة
    """
    t0 = time.perf_counter()
    _log('INFO', f'core_engine.process → name={target_name} intent={intent}')

    # ── قيم افتراضية ───────────────────────────────────
    if not hour_info:
        now = dt.now(timezone.utc)
        hour_info = {
            'planet_ar':   'الشمس',
            'hour_number': now.hour % 12 + 1,
            'is_forbidden': False,
            'day_name':    '',
        }

    if not lunar_mansion:
        lunar_mansion = {'name': '—', 'ruling': 'ممتزجة', 'element': 'هوائي'}

    current_planet  = hour_info.get('planet_ar', 'الشمس')
    is_forbidden    = hour_info.get('is_forbidden', False)
    mansion_ruling  = lunar_mansion.get('ruling', 'ممتزجة')

    # ══════════════════════════════════════════════════
    # المرحلة 1: تطبيق كل قواعد المخطوطة
    # ══════════════════════════════════════════════════
    rules_result = apply_all_rules(
        target_name, mother_name, intent,
        current_planet, is_forbidden, mansion_ruling,
    )

    name_analysis   = rules_result.pop('name_analysis')
    mother_analysis = rules_result.pop('mother_analysis')
    compatibility   = rules_result.pop('compatibility')

    # ══════════════════════════════════════════════════
    # المرحلة 2: حساب الجمل
    # ══════════════════════════════════════════════════
    target_abjad = name_analysis['total_abjad']
    mother_abjad = mother_analysis['total_abjad']
    combined     = target_abjad + mother_abjad

    # ══════════════════════════════════════════════════
    # المرحلة 3: الاسم الحسنى المناسب
    # ══════════════════════════════════════════════════
    best_name = rules_result.pop('recommended_divine_name', None)
    if not best_name:
        best_name = select_best_divine_name(
            intent,
            name_analysis['dominant_element'],
            name_analysis['dominant_type'],
        )

    # ══════════════════════════════════════════════════
    # المرحلة 4: الجفر إن توفر
    # ══════════════════════════════════════════════════
    jafr_data = {}
    if JAFR_OK and target_name:
        try:
            jafr_data = calc_jafr_simple(target_name, intent)
        except Exception:
            pass

    # ══════════════════════════════════════════════════
    # المرحلة 5: الحكم الكوني الشامل
    # ══════════════════════════════════════════════════
    cosmic_judgment = _build_cosmic_judgment(
        rules_result, name_analysis, mother_analysis,
        compatibility, current_planet, intent,
    )

    # ══════════════════════════════════════════════════
    # النتيجة المدمجة
    # ══════════════════════════════════════════════════
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    return {
        # ── معلومات أساسية ────────────────────────────
        'target_name':    target_name,
        'mother_name':    mother_name,
        'intent':         intent,
        'combined_abjad': combined,
        'target_abjad':   target_abjad,
        'mother_abjad':   mother_abjad,

        # ── تحليل الأسماء ─────────────────────────────
        'name_analysis': {
            'element':  name_analysis['dominant_element'],
            'type':     name_analysis['dominant_type'],
            'planet':   name_analysis['dominant_planet'],
            'breakdown': name_analysis['element_breakdown'],
        },
        'mother_analysis': {
            'element':  mother_analysis['dominant_element'],
            'type':     mother_analysis['dominant_type'],
            'planet':   mother_analysis['dominant_planet'],
        },

        # ── التوافق ────────────────────────────────────
        'compatibility': {
            'status':    compatibility['status'],
            'label':     compatibility['label'],
            'mediator':  compatibility['mediator'],
            'strength':  compatibility['strength'],
        },

        # ── الحكم والتوصيات ────────────────────────────
        'approved':       rules_result['approved'],
        'score':          rules_result['score'],
        'verdict':        rules_result['verdict'],
        'warnings':       rules_result['warnings'],
        'boosts':         rules_result['boosts'],
        'recommendations': rules_result['recommendations'],

        # ── الاسم الحسنى ───────────────────────────────
        'recommended_divine_name': best_name,

        # ── تعليمات الطقس ──────────────────────────────
        'ritual_instructions': rules_result.get('ritual_instructions', {}),

        # ── الجفر ──────────────────────────────────────
        'jafr': jafr_data,

        # ── الحكم الكوني ───────────────────────────────
        'cosmic_judgment': cosmic_judgment,

        # ── metadata ───────────────────────────────────
        'processing_ms': elapsed_ms,
        'engine':        'core_engine_v17',
        'kb_summary':    get_summary(),
    }


# ══════════════════════════════════════════════════════
# بناء الحكم الكوني الشامل
# ══════════════════════════════════════════════════════

def _build_cosmic_judgment(
    rules: Dict,
    name_info: Dict,
    mother_info: Dict,
    compat: Dict,
    planet: str,
    intent: str,
) -> Dict[str, Any]:
    """
    يولّد نصاً تفسيرياً شاملاً بأسلوب المخطوطة
    """
    name_elem   = name_info['dominant_element']
    mother_elem = mother_info['dominant_element']
    score       = rules.get('score', 50)
    verdict     = rules.get('verdict', '')

    planet_day = PLANETS.get(planet, {}).get('day', '—')

    lines = []

    # السطر الأول: الطبع
    elem_labels = {
        'ناري':  '🔥 طبع ناري حار يابس',
        'مائي':  '💧 طبع مائي بارد رطب',
        'هوائي': '🌬️ طبع هوائي حار رطب',
        'ترابي': '🌍 طبع ترابي بارد يابس',
    }
    lines.append(f"الاسم: {elem_labels.get(name_elem, name_elem)}")

    # التوافق
    if compat['compatible']:
        lines.append(f"التوافق مع الأم: {compat['label']}")
    else:
        lines.append(f"⚠️ تنبيه: {compat['label']}")
        if compat['mediator']:
            lines.append(f"   → الحل: استخدام حرف «{compat['mediator']}» كوسيط")

    # التوقيت
    lines.append(f"الكوكب الحالي: {planet} (يوم {planet_day})")

    # الحكم
    score_emoji = '🟢' if score >= 70 else '🟡' if score >= 50 else '🔴'
    lines.append(f"{score_emoji} الحكم: {verdict} ({score}/100)")

    # نص المخطوطة
    manuscript_refs = {
        'محبة':    'ومن أراد المحبة فليعمل في ساعة الزهرة والقمر',
        'رزق':     'والرزق مرتبط بالمشتري ويوم الخميس خير الأيام له',
        'قهر':     'وللقهر والسيطرة يُستعمل المريخ في يوم الثلاثاء',
        'حفظ':     'والتحصين يكون بالقمر وحروف الماء والأرض',
        'كشف':     'وكشف الخفايا في ساعة عطارد يوم الأربعاء',
        'هيبة':    'والهيبة تُستمد من أسماء العزيز القهار المقتدر',
        'شفاء':    'والشفاء بأسماء الرحمن الرحيم القادر المحيي',
    }
    if intent in manuscript_refs:
        lines.append(f'📜 من المخطوطة: "{manuscript_refs[intent]}"')

    return {
        'text':  ' · '.join(lines),
        'lines': lines,
        'score': score,
    }


# ══════════════════════════════════════════════════════
# واجهة بحث في قاعدة المعرفة
# ══════════════════════════════════════════════════════

def search_knowledge(query: str) -> Dict[str, Any]:
    """
    يبحث في قاعدة المعرفة الكاملة
    ويُعيد نتائج من الأسماء والقواعد والطقوس
    """
    results = {
        'query':        query,
        'divine_names': [],
        'rituals':      [],
        'rules':        [],
        'letters':      [],
    }

    q = query.strip()

    # بحث في الأسماء
    for name, data in DIVINE_NAMES.items():
        if (q in name or
                q in data.get('property', '') or
                q in data.get('suitable', '')):
            results['divine_names'].append({'name': name, **data})

    # بحث في الطقوس
    results['rituals'] = get_rituals_by_purpose(q)

    # بحث في القواعد
    from knowledge_loader import RULES
    for rule in RULES:
        if q in rule.get('name', '') or q in rule.get('description', ''):
            results['rules'].append(rule)

    # بحث في الحروف
    for char, data in LETTERS.items():
        if q in data.get('element', '') or q in data.get('planet', ''):
            results['letters'].append({'char': char, **data})

    results['total'] = (
        len(results['divine_names']) +
        len(results['rituals']) +
        len(results['rules']) +
        len(results['letters'])
    )
    return results


# ══════════════════════════════════════════════════════
# تحليل نص مدخل لاستخراج النية والاسم
# ══════════════════════════════════════════════════════

def parse_intent_from_text(text: str) -> Dict[str, Any]:
    """
    يحلل نصاً حراً ويستخرج منه:
    - النية المحتملة
    - الطبع الغالب
    - الكلمات المفتاحية
    """
    text_analysis = analyze_arabic_text(text)

    # كلمات مفتاحية للنوايا
    intent_keywords = {
        'محبة':      ['حب', 'محبة', 'قلب', 'عشق', 'ود', 'الفة'],
        'رزق':       ['رزق', 'مال', 'فقر', 'غنى', 'ثروة', 'بركة', 'عمل'],
        'حفظ':       ['حفظ', 'حماية', 'تحصين', 'عين', 'حسد', 'وقاية'],
        'شفاء':      ['مرض', 'شفاء', 'علاج', 'صحة', 'أذى', 'ألم'],
        'كشف':       ['سر', 'خفي', 'كشف', 'معرفة', 'علم', 'باطن'],
        'قهر':       ['عدو', 'ظالم', 'أذى', 'قهر', 'سيطرة', 'غلبة'],
        'هيبة':      ['هيبة', 'مكانة', 'احترام', 'حاسد', 'خوف', 'مهابة'],
        'جلب':       ['جلب', 'استقطاب', 'تقريب', 'استنزال'],
        'ترحيل':     ['إبعاد', 'ترحيل', 'إبطال', 'فك', 'طرد'],
        'قبول':      ['قبول', 'نجاح', 'موافقة', 'قبلوا', 'رضا'],
    }

    detected_intent = ''
    max_matches = 0
    for intent, keywords in intent_keywords.items():
        matches = sum(1 for k in keywords if k in text)
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent

    return {
        'detected_intent':  detected_intent,
        'confidence':        min(100, max_matches * 33),
        'dominant_element': text_analysis['dominant_element'],
        'total_abjad':      text_analysis['total_abjad'],
    }


# ── Aliases للتوافق مع app.py ────────────────────────────────────
process_request_full = process
quick_analyze = search_knowledge
