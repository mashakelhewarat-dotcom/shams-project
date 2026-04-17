# -*- coding: utf-8 -*-
"""
geomancy_engine.py
═══════════════════════════════════════════════════════════════════
محرك علم الرمل الكامل — يعتمد على قواعد "ميزان العدل"
من شمس المعارف الكبرى للإمام البوني.

⚠️ الخوارزميات هنا محمية — لا تُعدَّل دون مرجع من المخطوطة.
═══════════════════════════════════════════════════════════════════
"""

from typing import List, Dict, Tuple
from shams_data_extended import (
    GEOMANCY_PATTERNS_AR, GEOMANCY_HOUSES,
    GEOMANCY_AUSPICIOUS, GEOMANCY_INAUSPICIOUS, GEOMANCY_ASPECTS,
)

# ============================================================================
# 1. تحويل الإشارات → أمهات
# ============================================================================

def signals_to_mothers(signals: Dict) -> List[List[int]]:
    """
    ⚠️ خوارزمية محمية — تحويل إشارات المستخدم إلى 4 أمهات.
    كل أم = 4 قيم (زوج=0 / فرد=1).

    الإشارات المتوقعة:
        typing_speed  — متوسط الوقت بين الحروف (ms)
        char_count    — عدد الحروف
        word_count    — عدد الكلمات
        hesitation    — عدد التوقفات أو الحذف
        hour, minute, second — وقت الإدخال
    """
    ts  = signals.get("typing_speed", 100)
    cc  = signals.get("char_count",   1)
    wc  = signals.get("word_count",   1)
    hes = signals.get("hesitation",   0)
    h   = signals.get("hour",         0)
    m   = signals.get("minute",       0)
    s   = signals.get("second",       0)

    oe = lambda n: n % 2   # زوج=0، فرد=1

    # كل صف يمثل أماً، كل عمود يمثل سطراً منها
    raw = [
        [oe(ts  + j) for j in range(4)],   # الأم الأولى  ← سرعة الكتابة
        [oe(cc  + j) for j in range(4)],   # الأم الثانية ← عدد الحروف
        [oe(wc + hes + j) for j in range(4)], # الأم الثالثة ← كلمات + تردد
        [oe(h + m + s + j) for j in range(4)], # الأم الرابعة ← الوقت
    ]
    return raw

# ============================================================================
# 2. توليد التخت الكامل
# ============================================================================

def _pattern_to_name(pattern: List[int]) -> str:
    """ابحث عن اسم الشكل من نمطه الثنائي."""
    for name, p in GEOMANCY_PATTERNS_AR.items():
        if p == pattern:
            return name
    return "غير معروف"

def _xor(p1: List[int], p2: List[int]) -> List[int]:
    """دمج شكلين بـ XOR."""
    return [p1[i] ^ p2[i] for i in range(4)]

def generate_full_chart(mothers: List[List[int]]) -> Dict[int, Dict]:
    """
    ⚠️ خوارزمية محمية — توليد التخت الرملي الكامل (16 بيتاً).

    الترتيب:
        1-4  : الأمهات
        5-8  : البنات (تُستخرج من صفوف الأمهات)
        9-12 : الحفيدات (XOR أمهات × بنات)
        13   : الشاهد الأيمن  (XOR حفيدة 1 × 2)
        14   : الشاهد الأيسر  (XOR حفيدة 3 × 4)
        15   : القاضي          (XOR شاهد أيمن × أيسر)
        16   : العاقبة         (XOR قاضي × أم1)
    """
    chart: Dict[int, Dict] = {}

    # الأمهات
    for i in range(4):
        chart[i + 1] = {"name": _pattern_to_name(mothers[i]),
                        "pattern": mothers[i], "type": "mother"}

    # البنات — كل بنت = عمود من الأمهات
    daughters = [[mothers[m][row] for m in range(4)] for row in range(4)]
    for i in range(4):
        chart[5 + i] = {"name": _pattern_to_name(daughters[i]),
                        "pattern": daughters[i], "type": "daughter"}

    # الحفيدات
    grandchildren = [_xor(mothers[i], daughters[i]) for i in range(4)]
    for i in range(4):
        chart[9 + i] = {"name": _pattern_to_name(grandchildren[i]),
                        "pattern": grandchildren[i], "type": "grandchild"}

    # الشاهدان
    w_right = _xor(grandchildren[0], grandchildren[1])
    w_left  = _xor(grandchildren[2], grandchildren[3])
    chart[13] = {"name": _pattern_to_name(w_right), "pattern": w_right, "type": "witness_right"}
    chart[14] = {"name": _pattern_to_name(w_left),  "pattern": w_left,  "type": "witness_left"}

    # القاضي
    judge = _xor(w_right, w_left)
    chart[15] = {"name": _pattern_to_name(judge), "pattern": judge, "type": "judge"}

    # العاقبة
    consequence = _xor(judge, mothers[0])
    chart[16] = {"name": _pattern_to_name(consequence), "pattern": consequence, "type": "consequence"}

    return chart

# ============================================================================
# 3. تحليل التخت
# ============================================================================

def analyze_chart(chart: Dict[int, Dict]) -> Dict:
    """
    تحليل التخت الرملي الكامل.
    المخرجات:
        houses       — قائمة الـ16 بيتاً مع التفسير
        aspects      — المناظرات بين البيوت
        time_data    — تقسيم الأشكال (ماضي/حاضر/مستقبل)
        hidden_intent— نص الضمير المستخرج
        summary      — ملخص (طالع، قاضي، عاقبة)
    """
    # البيوت
    houses = []
    for n in range(1, 17):
        fig  = chart[n]
        info = GEOMANCY_HOUSES[n]
        houses.append({
            "number":         n,
            "name":           info["name"],
            "meaning":        info["meaning"],
            "figure_name":    fig["name"],
            "figure_pattern": fig["pattern"],
            "is_auspicious":  fig["name"] in GEOMANCY_AUSPICIOUS,
            "is_inauspicious":fig["name"] in GEOMANCY_INAUSPICIOUS,
            "element":        info["element"],
        })

    # المناظرات
    aspects = []
    for i in range(1, 17):
        for j in range(i + 1, 17):
            diff = abs(i - j)
            if diff in GEOMANCY_ASPECTS:
                aspects.append({
                    "house1":   i,
                    "house2":   j,
                    "aspect":   GEOMANCY_ASPECTS[diff]["name"],
                    "meaning":  GEOMANCY_ASPECTS[diff]["meaning"],
                })

    # الزمن
    time_data: Dict[str, list] = {"past": [], "present": [], "future": []}
    for n in range(1, 17):
        label = GEOMANCY_HOUSES[n]["time"]
        time_data[label].append({
            "house":      n,
            "figure":     chart[n]["name"],
            "house_name": GEOMANCY_HOUSES[n]["name"],
        })

    # كشف الضمير
    asc   = chart[1]["name"]
    soul  = chart[13]["name"]
    bal   = chart[15]["name"]

    if asc == soul:
        intent = f"السائل يُظهر ما في ضميره: {asc} يطابق {soul}."
    elif asc == bal:
        intent = f"الميزان يؤكد صدق التخت: {asc} يطابق {bal}."
    elif asc in GEOMANCY_AUSPICIOUS and soul in GEOMANCY_INAUSPICIOUS:
        intent = f"الظاهر سعد ({asc})، لكن الباطن نحس ({soul}) — هناك خوف لا يُظهره السائل."
    elif asc in GEOMANCY_INAUSPICIOUS and soul in GEOMANCY_AUSPICIOUS:
        intent = f"الظاهر نحس ({asc})، لكن الباطن سعد ({soul}) — السائل متفائل أكثر مما يبدو."
    else:
        intent = f"الضمير مرتبط بـ {bal}، وهو يشير إلى حاجة خفية."

    return {
        "houses":        houses,
        "aspects":       aspects,
        "time_data":     time_data,
        "hidden_intent": intent,
        "summary": {
            "ascendant":   asc,
            "judge":       chart[15]["name"],
            "consequence": chart[16]["name"],
        },
    }

# ============================================================================
# 4. التوصية من التحليل
# ============================================================================

def get_recommendation(analysis: Dict) -> Dict:
    """
    اقتراح اسم حسنى + خادم + وفق + طلسم
    بناءً على تحليل التخت.
    """
    s = analysis["summary"]
    asc, judge, cons = s["ascendant"], s["judge"], s["consequence"]

    if (asc in GEOMANCY_AUSPICIOUS and
            judge in GEOMANCY_AUSPICIOUS and
            cons  in GEOMANCY_AUSPICIOUS):
        return {
            "asma": "الفتاح", "servant": "تمخيائيل",
            "wafq": "3x3", "talisman": "al_fattah",
            "advice": "الأمر مفتوح — يمكن البدء فوراً.",
        }
    elif (asc  in GEOMANCY_INAUSPICIOUS or
          judge in GEOMANCY_INAUSPICIOUS or
          cons  in GEOMANCY_INAUSPICIOUS):
        return {
            "asma": "القهار", "servant": "حقيائيل",
            "wafq": "4x4 (تكسير)", "talisman": "al_qahhar",
            "advice": "هناك عوائق — استخدم القهر والبطش.",
        }
    else:
        return {
            "asma": "الودود", "servant": "ودديائيل",
            "wafq": "3x3", "talisman": "al_wadud",
            "advice": "تحتاج إلى المحبة والتأليف.",
        }

# ============================================================================
# 5. الدالة الرئيسية: إشارات → نتيجة كاملة
# ============================================================================

def process_signals(signals: Dict) -> Dict:
    """إشارات المستخدم → تخت كامل → تحليل → توصية."""
    mothers        = signals_to_mothers(signals)
    chart          = generate_full_chart(mothers)
    analysis       = analyze_chart(chart)
    recommendation = get_recommendation(analysis)
    return {
        "mothers":        mothers,
        "chart":          chart,
        "analysis":       analysis,
        "recommendation": recommendation,
    }


# ============================================================================
# ✦ v11.0 — استخراج الضمير المتقدم (Pointer Tracking)
# المصدر: شمس المعارف الكبرى، الفصل السابع (أحكام البيوت)
# ⚠️ لا تُعدَّل دون مرجع من المخطوطة
# ============================================================================

# دلالات البيوت الفلكية الـ12 (داخل التخت الرملي)
HOUSE_MEANINGS_DAMIR = {
    1:  {'subject': 'السائل نفسه',           'detail': 'ذات السائل وهيئته وشخصه'},
    2:  {'subject': 'المال والرزق',           'detail': 'ضميره متعلق بمال أو رزق أو مكسب'},
    3:  {'subject': 'الإخوة والتنقل',         'detail': 'يفكر في أخ أو سفر أو رسالة'},
    4:  {'subject': 'الآباء والعقارات',       'detail': 'همّه متعلق بأب أو منزل أو أرض'},
    5:  {'subject': 'الأولاد والأفراح',       'detail': 'يفكر في ولد أو زواج أو فرح'},
    6:  {'subject': 'الأمراض والأسقام',       'detail': 'ضميره متعلق بمرض أو هم أو خوف خفي'},
    7:  {'subject': 'الزواج والشركاء',        'detail': 'يسأل في حقيقته عن زواج أو شريك'},
    8:  {'subject': 'الموت والميراث',         'detail': 'يفكر في موت أو ميراث أو مال غائب'},
    9:  {'subject': 'السفر والدين والعلم',    'detail': 'نيته متعلقة بسفر بعيد أو علم أو دين'},
    10: {'subject': 'الملك والسلطة والجاه',  'detail': 'يريد الجاه أو المنصب أو السلطة'},
    11: {'subject': 'الأصدقاء والأمل',       'detail': 'همّه في صديق أو أمل مرتقب'},
    12: {'subject': 'الأعداء والخصوم',       'detail': 'يخفي خوفاً من عدو أو حاسد'},
}

def extract_hidden_intent_advanced(chart: Dict[int, Dict]) -> Dict:
    """
    ✦ استخراج الضمير المتقدم — v11.0
    ══════════════════════════════════
    الخوارزمية (Pointer Tracking من الفصل السابع):
    1. أخذ شكل الطالع (البيت رقم 1)
    2. البحث عن نفس الشكل في البيوت 2-15
    3. أول تطابق = موضوع الضمير الحقيقي
    4. إذا لم يوجد تطابق كامل → أقرب شكل بـ Hamming distance

    قاعدة البوني: "من ظهر طالعه في بيت من البيوت، فاعلم أن ضميره في موضوع ذلك البيت."
    """
    ascendant_pattern = chart[1]['pattern']
    ascendant_name    = chart[1]['name']

    # 1. بحث عن تطابق كامل في البيوت 2-15
    exact_match = None
    for house_num in range(2, 16):
        if chart[house_num]['pattern'] == ascendant_pattern:
            exact_match = house_num
            break

    if exact_match:
        # تطابق كامل
        house_idx = ((exact_match - 1) % 12) + 1
        meaning   = HOUSE_MEANINGS_DAMIR.get(house_idx, {})
        return {
            'method':       'تطابق كامل',
            'matched_house': exact_match,
            'house_subject': meaning.get('subject', ''),
            'house_detail':  meaning.get('detail', ''),
            'ascendant':     ascendant_name,
            'confidence':    'عالية',
            'text': (
                f"ضمير السائل متعلق بـ {meaning.get('subject','')}. "
                f"{meaning.get('detail','')}. "
                f"(الطالع {ascendant_name} ظهر في البيت {exact_match})"
            ),
        }

    # 2. إذا لم يوجد تطابق — Hamming Distance (أقرب شكل)
    def hamming(p1: List[int], p2: List[int]) -> int:
        return sum(a != b for a, b in zip(p1, p2))

    best_house = None
    best_dist  = 5  # أقصى مسافة مقبولة = 1 فارق
    for house_num in range(2, 16):
        d = hamming(ascendant_pattern, chart[house_num]['pattern'])
        if d < best_dist:
            best_dist  = d
            best_house = house_num

    if best_house and best_dist == 1:
        house_idx = ((best_house - 1) % 12) + 1
        meaning   = HOUSE_MEANINGS_DAMIR.get(house_idx, {})
        return {
            'method':        'تشابه قريب (فارق حرف واحد)',
            'matched_house':  best_house,
            'house_subject':  meaning.get('subject', ''),
            'house_detail':   meaning.get('detail', ''),
            'ascendant':      ascendant_name,
            'hamming_dist':   best_dist,
            'confidence':     'متوسطة',
            'text': (
                f"ضمير السائل يميل نحو {meaning.get('subject','')}. "
                f"{meaning.get('detail','')}. "
                f"(فارق درجة واحدة — ثقة متوسطة)"
            ),
        }

    # 3. لا تطابق — استخدام القاضي والعاقبة
    judge_house    = 15
    judge_meaning  = HOUSE_MEANINGS_DAMIR.get((judge_house % 12) or 12, {})
    return {
        'method':       'استنباط من القاضي',
        'matched_house': judge_house,
        'house_subject': judge_meaning.get('subject', ''),
        'house_detail':  judge_meaning.get('detail', ''),
        'ascendant':     ascendant_name,
        'confidence':    'منخفضة — تحتاج مزيداً من البيانات',
        'text': (
            f"لم يتطابق الطالع مع بيت محدد — الضمير غير واضح. "
            f"القاضي يشير إلى {judge_meaning.get('subject','')}. "
            f"يُنصح بإعادة طرح السؤال بدقة أكثر."
        ),
    }


# ============================================================================
# V19 Addition: GeomancyEngine Class (from V18 engines/geomancy_engine.py)
# ============================================================================
import random as _random

class GeomancyEngine:
    """محرك علم الرمل الكامل — يولد الأشكال ويحللها (V18 Addition)."""
    def __init__(self):
        try:
            from knowledge.geomancy import GEOMANCY_SHAPES
            self.shapes = GEOMANCY_SHAPES
        except ImportError:
            self.shapes = {}

    def generate_random_points(self, lines: int = 4):
        points = []
        for _ in range(lines):
            num_points = _random.randint(1, 16)
            points.append([_random.choice([0, 1]) for _ in range(num_points)])
        return points

    def reduce_points(self, pts):
        return len(pts) % 2

    def points_to_shape(self, points_line):
        reduced = [self.reduce_points(points_line[i:i+4]) for i in range(0, len(points_line), 4)]
        while len(reduced) < 4:
            reduced.append(0)
        return reduced[:4]

    def generate_mothers(self, points):
        mothers = []
        for i in range(4):
            line = []
            for j in range(4):
                v = points[i][j] if i < len(points) and j < len(points[i]) else 0
                line.append(v % 2)
            mothers.append(line)
        return mothers

    def generate_daughters(self, mothers):
        return [[mothers[j][i] for j in range(4)] for i in range(4)]

    def generate_nieces(self, mothers, daughters):
        nieces = []
        for i in range(0, 4, 2):
            for j in range(0, 4, 2):
                niece = [
                    (mothers[i][j]   + mothers[i+1][j])   % 2,
                    (mothers[i][j+1] + mothers[i+1][j+1]) % 2,
                    (daughters[i][j]   + daughters[i+1][j])   % 2,
                    (daughters[i][j+1] + daughters[i+1][j+1]) % 2,
                ]
                nieces.append(niece)
        return nieces

    def generate_witnesses(self, nieces):
        rw = [(nieces[0][k] + nieces[1][k]) % 2 for k in range(4)]
        lw = [(nieces[2][k] + nieces[3][k]) % 2 for k in range(4)]
        return rw, lw

    def generate_judge(self, rw, lw):
        return [(rw[k] + lw[k]) % 2 for k in range(4)]

    def _get_shape_name(self, pattern):
        for name, data in self.shapes.items():
            if data.get('pattern') == pattern:
                return name
        return 'غير معروف'

    def generate_full_chart(self, points=None):
        if points is None:
            points = self.generate_random_points()
        mothers   = self.generate_mothers(points)
        daughters = self.generate_daughters(mothers)
        nieces    = self.generate_nieces(mothers, daughters)
        rw, lw    = self.generate_witnesses(nieces)
        judge     = self.generate_judge(rw, lw)
        return {
            'points': points,
            'mothers': mothers,   'mothers_names':   [self._get_shape_name(m) for m in mothers],
            'daughters': daughters,'daughters_names': [self._get_shape_name(d) for d in daughters],
            'nieces': nieces,     'nieces_names':    [self._get_shape_name(n) for n in nieces],
            'right_witness': rw,  'right_witness_name': self._get_shape_name(rw),
            'left_witness': lw,   'left_witness_name':  self._get_shape_name(lw),
            'judge': judge,       'judge_name': self._get_shape_name(judge),
        }

    def analyze_chart(self, chart):
        judge_name = chart.get('judge_name', '')
        judge_data = self.shapes.get(judge_name, {})
        auspicious = judge_data.get('auspicious', False)
        return {
            'judge': judge_name, 'auspicious': auspicious,
            'meaning': judge_data.get('meaning', ''),
            'recommendation': 'يُستحسن العمل' if auspicious else 'يُتجنب العمل في هذا الوقت'
        }
