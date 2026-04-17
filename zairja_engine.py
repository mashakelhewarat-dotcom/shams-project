# -*- coding: utf-8 -*-
"""
zairja_engine.py — v11.0
═══════════════════════════════════════════════════════════════════
محرك الزايرجة الدائرية الكاملة + قاعدة اللقط والوثب
المصدر: شمس المعارف الكبرى، الفصل الثاني والثالث (البوني)

✦ يشمل:
  - الزايرجة الخطية الأصلية (محفوظة بالكامل)
  - الزايرجة الدائرية الجديدة (أوتار الأبراج + التعشيق + اللقط)
  - جفر الزمام المدمج (حرفا اليوم والطالع)

⚠️ خوارزميات محمية — لا تُعدَّل دون مرجع من المخطوطة.
═══════════════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, List
from datetime import datetime
from shams_data_extended import (
    ZAIRJA_ALPHABET, ZAIRJA_CONSTANTS, ZAIRJA_ABJAD,
    ZODIAC_STRINGS, LEAP_BY_HOUR,
    DAY_LETTERS, ASCENDANT_LETTERS,
)

# ============================================================================
# 1. الأدوات الأساسية (محفوظة من v10)
# ============================================================================

def text_to_abjad(text: str) -> int:
    """تحويل النص إلى قيمة جُمَّل."""
    return sum(ZAIRJA_ABJAD.get(ch, 0) for ch in text)


def number_to_letters(num: int, length: int = 4) -> str:
    """
    ⚠️ خوارزمية محمية — تحويل رقم إلى سلسلة حروف بنظام الزايرجة.
    يستخدم modulo 28 مع ثوابت المخطوطة في كل دورة.
    """
    result = []
    for i in range(length):
        idx = num % 28
        result.append(ZAIRJA_ALPHABET[idx])
        num = num // 28 + ZAIRJA_CONSTANTS[i % len(ZAIRJA_CONSTANTS)]
    return ''.join(result)


def approximate_ascendant(hour: int, minute: int) -> int:
    """تقريب درجة الطالع من الوقت (كل ساعتين ≈ 30 درجة)."""
    return (hour * 60 + minute) * 360 // (24 * 60)


def ask(question: str, ascendant_degree: int = 0) -> Optional[str]:
    """
    ⚠️ خوارزمية محمية — دالة الاستفسار الأصلية (محفوظة من v10).
    """
    if not question:
        return None
    total = text_to_abjad(question) + ascendant_degree
    answer_raw = number_to_letters(total, length=4)
    if any(w in answer_raw for w in ['نعم', 'اجل', 'حسن', 'بلى', 'نح']):
        return "نعم"
    elif any(w in answer_raw for w in ['لا', 'لم', 'لن', 'ليس', 'لأ']):
        return "لا"
    elif any(w in answer_raw for w in ['رب', 'عسى', 'قد', 'لعل', 'أشك']):
        return "ربما"
    elif any(w in answer_raw for w in ['انتظر', 'بعد', 'غدا', 'لاحق', 'وقت']):
        return "مؤجل"
    else:
        return f"الجواب المستنطق: {answer_raw}"


# ============================================================================
# 2. الزايرجة الدائرية — v11.0
# ⚠️ خوارزمية جديدة مستمدة من الفصل الثاني (أوتار الأبراج)
# ============================================================================

def _get_zodiac_string(total: int) -> tuple:
    """
    توجيه الطلب: يحسب البرج المستهدف بـ modulo 12
    ويسحب الوتر الحرفي الخاص به.
    القاعدة: Total % 12 → رقم البرج (1-12)
    """
    zodiac_num = (total % 12) or 12
    string = ZODIAC_STRINGS.get(zodiac_num, ZODIAC_STRINGS[1])
    return zodiac_num, string


def _interleave(seq1: List[str], seq2: List[str]) -> List[str]:
    """
    التعشيق: دمج سلسلتين بالتبادل (حرف من هنا وحرف من هنا).
    ⚠️ هذه هي خطوة بناء المصفوفة الدائرية.
    """
    result = []
    max_len = max(len(seq1), len(seq2))
    for i in range(max_len):
        if i < len(seq1):
            result.append(seq1[i])
        if i < len(seq2):
            result.append(seq2[i])
    return result


def _loqt(matrix: List[str], leap: int) -> List[str]:
    """
    ⚠️ قاعدة اللقط والوثب — الفصل الثالث من شمس المعارف.
    لا تُقرأ المصفوفة بالتسلسل. يُقفز بـ (leap) حروف ويُؤخذ ما بعدها.
    leap يتحدد من رقم الساعة الكوكبية الحالية.
    المثال: leap=3 → خذ [0]، اقفز 3، خذ [4]، اقفز 3، خذ [8]...
    """
    if not matrix or leap < 1:
        return matrix[:8]
    result = []
    idx = 0
    visited = set()
    while len(result) < 8 and len(visited) < len(matrix):
        result.append(matrix[idx % len(matrix)])
        visited.add(idx % len(matrix))
        idx += leap + 1
    return result


def _letters_to_phrase(letters: List[str]) -> str:
    """
    تحويل الحروف الملتقطة إلى عبارة مقفاة مستنطقة.
    يستخدم قاموس تفسيري داخلي لتحويل الحروف لمعانٍ.
    """
    LETTER_MEANINGS = {
        'أ': 'أمر', 'ب': 'بشرى', 'ج': 'جمع', 'د': 'دوام',
        'ه': 'هناء', 'و': 'وصال', 'ز': 'زوال', 'ح': 'حفظ',
        'ط': 'طيب', 'ي': 'يسر', 'ك': 'كرم', 'ل': 'لطف',
        'م': 'مراد', 'ن': 'نور', 'س': 'سعة', 'ع': 'علو',
        'ف': 'فتح', 'ص': 'صبر', 'ق': 'قوة', 'ر': 'رفعة',
        'ش': 'شرف', 'ت': 'تمكين', 'ث': 'ثبات', 'خ': 'خير',
        'ذ': 'ذكاء', 'ض': 'ضياء', 'ظ': 'ظفر', 'غ': 'غنى',
    }
    words = [LETTER_MEANINGS.get(l, l) for l in letters if l in LETTER_MEANINGS]
    if len(words) >= 4:
        return f"{words[0]} وَ{words[1]} مع {words[2]}، ويتحقق {words[3]}"
    elif words:
        return ' وَ'.join(words)
    return ''.join(letters)


def circular_zairja(question: str, hour_number: int = 1,
                    ascendant_degree: int = 0) -> Dict:
    """
    ✦ الزايرجة الدائرية الكاملة — v11.0
    ═══════════════════════════════════════════
    الخطوات (من الفصل الثاني والثالث من شمس المعارف):
    1. حساب جُمَّل السؤال + درجة الطالع
    2. توجيه الطلب → البرج المستهدف وسحب وتره
    3. التعشيق: دمج حروف السؤال مع حروف الوتر
    4. قاعدة اللقط: تصفية المصفوفة بقفزات من الساعة الكوكبية
    5. تكوين العبارة المستنطقة
    """
    if not question:
        return {'error': 'السؤال مطلوب'}

    # 1. الجُمَّل الكلي
    q_abjad = text_to_abjad(question)
    total   = q_abjad + ascendant_degree

    # 2. البرج والوتر
    zodiac_num, zodiac_str = _get_zodiac_string(total)

    # 3. التعشيق (سؤال + وتر البرج)
    question_letters = [c for c in question if c in ZAIRJA_ABJAD]
    zodiac_letters   = list(zodiac_str)
    matrix = _interleave(question_letters, zodiac_letters)

    # 4. قاعدة اللقط (leap من رقم الساعة)
    leap   = LEAP_BY_HOUR.get(hour_number, 3)
    picked = _loqt(matrix, leap)

    # 5. العبارة المستنطقة
    phrase = _letters_to_phrase(picked)

    ZODIAC_NAMES = {
        1:'الحمل', 2:'الثور', 3:'الجوزاء', 4:'السرطان',
        5:'الأسد', 6:'السنبلة', 7:'الميزان', 8:'العقرب',
        9:'القوس', 10:'الجدي', 11:'الدلو', 12:'الحوت',
    }

    return {
        'question':          question,
        'q_abjad':           q_abjad,
        'total':             total,
        'target_zodiac':     zodiac_num,
        'zodiac_name':       ZODIAC_NAMES.get(zodiac_num, ''),
        'zodiac_string':     zodiac_str,
        'matrix_size':       len(matrix),
        'leap_step':         leap,
        'picked_letters':    ''.join(picked),
        'answer_phrase':     phrase,
        'method':            'زايرجة دائرية — أوتار الأبراج + قاعدة اللقط',
        'source':            'شمس المعارف الكبرى، الفصل الثاني والثالث',
    }


# ============================================================================
# 3. جفر الزمام المدمج مع اليوم والطالع — v11.0
# ⚠️ تحديث: يضيف حرفي اليوم والطالع كـ Salt في بداية ونهاية السطر
# ============================================================================

def _get_day_letter(weekday: int) -> str:
    """حرف اليوم الكوكبي من جدول DAY_LETTERS."""
    return DAY_LETTERS.get(weekday, 'أ')


def _get_ascendant_letter(degree: int) -> str:
    """حرف الطالع: كل 30 درجة = حرف من دائرة الـ28."""
    idx = int(degree / 12.857) % 28  # 360/28 ≈ 12.857
    return ASCENDANT_LETTERS[idx]


def _interleave_permutation(chars: List[str]) -> List[str]:
    """
    ⚠️ خوارزمية التكسير المتكررة:
    أخذ الحرف الأخير، ثم الأول، ثم ما قبل الأخير، ثم الثاني...
    حتى تنتهي الحروف.
    """
    if len(chars) <= 1:
        return chars
    result = []
    left, right = 0, len(chars) - 1
    toggle = False
    while left <= right:
        if toggle:
            result.append(chars[left])
            left += 1
        else:
            result.append(chars[right])
            right -= 1
        toggle = not toggle
    return result


def advanced_jafr_zamam(name: str, intent: str = '',
                         weekday: int = None,
                         ascendant_degree: int = 0) -> Dict:
    """
    ✦ جفر الزمام المتقدم — v11.0
    ══════════════════════════════════
    يضيف حرفي اليوم والطالع كـ Salt في بداية ونهاية السطر،
    ثم يطبق دورة التكسير 28 مرة، ثم يضيف "ملح الدرجة 29".

    المصدر: الفصل الحادي والعشرون، شمس المعارف الكبرى.
    """
    now = datetime.now()
    if weekday is None:
        weekday = (now.weekday() + 2) % 7  # weekday بنظام شمس المعارف

    # حرفا اليوم والطالع
    day_letter = _get_day_letter(weekday)
    asc_letter = _get_ascendant_letter(ascendant_degree)

    # بناء السطر الأصلي: حرف اليوم + اسم + نية + حرف الطالع
    base_text  = day_letter + name + intent + asc_letter
    base_chars = [c for c in base_text if c in ZAIRJA_ABJAD or c in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي']

    # دورة التكسير 28 مرة
    current = base_chars[:]
    for cycle in range(28):
        current = _interleave_permutation(current)

    # ملح الدرجة 29: ناتج المجموع % 29 يُحدد حرف Salt إضافي
    total_val = text_to_abjad(name + intent)
    salt_idx  = total_val % 29
    salt_char = ASCENDANT_LETTERS[salt_idx % 28]
    current.append(salt_char)

    # الجواب النهائي: أول 7 حروف من الناتج
    zamam_letters = ''.join(current[:7])
    zamam_abjad   = text_to_abjad(zamam_letters)

    return {
        'name':             name,
        'intent':           intent,
        'day_letter':       day_letter,
        'ascendant_letter': asc_letter,
        'base_text':        base_text,
        'cycles':           28,
        'salt_char':        salt_char,
        'zamam_letters':    zamam_letters,
        'zamam_abjad':      zamam_abjad,
        'zamam_reduced':    zamam_abjad % 28 or 28,
        'source':           'الفصل الحادي والعشرون — شمس المعارف الكبرى',
        'note':             f'حرف اليوم: {day_letter} | حرف الطالع: {asc_letter} | ملح الدرجة 29: {salt_char}',
    }


# ============================================================================
# 4. full_zairja_reading — موحّدة (خطية + دائرية + زمام)
# ============================================================================

def full_zairja_reading(question: str, hour: int = 0, minute: int = 0) -> Dict:
    """
    قراءة زايرجة كاملة تجمع:
    - الزايرجة الخطية الأصلية (محفوظة)
    - الزايرجة الدائرية الجديدة (أوتار + لقط)
    - الزمام المتقدم
    """
    now = datetime.now()
    asc = approximate_ascendant(int(hour or now.hour), int(minute or now.minute))
    weekday = (now.weekday() + 2) % 7

    # من app.py نحصل على hour_number — نستخدم تقريب بسيط هنا
    hour_number = max(1, min(12, int(hour or now.hour) % 12 or 12))

    # الزايرجة الخطية (v10 — محفوظة)
    total_linear = text_to_abjad(question) + asc
    raw_letters  = number_to_letters(total_linear, length=4)
    answer_linear = ask(question, asc)

    # الزايرجة الدائرية (v11)
    circular = circular_zairja(question, hour_number, asc)

    # الزمام المتقدم (v11)
    zamam = advanced_jafr_zamam(question, '', weekday, asc)

    return {
        # خطية (v10 — محفوظة)
        'question':         question,
        'abjad_value':      text_to_abjad(question),
        'ascendant_degree': asc,
        'combined_total':   total_linear,
        'raw_letters':      raw_letters,
        'answer':           answer_linear,
        # دائرية (v11)
        'circular':         circular,
        # زمام (v11)
        'zamam':            zamam,
        # الجواب الموحّد
        'final_answer': {
            'linear':   answer_linear,
            'circular': circular.get('answer_phrase', ''),
            'zamam':    zamam.get('zamam_letters', ''),
        },
    }

# ============================================================================
# V19 Addition: إضافات الزايرجة من V18 (أنظمة جديدة)
# ============================================================================

# بيانات الزايرجة الدائرية
_ZAIRJA_ZODIAC_STRINGS = {
    'الحمل': 'ابجدهوزحطيكلمنسعفصقرشتثخذظغش',
    'الثور': 'بجدهوزحطيكلمنسعفصقرشتثخذظغشا',
    'الجوزاء': 'جدهوزحطيكلمنسعفصقرشتثخذظغشاب',
    'السرطان': 'دهوزحطيكلمنسعفصقرشتثخذظغشابج',
    'الأسد': 'هوزحطيكلمنسعفصقرشتثخذظغشابجد',
    'السنبلة': 'وزحطيكلمنسعفصقرشتثخذظغشابجده',
    'الميزان': 'زحطيكلمنسعفصقرشتثخذظغشابجدهو',
    'العقرب': 'حطيكلمنسعفصقرشتثخذظغشابجدهوز',
    'القوس': 'طيكلمنسعفصقرشتثخذظغشابجدهوزح',
    'الجدي': 'يكلمنسعفصقرشتثخذظغشابجدهوزحط',
    'الدلو': 'كلمنسعفصقرشتثخذظغشابجدهوزحطي',
    'الحوت': 'لمنسعفصقرشتثخذظغشابجدهوزحطيك'
}

_ZAIRJA_ZODIAC_BASES = {
    'الحمل':   {'letter': 'ب', 'number': 21, 'wafq': 'كهيعص'},
    'الثور':   {'letter': 'ط', 'number': 89, 'wafq': 'مثلث'},
    'الجوزاء': {'letter': 'ي', 'number': 32, 'wafq': 'مربع'},
    'السرطان': {'letter': 'ط', 'number': 25, 'wafq': 'مسدس'},
    'الأسد':   {'letter': 'ح', 'number': 21, 'wafq': 'مسبع'},
    'السنبلة': {'letter': 'ر', 'number': 14, 'wafq': 'مربع'},
    'الميزان': {'letter': 'و', 'number': 14, 'wafq': 'مثمن'},
    'العقرب':  {'letter': None, 'number': 90, 'wafq': 'متسع'},
    'القوس':   {'letter': 'ج', 'number': 2,  'wafq': 'مثلث'},
    'الجدي':   {'letter': 'ح', 'number': 12, 'wafq': 'مربع'},
    'الدلو':   {'letter': 'ب', 'number': 2,  'wafq': 'مثمن'},
    'الحوت':   {'letter': 'ا', 'number': 20, 'wafq': 'مسبع'},
}

_QUTB_STRING = "سؤال عظيم الخلق حرت فصن اذا غرائب شك ضبطه الجد مثلا"
_QUTB_CLEAN  = ''.join(_QUTB_STRING.split())
_ELEMENT_DROP_VALUES = {'نار': 99, 'هواء': 1313, 'ماء': 1010, 'تراب': 1616}


def _get_zodiac_from_date(d) -> str:
    month, day = d.month, d.day
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return 'الحمل'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20): return 'الثور'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20): return 'الجوزاء'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22): return 'السرطان'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22): return 'الأسد'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22): return 'السنبلة'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22): return 'الميزان'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21): return 'العقرب'
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21): return 'القوس'
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19): return 'الجدي'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18): return 'الدلو'
    else: return 'الحوت'


def _letters_to_numbers_v18(text: str):
    from jafr_engine import JAFR_ABJAD
    return [JAFR_ABJAD.get(c, 0) for c in text if c in JAFR_ABJAD]


def _reduce_num(num: int) -> int:
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num


def zairja_center(question: str, seeker_name: str = '', d=None) -> dict:
    """الزايرجة المركزية — القانون الأول (V18 Addition)."""
    from datetime import datetime as _dt
    if d is None: d = _dt.now()
    from jafr_engine import calculate_abjad as _abjad
    q_abjad = _abjad(question)
    n_abjad = _abjad(seeker_name) if seeker_name else 0
    zodiac = _get_zodiac_from_date(d)
    zodiac_base = _ZAIRJA_ZODIAC_BASES.get(zodiac, {})
    zodiac_string = _ZAIRJA_ZODIAC_STRINGS.get(zodiac, '')
    combined = question + seeker_name + zodiac_string[:20] + _QUTB_CLEAN
    numbers = _letters_to_numbers_v18(combined)
    total = sum(numbers)
    for _ in range(7):
        for drop in _ELEMENT_DROP_VALUES.values():
            if total > drop: total -= drop
    remainder = _reduce_num(total)
    answers = [
        "نعم، الأمر يتحقق قريباً ببركة الله",
        "الأمر يحتاج إلى صبر وتأنٍ",
        "لا، الوقت غير مناسب، انتظر علامة",
        "ربما، اعقد العزم وتوكل على الله",
        "نعم، ولكن بعد جهد وتعب",
        "الأمر متردد، استخر الله",
    ]
    answer = answers[remainder % len(answers)]
    return {
        'method': 'المركز (القانون الأول)', 'question': question,
        'seeker_name': seeker_name, 'abjad': q_abjad,
        'zodiac': zodiac, 'zodiac_string': zodiac_string[:30],
        'remainder': remainder, 'answer': answer,
        'advice': 'استخر ساعة القمر أو المشتري' if remainder in [1,3,5] else 'تجنب ساعة زحل والمريخ'
    }


def get_zodiac_string_v18(zodiac: str) -> str:
    return _ZAIRJA_ZODIAC_STRINGS.get(zodiac, '')


def get_zodiac_base_v18(zodiac: str) -> dict:
    return _ZAIRJA_ZODIAC_BASES.get(zodiac, {})


def get_qutb_string() -> str:
    return _QUTB_STRING
