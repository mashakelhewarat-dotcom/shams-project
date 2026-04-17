# -*- coding: utf-8 -*-
"""
elemental_balance.py — ميزان الطبائع وحرف الميزان
═══════════════════════════════════════════════════════════════════
يحلل اسم المستخدم واسم أمه، يكشف التضاد العنصري،
ويحقن حرف الميزان تلقائياً عند الحاجة.
المصدر: شمس المعارف الكبرى، الفصل الأول (موازين الطبائع)
═══════════════════════════════════════════════════════════════════
"""

from typing import Dict, List, Optional, Tuple

# ============================================================================
# تصنيف الحروف العربية إلى طبائع
# ============================================================================
ELEMENT_MAP = {
    # ناري
    'ا':'نار','أ':'نار','إ':'نار','آ':'نار','ه':'نار','ة':'نار',
    'ط':'نار','م':'نار','ف':'نار','ش':'نار','ذ':'نار',
    # هوائي
    'ب':'هواء','و':'هواء','ك':'هواء','ص':'هواء',
    'ق':'هواء','ر':'هواء','ت':'هواء',
    # مائي
    'ج':'ماء','ز':'ماء','ح':'ماء','ل':'ماء',
    'ع':'ماء','س':'ماء','ث':'ماء',
    # ترابي
    'د':'تراب','ي':'تراب','ى':'تراب','ن':'تراب',
    'ظ':'تراب','خ':'تراب','ض':'تراب','غ':'تراب',
}

# حرف الميزان لكل حالة تضاد
MEDIATOR_LETTERS = {
    ('نار',  'ماء'):   {'letter':'س', 'reason':'السين مائية تلطّف النار وتجمع الماء'},
    ('ماء',  'نار'):   {'letter':'س', 'reason':'السين مائية تلطّف النار وتجمع الماء'},
    ('تراب', 'هواء'):  {'letter':'م', 'reason':'الميم نارية توازن بين التراب والهواء'},
    ('هواء', 'تراب'):  {'letter':'م', 'reason':'الميم نارية توازن بين الهواء والتراب'},
    ('نار',  'تراب'):  {'letter':'و', 'reason':'الواو هوائي يجمع النار والتراب'},
    ('تراب', 'نار'):   {'letter':'و', 'reason':'الواو هوائي يجمع التراب والنار'},
    ('ماء',  'هواء'):  {'letter':'ل', 'reason':'اللام مائي يجمع الماء والهواء'},
    ('هواء', 'ماء'):   {'letter':'ل', 'reason':'اللام مائي يجمع الهواء والماء'},
}

# ============================================================================
# دوال التحليل
# ============================================================================

def analyze_composition(text: str) -> Dict[str, int]:
    counts = {'نار': 0, 'هواء': 0, 'ماء': 0, 'تراب': 0}
    for ch in (text or ''):
        el = ELEMENT_MAP.get(ch)
        if el:
            counts[el] += 1
    return counts


def get_dominant(counts: Dict[str, int]) -> str:
    total = sum(counts.values())
    if total == 0:
        return 'تراب'
    return max(counts, key=counts.get)


def get_balance(counts: Dict[str, int]) -> Dict:
    total = sum(counts.values())
    if total == 0:
        return {'balanced': True, 'imbalance_score': 0.0}
    avg      = total / 4
    variance = sum((v - avg)**2 for v in counts.values()) / 4
    score    = round(min(1.0, variance / 10), 3)
    return {'balanced': score < 0.3, 'imbalance_score': score}


def detect_elemental_conflict(dom1: str, dom2: str) -> Tuple[bool, Optional[Dict]]:
    key = (dom1, dom2)
    if key in MEDIATOR_LETTERS:
        return True, MEDIATOR_LETTERS[key]
    return False, None


def inject_mediator(text: str, mediator_letter: str,
                    position: str = 'middle') -> str:
    if not mediator_letter:
        return text
    if position == 'start':
        return mediator_letter + text
    if position == 'end':
        return text + mediator_letter
    mid = len(text) // 2
    return text[:mid] + mediator_letter + text[mid:]

# ============================================================================
# الدالة الرئيسية
# ============================================================================

def analyze_user_balance(name: str, mother: str) -> Dict:
    """
    تحليل طبائع الاسم + الأم، كشف التضاد، اقتراح حرف الميزان.
    تُستدعى من app.py في pipeline التنفيذ.
    """
    name_counts   = analyze_composition(name)
    mother_counts = analyze_composition(mother)

    combined = {
        el: name_counts[el] + mother_counts[el]
        for el in ('نار', 'هواء', 'ماء', 'تراب')
    }

    name_dom     = get_dominant(name_counts)
    mother_dom   = get_dominant(mother_counts)
    combined_dom = get_dominant(combined)
    balance      = get_balance(combined)
    conflict, mediator_data = detect_elemental_conflict(name_dom, mother_dom)

    mediator_letter  = mediator_data['letter']  if mediator_data else None
    mediator_reason  = mediator_data['reason']  if mediator_data else None

    if conflict:
        rec = (
            f"⚠️ تضاد بين طبع اسمك ({name_dom}) وطبع اسم أمك ({mother_dom}). "
            f"يُنصح بإضافة حرف الميزان «{mediator_letter}» في الوفق. "
            f"{mediator_reason}."
        )
    elif not balance['balanced']:
        rec = (
            f"⚠️ عدم توازن في الطبائع (درجة {balance['imbalance_score']}). "
            f"الطبع الغالب: {combined_dom}."
        )
    else:
        rec = f"✅ توازن الطبائع جيد. الطبع الغالب: {combined_dom}."

    return {
        'name':            name,
        'mother':          mother,
        'name_dominant':   name_dom,
        'mother_dominant': mother_dom,
        'combined_dominant': combined_dom,
        'combined_counts': combined,
        'balance':         balance,
        'conflict_detected': conflict,
        'mediator_letter': mediator_letter,
        'mediator_reason': mediator_reason,
        'recommendation':  rec,
    }


if __name__ == "__main__":
    tests = [
        ("محمد", "آمنة"),
        ("أحمد", "فاطمة"),
        ("علي",  "زينب"),
    ]
    for n, m in tests:
        r = analyze_user_balance(n, m)
        print(f"{n}/{m}: {r['name_dominant']}/{r['mother_dominant']} "
              f"conflict={r['conflict_detected']} mediator={r['mediator_letter']}")
