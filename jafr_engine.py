# -*- coding: utf-8 -*-
"""
jafr_engine.py — شمس المعارف v19
═══════════════════════════════════════════════════════════════════
محرك الجفر الكامل المدمج — الفصل الحادي والعشرون من شمس المعارف الكبرى
استنطاق الحروف والأعداد بنظام الجفر البسيط والمركب + الجفر التاريخي (الفتن)

⚠️ لا تُعدَّل الخوارزميات دون مرجع من المخطوطة.
═══════════════════════════════════════════════════════════════════
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

# ============================================================================
# 1. حروف الجفر الثمانية والعشرون
# ============================================================================
JAFR_LETTERS = list('أبجدهوزحطيكلمنسعفصقرشتثخذضظغ')

JAFR_ABJAD = {
    'أ': 1,  'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'ة': 5,
    'و': 6,  'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10, 'ى': 10,
    'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70,
    'ف': 80, 'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400,
    'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
}

# ============================================================================
# 2. جدول الحروف والمنازل والكواكب (الفصل الحادي والعشرون)
# ============================================================================
JAFR_TABLE = {
    'أ': {'mansion': 'الشرطين',    'planet': 'زحل',     'nature': 'ناري',  'number': 1,   'class': 'نوراني'},
    'ب': {'mansion': 'البطين',     'planet': 'المشتري', 'nature': 'ترابي', 'number': 2,   'class': 'نوراني'},
    'ج': {'mansion': 'الثريا',     'planet': 'المريخ',  'nature': 'هوائي', 'number': 3,   'class': 'ظلماني'},
    'د': {'mansion': 'الدبران',    'planet': 'الشمس',   'nature': 'ناري',  'number': 4,   'class': 'نوراني'},
    'ه': {'mansion': 'الهقعة',     'planet': 'الزهرة',  'nature': 'هوائي', 'number': 5,   'class': 'نوراني'},
    'و': {'mansion': 'الهنعة',     'planet': 'عطارد',   'nature': 'مائي',  'number': 6,   'class': 'نوراني'},
    'ز': {'mansion': 'الذراع',     'planet': 'القمر',   'nature': 'هوائي', 'number': 7,   'class': 'ظلماني'},
    'ح': {'mansion': 'النثرة',     'planet': 'زحل',     'nature': 'مائي',  'number': 8,   'class': 'نوراني'},
    'ط': {'mansion': 'الطرف',      'planet': 'المشتري', 'nature': 'ناري',  'number': 9,   'class': 'نوراني'},
    'ي': {'mansion': 'الجبهة',     'planet': 'المريخ',  'nature': 'ترابي', 'number': 10,  'class': 'نوراني'},
    'ك': {'mansion': 'الخراتان',   'planet': 'الشمس',   'nature': 'هوائي', 'number': 20,  'class': 'نوراني'},
    'ل': {'mansion': 'الصرفة',     'planet': 'الزهرة',  'nature': 'هوائي', 'number': 30,  'class': 'نوراني'},
    'م': {'mansion': 'العواء',     'planet': 'عطارد',   'nature': 'ترابي', 'number': 40,  'class': 'نوراني'},
    'ن': {'mansion': 'السماك',     'planet': 'القمر',   'nature': 'مائي',  'number': 50,  'class': 'نوراني'},
    'س': {'mansion': 'الغفر',      'planet': 'زحل',     'nature': 'ترابي', 'number': 60,  'class': 'ظلماني'},
    'ع': {'mansion': 'الزبانان',   'planet': 'المشتري', 'nature': 'هوائي', 'number': 70,  'class': 'نوراني'},
    'ف': {'mansion': 'الإكليل',    'planet': 'المريخ',  'nature': 'ناري',  'number': 80,  'class': 'نوراني'},
    'ص': {'mansion': 'القلب',      'planet': 'الشمس',   'nature': 'ناري',  'number': 90,  'class': 'ظلماني'},
    'ق': {'mansion': 'الشولة',     'planet': 'الزهرة',  'nature': 'ترابي', 'number': 100, 'class': 'نوراني'},
    'ر': {'mansion': 'النعائم',    'planet': 'عطارد',   'nature': 'هوائي', 'number': 200, 'class': 'نوراني'},
    'ش': {'mansion': 'البلدة',     'planet': 'القمر',   'nature': 'ترابي', 'number': 300, 'class': 'نوراني'},
    'ت': {'mansion': 'سعد الذابح', 'planet': 'زحل',     'nature': 'ترابي', 'number': 400, 'class': 'ظلماني'},
    'ث': {'mansion': 'سعد بلع',    'planet': 'المشتري', 'nature': 'مائي',  'number': 500, 'class': 'نوراني'},
    'خ': {'mansion': 'سعد السعود', 'planet': 'المريخ',  'nature': 'مائي',  'number': 600, 'class': 'ظلماني'},
    'ذ': {'mansion': 'سعد الأخبية','planet': 'الشمس',   'nature': 'مائي',  'number': 700, 'class': 'نوراني'},
    'ض': {'mansion': 'الفرغ الأول','planet': 'الزهرة',  'nature': 'مائي',  'number': 800, 'class': 'نوراني'},
    'ظ': {'mansion': 'الفرغ الثاني','planet':'عطارد',   'nature': 'هوائي', 'number': 900, 'class': 'ظلماني'},
    'غ': {'mansion': 'بطن الحوت',  'planet': 'القمر',   'nature': 'مائي',  'number': 1000,'class': 'ظلماني'},
}

# ============================================================================
# 3. تفسيرات الجفر الصغير
# ============================================================================
JAFR_FIRST_LETTER_READINGS = {
    'أ': 'بداية قوية ونور — الطالع مواتٍ للبدء.',
    'ب': 'خير وبركة — تأمل قبل الخطوة القادمة.',
    'ج': 'حركة وتحوّل — الجمع والفصل.',
    'د': 'ثبات ودوام — لا عجلة.',
    'ه': 'روحانية وهيبة — العمل في الهدوء.',
    'و': 'مودة واتصال — خير في العلاقات.',
    'ز': 'تحذير وتأخير — الصبر لازم.',
    'ح': 'حفظ وحماية — التحصين أولاً.',
    'ط': 'طيب وصلاح — وقت مناسب للأعمال الخيرية.',
    'ي': 'يسر وسهولة — السبيل ممهّد.',
    'ك': 'كرامة وجاه — الطلب من الأكابر.',
    'ل': 'لطف ولين — المودة والمحبة.',
    'م': 'مراد ومقصود — تحقق الغاية.',
    'ن': 'نور وهداية — الكشف قريب.',
    'س': 'سعة ورزق — يبشر بالوفرة.',
    'ع': 'علم وعرفان — وقت التأمل والدراسة.',
    'ف': 'فتح وفرج — يبشر بالانفراج.',
    'ص': 'صبر وصمود — الحل في التأني.',
    'ق': 'قوة وقدرة — التصميم ينجح.',
    'ر': 'رفعة وريادة — السعي محمود.',
    'ش': 'شرف وشموخ — مكانة مرتفعة.',
    'ت': 'توبة وتراجع — مراجعة الخطط.',
    'ث': 'ثمرة وثواب — نتيجة العمل تأتي.',
    'خ': 'خفاء وخصومة — الحذر واجب.',
    'ذ': 'ذكاء وذكر — التفكير قبل الفعل.',
    'ض': 'ضعف وضيق — وقت الاستعداد لا الفعل.',
    'ظ': 'ظفر وظهور — النصر بعد الجهد.',
    'غ': 'غيب وغموض — الأمر ملتبس — انتظر.',
}

# ============================================================================
# 4. هيكل الجفر الكبير وجداوله (V18 Addition)
# ============================================================================
JAFR_STRUCTURE = {
    'base_letters': 28, 'pages_per_letter': 28, 'lines_per_page': 28,
    'houses_per_line': 28, 'letters_per_house': 28, 'total_pages': 784,
    'total_lines': 21952, 'total_houses': 614656, 'total_letters': 17210368
}

JAFR_TABLES_DATA = [
    {'id': 1, 'name': 'جدول الحروف الأصلية', 'data': list(range(1, 29))},
    {'id': 2, 'name': 'جدول الأعداد المقلوبة', 'data': list(range(28, 0, -1))},
    {'id': 3, 'name': 'جدول الحروف النورانية', 'data': [1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181,6765,10946,17711,28657,46368,75025,121393,196418,317811,514229]}
]

JAFR_SYMBOLIC_NAMES = [
    'شعيب', 'سميع', 'شيث', 'حزقيل', 'قابيل', 'طوس', 'دمياط', 'نابلس',
    'طرابلس', 'طرسوس', 'حلب', 'حمص', 'دمشق', 'تفارقا', 'احر', 'مواد',
    'محمد', 'أحمد', 'موسى', 'الياس', 'يوسف', 'محمد المهدى', 'الملك المبين',
    'الله', 'وكيل', 'موسى', 'بلقيس', 'سليمان', 'جليل', 'نخم', 'قابض',
    'المص', 'كهيعص', 'طه', 'حم', 'عسق', 'ن', 'القلم'
]

# ============================================================================
# 5. الفتن والأحداث الكبرى (V18 Addition)
# ============================================================================
FITAN_EVENTS = [
    {'name': 'سقوط بغداد',                 'jafar_number': 312,  'description': 'يحكمها 39 خليفة ثم تنقرض وتغلق 24 عاماً'},
    {'name': 'ظهور نجم عظيم',               'jafar_number': 360,  'description': 'علامة فلكية لبدء الأحداث الكبرى'},
    {'name': 'سيطرة الإفرنج على السواحل',   'jafar_number': 583,  'description': 'سقوط عكا والرملة البيضاء والقدس'},
    {'name': 'ظهور طغاة',                   'jafar_number': 666,  'description': 'يقصون الشوارب ويطيلون اللحى ويستبيحون الحرام'},
    {'name': 'معارك الشام',                 'jafar_number': 777,  'description': 'حروب طاحنة في حلب وحمص وحماة'},
    {'name': 'خروج المهدي',                 'jafar_number': 888,  'description': 'يملك البلاد ويقسم المال بالسوية'},
    {'name': 'خروج الدجال',                 'jafar_number': 999,  'description': 'يكون خروجه من طبرستان ويتبعه يهود أصبهان'},
    {'name': 'يأجوج ومأجوج',                'jafar_number': 1111, 'description': 'يشربون بحيرة طبرية ويهلكهم الله بالدود'},
]

CITY_RUIN_CAUSES = {
    'مصر': 'النيل', 'اليمن': 'الجراد', 'الأندلس': 'السيف', 'سمرقند': 'السيف',
    'المدينة المنورة': 'الجوع', 'مكة': 'الطاعون', 'صنعاء': 'الطاعون',
    'فارس': 'القحط', 'بلخ': 'الماء', 'ترمذ': 'الطاعون', 'مرو': 'الرمل',
    'الموصل': 'الريح الشمالية', 'ديار بكر': 'الريح الشمالية', 'السند': 'الريح الشمالية'
}

# ============================================================================
# 6. الدوال المساعدة
# ============================================================================
def _abjad_to_letter(val: int) -> str:
    keys = sorted(JAFR_ABJAD.keys(), key=lambda c: JAFR_ABJAD[c])
    return min(keys, key=lambda c: abs(JAFR_ABJAD[c] - (val % 1001 or 1)))

def _compress_to_28(num: int) -> int:
    if num <= 0:
        num = abs(num) or 1
    while num > 28:
        num = sum(int(d) for d in str(num)) or 1
    return num

def _reduce_to_single_digit(number: int) -> int:
    while number > 9:
        number = sum(int(d) for d in str(number))
    return number

def calculate_abjad(text: str) -> int:
    return sum(JAFR_ABJAD.get(c, 0) for c in text)

# ============================================================================
# 7. الجفر الصغير — الدوال الرئيسية (V17 Original)
# ============================================================================
def calc_jafr_simple(name: str, intent: str = '') -> dict:
    """الجفر الصغير — استنطاق الاسم والنية."""
    text = (name + intent).strip()
    if not text:
        return {'error': 'أدخل الاسم أو النص'}
    jummal = sum(JAFR_ABJAD.get(c, 0) for c in text)
    letter_idx = (_compress_to_28(jummal) - 1) % len(JAFR_LETTERS)
    natiq = JAFR_LETTERS[letter_idx]
    natiq_data = JAFR_TABLE.get(natiq, {})
    first = next((c for c in name if c in JAFR_TABLE), 'أ')
    rasd_num = jummal % 7
    return {
        'name': name, 'intent': intent, 'jummal': jummal,
        'letter_idx': letter_idx + 1, 'natiq': natiq, 'natiq_data': natiq_data,
        'natiq_reading': JAFR_FIRST_LETTER_READINGS.get(natiq, ''),
        'first_letter': first,
        'first_reading': JAFR_FIRST_LETTER_READINGS.get(first, ''),
        'best_day': ['السبت','الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة'][rasd_num],
        'summary': (
            f"جُمَّل «{name}» = {jummal} | الحرف الناطق: {natiq} | "
            f"المنزل: {natiq_data.get('mansion','')} | الكوكب: {natiq_data.get('planet','')} | "
            f"الطبع: {natiq_data.get('nature','')} | {JAFR_FIRST_LETTER_READINGS.get(natiq,'')}"
        ),
        'quote': "قال البوني: 'الجفر الصغير هو استنطاق الحروف بأعدادها الجُمَّلية، تُسقط على دائرة الثمانية والعشرين حرفاً، فيُعرف به حكم الوقت ومآل الأمر'. (الفصل الحادي والعشرون، ص 558)"
    }

def calc_jafr_compound(name1: str, name2: str) -> dict:
    """الجفر المركب — دمج اسمين."""
    j1 = sum(JAFR_ABJAD.get(c, 0) for c in name1)
    j2 = sum(JAFR_ABJAD.get(c, 0) for c in name2)
    combined = j1 + j2
    diff = abs(j1 - j2)
    union_letter = JAFR_LETTERS[(_compress_to_28(combined) - 1) % 28]
    diff_letter  = JAFR_LETTERS[(_compress_to_28(diff or 1) - 1) % 28]
    union_data = JAFR_TABLE.get(union_letter, {})
    n1_data = JAFR_TABLE.get(next((c for c in name1 if c in JAFR_TABLE), 'أ'), {})
    n2_data = JAFR_TABLE.get(next((c for c in name2 if c in JAFR_TABLE), 'أ'), {})
    affinity = 0
    if n1_data.get('nature') == n2_data.get('nature'): affinity += 40
    if n1_data.get('planet') == n2_data.get('planet'):  affinity += 30
    if n1_data.get('class') == n2_data.get('class'):    affinity += 20
    if (j1 + j2) % 7 in (0, 1, 5):                     affinity += 10
    return {
        'name1': name1, 'jummal1': j1, 'name2': name2, 'jummal2': j2,
        'combined': combined, 'diff': diff,
        'union_letter': union_letter, 'union_planet': union_data.get('planet', ''),
        'union_nature': union_data.get('nature', ''),
        'union_reading': JAFR_FIRST_LETTER_READINGS.get(union_letter, ''),
        'diff_letter': diff_letter,
        'diff_reading': JAFR_FIRST_LETTER_READINGS.get(diff_letter, ''),
        'affinity_score': min(100, affinity),
        'affinity_label': (
            'توافق عالٍ جداً' if affinity >= 80 else 'توافق جيد' if affinity >= 60 else
            'توافق متوسط' if affinity >= 40 else 'توافق ضعيف'
        ),
        'summary': (
            f"جمع «{name1}»({j1}) و«{name2}»({j2}) = {combined} | "
            f"حرف الاتحاد: {union_letter} ({union_data.get('nature','')}) | "
            f"درجة التوافق: {min(100,affinity)}%"
        ),
    }

def get_jafr_letter_info(letter: str) -> dict:
    """معلومات تفصيلية عن حرف واحد من الجفر."""
    data = JAFR_TABLE.get(letter)
    if not data:
        return {'error': f'الحرف "{letter}" غير موجود في جدول الجفر'}
    return {
        'letter': letter, 'abjad_value': JAFR_ABJAD.get(letter, 0),
        **data, 'reading': JAFR_FIRST_LETTER_READINGS.get(letter, ''),
        'quote': "قال البوني في استنطاق الحروف: 'كل حرف له منزلة وكوكب وطبع، فإذا عرفتها عرفت حكم صاحبه ومآل أمره'. (الفصل الأول، ص 18)"
    }

def get_all_jafr_table() -> List[dict]:
    """إرجاع جدول الجفر الكامل."""
    return [
        {'letter': l, 'value': JAFR_ABJAD.get(l, 0), **JAFR_TABLE.get(l, {})}
        for l in JAFR_LETTERS
    ]

# ============================================================================
# 8. الجفر التاريخي — حسابات الملوك والفتن (V18 Additions)
# ============================================================================
def calculate_reign_duration(king_name: str, accession_year: int, hijri_year: int = None) -> Dict[str, Any]:
    """حساب مدة حكم الملك بالجفر."""
    abjad = calculate_abjad(king_name)
    letter_count = len(king_name)
    if letter_count == 4:
        base = abjad - 2
        squared = base * base
        if hijri_year: squared -= hijri_year
    elif letter_count == 3:
        base = letter_count * letter_count
        squared = base * base
        if hijri_year: squared -= hijri_year
    elif letter_count == 5 and len(set(king_name)) < len(king_name):
        base = abjad - 2
        squared = base * base + abjad
        if hijri_year: squared -= hijri_year
    else:
        squared = abjad * abjad
        if hijri_year: squared -= hijri_year
    years = squared // 360
    remainder = squared % 360
    months = remainder // 30
    days = remainder % 30
    return {
        'king_name': king_name, 'abjad': abjad, 'letter_count': letter_count,
        'accession_year': hijri_year, 'calculated_years': years,
        'calculated_months': months, 'calculated_days': days,
        'total_days': years * 360 + months * 30 + days,
        'method': 'جفري (ضرب الاسم في نفسه وطرح التاريخ)'
    }

def calculate_reign_using_qahqara(king_name: str, century: int = 700) -> dict:
    """تطبيق خوارزمية القهقرة لحساب مدة ولاية ملك."""
    abjad = calculate_abjad(king_name)
    doubled = abjad * 2
    total = doubled + abjad
    after_subtract = total - century
    years = after_subtract // 100
    remainder = after_subtract % 100
    months = remainder // 10
    days = remainder % 10
    return {
        'king': king_name, 'abjad': abjad,
        'total_before_subtract': total,
        'years': years, 'months': months, 'days': days,
        'method': 'القاعدة الجفرية (القهقرة)'
    }

def predict_event(event_name: str, base_year: int) -> Dict[str, Any]:
    """التنبؤ بالأحداث من الجفر."""
    abjad = calculate_abjad(event_name)
    reduced = _reduce_to_single_digit(abjad)
    event_types = {
        1: 'بداية دولة أو عهد جديد', 2: 'حرب أو صراع داخلي',
        3: 'ظهور فتنة أو بدعة',      4: 'كارثة طبيعية أو وباء',
        5: 'تغيير في السلطة أو انقلاب', 6: 'ازدهار ورخاء',
        7: 'خراب أو هزيمة',           8: 'فتح أو نصر',
        9: 'علامة كبرى أو حدث غيبي'
    }
    offsets = {1:7, 2:40, 3:132, 4:187, 5:312, 6:432, 7:570, 8:583, 9:627}
    predicted_year = base_year + offsets.get(reduced, 0)
    return {
        'event_name': event_name, 'abjad': abjad, 'reduced': reduced,
        'event_type': event_types.get(reduced, 'غير محدد'),
        'predicted_year_hijri': predicted_year,
        'predicted_year_gregorian': int(predicted_year * 0.97 + 622),
        'confidence': 'متوسطة' if reduced in [3,4,5] else 'ضعيفة'
    }

def predict_city_fate(city_name: str) -> Dict[str, Any]:
    """التنبؤ بمصير مدينة من الجفر."""
    abjad = calculate_abjad(city_name)
    reduced = _reduce_to_single_digit(abjad)
    cause = CITY_RUIN_CAUSES.get(city_name, 'غير محدد')
    return {
        'city': city_name, 'abjad': abjad, 'reduced': reduced,
        'cause_of_ruin': cause,
        'warning': f'احذر من {cause} في آخر الزمان' if cause != 'غير محدد' else 'لا توجد معلومات محددة'
    }

def get_fitan_event(jafar_number: int) -> Dict[str, Any]:
    """الحصول على حدث فتنة بالرقم الجفري."""
    for event in FITAN_EVENTS:
        if event['jafar_number'] == jafar_number:
            return event
    return {}

def get_jafr_table(table_id: int) -> Dict[str, Any]:
    """الحصول على جدول جفر بالرقم."""
    for table in JAFR_TABLES_DATA:
        if table['id'] == table_id:
            return table
    return {}

def get_jafr_symbolic_name(index: int) -> str:
    if 0 <= index < len(JAFR_SYMBOLIC_NAMES):
        return JAFR_SYMBOLIC_NAMES[index]
    return ""
