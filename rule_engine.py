# -*- coding: utf-8 -*-
"""
rule_engine.py — شمس المعارف v17
══════════════════════════════════════════════════════
محرك القواعد — يُطبّق قوانين المخطوطة على كل طلب

كل حاجة = Rule Engine
كل دعاء = Function
كل وفق = Matrix Generator
كل وقت = Trigger Condition
══════════════════════════════════════════════════════
"""

from typing import Dict, List, Optional, Any, Tuple
from knowledge_loader import (
    LETTERS, DIVINE_NAMES, PLANETS, RULES, RITUALS,
    get_dominant_element, get_compatible_elements,
    get_letters_by_element, get_letters_by_type,
    get_rituals_by_purpose, get_wafq_size_for_element,
    validate_timing,
)

# ══════════════════════════════════════════════════════
# 1. تحليل الاسم العميق
# ══════════════════════════════════════════════════════

def analyze_name_deep(name: str) -> Dict[str, Any]:
    """
    تحليل شامل للاسم بقواعد المخطوطة:
    - الطبع الغالب
    - التوزيع العنصري
    - النوع (نوراني/ظلماني/محايد)
    - حرف الميزان إن لزم
    - الكوكب المناسب
    """
    element_counts = {'ناري': 0, 'مائي': 0, 'هوائي': 0, 'ترابي': 0}
    type_counts    = {'نوراني': 0, 'ظلماني': 0}
    letter_details = []

    for char in name:
        info = LETTERS.get(char)
        if info:
            elem = info.get('element', '')
            ltype = info.get('type', '')
            if elem in element_counts:
                element_counts[elem] += info.get('abjad', 1)
            if ltype in type_counts:
                type_counts[ltype] += 1
            letter_details.append({
                'char':    char,
                'element': elem,
                'type':    ltype,
                'abjad':   info.get('abjad', 0),
                'planet':  info.get('planet', ''),
            })

    total = sum(element_counts.values()) or 1
    dominant = max(element_counts, key=element_counts.get)
    dom_type  = 'نوراني' if type_counts['نوراني'] >= type_counts['ظلماني'] else 'ظلماني'

    # الكوكب الغالب
    planet_counts: Dict[str, int] = {}
    for ld in letter_details:
        p = ld.get('planet', '')
        if p:
            planet_counts[p] = planet_counts.get(p, 0) + 1
    dominant_planet = max(planet_counts, key=planet_counts.get) if planet_counts else 'الشمس'

    return {
        'name':             name,
        'dominant_element': dominant,
        'dominant_type':    dom_type,
        'dominant_planet':  dominant_planet,
        'element_breakdown': {k: round(v / total * 100, 1) for k, v in element_counts.items()},
        'type_breakdown':   type_counts,
        'letters':          letter_details,
        'total_abjad':      sum(ld['abjad'] for ld in letter_details),
    }


# ══════════════════════════════════════════════════════
# 2. قاعدة التوافق العنصري
# ══════════════════════════════════════════════════════

def check_elemental_law(
    name1_element: str,
    name2_element: str,
) -> Dict[str, Any]:
    """
    R13: قانون تعارض الطبائع
    يُحدد إن كان الاسمان متوافقان أم لا
    ويقترح حرف الميزان إن لزم
    """
    compat = get_compatible_elements(name1_element)

    if name2_element == name1_element:
        status  = 'match'
        label   = 'تطابق طبيعي — أقوى عمل ممكن'
        mediator = None
    elif name2_element == compat.get('ally'):
        status  = 'ally'
        label   = 'تحالف طبيعي — العمل قوي'
        mediator = None
    elif name2_element == compat.get('neutral'):
        status  = 'neutral'
        label   = 'طبيعتان محايدتان — العمل مقبول'
        mediator = None
    else:
        status  = 'enemy'
        label   = f'تضاد طبيعي ({name1_element} ⟷ {name2_element}) — يحتاج حرف ميزان'
        # نختار حرف الميزان من الطبع المتوسط
        neutral_elem = compat.get('neutral', 'هوائي')
        neutral_letters = get_letters_by_element(neutral_elem)
        mediator = neutral_letters[0] if neutral_letters else 'و'

    return {
        'status':   status,
        'label':    label,
        'mediator': mediator,
        'compatible': status in ('match', 'ally', 'neutral'),
        'strength': {'match': 100, 'ally': 80, 'neutral': 60, 'enemy': 20}.get(status, 50),
    }


# ══════════════════════════════════════════════════════
# 3. اختيار الاسم الحسنى المناسب
# ══════════════════════════════════════════════════════

def select_best_divine_name(
    intent: str,
    element: str,
    name_type: str = 'نوراني',
) -> Optional[Dict]:
    """
    R04-R09: اختيار أفضل اسم حسنى حسب النية والطبع والنوع
    """
    intent_map = {
        'محبة':      ['ودود', 'جميل', 'لطيف', 'حميد'],
        'رزق':       ['رزاق', 'وهاب', 'مغني', 'باسط', 'واجد'],
        'حفظ':       ['حافظ', 'مؤمن', 'مهيمن', 'قوي', 'متين'],
        'شفاء':      ['شافي', 'طيب', 'رؤوف', 'رحيم', 'محيي'],
        'علم':       ['عليم', 'حكيم', 'خبير', 'رشيد', 'مبدئ'],
        'قبول':      ['كريم', 'جواد', 'واجد', 'ماجد', 'حميد'],
        'قهر':       ['قهار', 'قادر', 'مقتدر', 'منتقم', 'جبار'],
        'كشف':       ['ظاهر', 'باطن', 'خبير', 'بصير', 'محيط'],
        'توبة':      ['تواب', 'عفو', 'رحيم', 'غفور', 'غفار'],
        'هيبة':      ['عزيز', 'قهار', 'متكبر', 'جبار', 'عظيم'],
        'جلب':       ['جامع', 'قريب', 'مجيب', 'واسع', 'ودود'],
        'ترحيل':     ['منتقم', 'مانع', 'قهار', 'شديد', 'مقتدر'],
        'إبطال':     ['باطن', 'عفو', 'رحيم', 'حي', 'قيوم'],
        'شهرة':      ['شهيد', 'ظاهر', 'حميد', 'مجيد', 'واجد'],
    }

    candidates = intent_map.get(intent, [])

    # ابحث في قاعدة البيانات
    for candidate in candidates:
        if candidate in DIVINE_NAMES:
            data = DIVINE_NAMES[candidate]
            # تحقق من التوافق العنصري إن أمكن
            return {'name': candidate, **data}

    # إذا لم يوجد محدد، ابحث في الخاصية
    for name, data in DIVINE_NAMES.items():
        prop = data.get('property', '') + data.get('suitable', '')
        if any(word in prop for word in intent.split()):
            return {'name': name, **data}

    return None


# ══════════════════════════════════════════════════════
# 4. توليد تعليمات الطقس
# ══════════════════════════════════════════════════════

def generate_ritual_instructions(
    intent: str,
    name_element: str,
    planet: str,
    abjad: int,
) -> Dict[str, Any]:
    """
    يولّد تعليمات العمل الكاملة بناءً على قواعد المخطوطة:
    - التوقيت المناسب
    - المادة المناسبة
    - عدد التكرار
    - الاتجاه
    - البخور
    """
    planet_data = PLANETS.get(planet, {})

    # R15: الاتجاه
    direction_map = {
        'ناري':  'الشرق',
        'هوائي': 'الشمال',
        'مائي':  'الغرب',
        'ترابي': 'الجنوب',
    }
    direction = direction_map.get(name_element, 'الشرق')

    # عدد التكرار من الجمل
    # R11: الأعداد المثلثة أقوى
    base_count = abjad % 100 or 33
    if base_count % 3 != 0:
        base_count = (base_count // 3 + 1) * 3

    # R07: مركز الوفق
    wafq_center = abjad

    # الطقس المناسب
    matching_rituals = get_rituals_by_purpose(intent)

    # المادة حسب الطبع
    material_map = {
        'ناري':  'ورق أحمر أو نحاس أحمر',
        'مائي':  'ورق أبيض أو فضة',
        'هوائي': 'حرير أخضر أو ذهب',
        'ترابي': 'خشب أو رصاص',
    }

    return {
        'direction':      direction,
        'timing':         f"يوم {planet_data.get('day','—')} في ساعة {planet}",
        'count':          base_count,
        'wafq_center':    wafq_center,
        'wafq_size':      get_wafq_size_for_element(name_element),
        'incense':        planet_data.get('incense', 'العود'),
        'material':       material_map.get(name_element, 'ورق أبيض'),
        'rituals':        matching_rituals[:2],
        'purity_required': True,
        'fast_recommended': intent in ['قهر', 'ترحيل', 'كشف', 'هيبة'],
    }


# ══════════════════════════════════════════════════════
# 5. المحرك الرئيسي — تطبيق كل القواعد
# ══════════════════════════════════════════════════════

def apply_all_rules(
    target_name: str,
    mother_name: str,
    intent: str,
    current_planet: str,
    is_forbidden_hour: bool,
    mansion_ruling: str,
) -> Dict[str, Any]:
    """
    النقطة الرئيسية للـ Rule Engine:
    يطبّق جميع القواعد المستخرجة من المخطوطة ويعطي حكماً شاملاً.
    """
    result: Dict[str, Any] = {
        'approved':  True,
        'score':     100,
        'warnings':  [],
        'boosts':    [],
        'recommendations': [],
    }

    # تحليل الاسمين
    name_analysis   = analyze_name_deep(target_name)
    mother_analysis = analyze_name_deep(mother_name)

    name_elem   = name_analysis['dominant_element']
    mother_elem = mother_analysis['dominant_element']
    name_type   = name_analysis['dominant_type']

    # R13: توافق الطبائع
    compat = check_elemental_law(name_elem, mother_elem)
    if not compat['compatible']:
        result['warnings'].append(compat['label'])
        result['score'] -= 20
        if compat['mediator']:
            result['recommendations'].append(
                f'أضف حرف الميزان «{compat["mediator"]}» في بداية الاسم لموازنة الطبائع'
            )

    # R02-R03-R14: التوقيت
    timing = validate_timing(name_elem, current_planet, is_forbidden_hour, mansion_ruling)
    result['score'] += (timing['score'] - 100) // 2
    result['warnings'].extend(timing['warnings'])
    if not timing['valid']:
        result['approved'] = False

    # R04-R09: التوافق مع النية
    intent_element_map = {
        'محبة': 'مائي', 'جلب': 'مائي', 'قبول': 'ناري', 'حفظ': 'ترابي',
        'كشف': 'هوائي', 'عقد لسان': 'ترابي', 'دخول': 'ناري', 'قهر': 'ناري',
        'إبطال': 'هوائي', 'رزق': 'ترابي', 'شفاء': 'مائي', 'إخفاء': 'هوائي',
        'ترحيل': 'ناري', 'شهرة': 'ناري', 'هيبة': 'ناري',
    }
    intent_elem = intent_element_map.get(intent, name_elem)

    if name_elem == intent_elem:
        result['boosts'].append(f'✅ طبع الاسم ({name_elem}) يتوافق مع طبع النية ({intent}) — قوة مضاعفة')
        result['score'] += 15

    # R08: النوراني للخير، الظلماني للقهر
    dark_intents = {'قهر', 'ترحيل', 'عقد لسان', 'إخفاء'}
    if intent in dark_intents and name_type == 'ظلماني':
        result['boosts'].append('✅ الحروف الظلمانية تناسب هذا النوع من الأعمال')
        result['score'] += 10
    elif intent not in dark_intents and name_type == 'نوراني':
        result['boosts'].append('✅ الحروف النورانية تناسب هذا العمل الخيري')
        result['score'] += 10

    # اسم حسنى مناسب
    best_name = select_best_divine_name(intent, name_elem, name_type)
    if best_name:
        result['recommended_divine_name'] = best_name

    # تعليمات الطقس
    total_abjad = name_analysis['total_abjad'] + mother_analysis['total_abjad']
    result['ritual_instructions'] = generate_ritual_instructions(
        intent, name_elem, current_planet, total_abjad
    )

    # تحليل الاسمين
    result['name_analysis']   = name_analysis
    result['mother_analysis'] = mother_analysis
    result['compatibility']   = compat
    result['score'] = max(0, min(100, result['score']))

    # الحكم النهائي
    if result['score'] >= 80:
        result['verdict'] = 'ممتاز — ظروف مثالية للعمل'
        result['approved'] = True
    elif result['score'] >= 60:
        result['verdict'] = 'جيد — العمل مقبول مع الاحتياطات'
        result['approved'] = True
    elif result['score'] >= 40:
        result['verdict'] = 'متوسط — يُفضَّل التأجيل'
        result['approved'] = True
    else:
        result['verdict'] = 'ضعيف — الظروف غير مناسبة'
        result['approved'] = False

    return result


# ══════════════════════════════════════════════════════
# 6. تحليل نص عربي وتصنيفه
# ══════════════════════════════════════════════════════

def analyze_arabic_text(text: str) -> Dict[str, Any]:
    """
    يحلل نصاً عربياً ويستخرج:
    - الطبع الغالب
    - الكوكب المهيمن
    - النوع (نوراني/ظلماني)
    - الجمل الإجمالي
    """
    total_abjad  = 0
    elem_score: Dict[str, int] = {'ناري': 0, 'مائي': 0, 'هوائي': 0, 'ترابي': 0}
    planet_score: Dict[str, int] = {}
    type_score: Dict[str, int] = {'نوراني': 0, 'ظلماني': 0}

    for char in text:
        info = LETTERS.get(char)
        if info:
            abjad = info.get('abjad', 0)
            total_abjad += abjad
            elem = info.get('element', '')
            if elem in elem_score:
                elem_score[elem] += abjad
            planet = info.get('planet', '')
            if planet:
                planet_score[planet] = planet_score.get(planet, 0) + 1
            ltype = info.get('type', '')
            if ltype in type_score:
                type_score[ltype] += 1

    total_elem = sum(elem_score.values()) or 1
    dominant_elem   = max(elem_score, key=elem_score.get)
    dominant_planet = max(planet_score, key=planet_score.get) if planet_score else 'الشمس'
    dominant_type   = 'نوراني' if type_score['نوراني'] >= type_score['ظلماني'] else 'ظلماني'

    return {
        'text':             text,
        'total_abjad':      total_abjad,
        'dominant_element': dominant_elem,
        'dominant_planet':  dominant_planet,
        'dominant_type':    dominant_type,
        'element_distribution': {
            k: round(v / total_elem * 100, 1) for k, v in elem_score.items()
        },
    }
