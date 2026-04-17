# -*- coding: utf-8 -*-
"""
astro_gatekeeper.py — حارس الوقت السيادي
═══════════════════════════════════════════════════════════════════
يمنح أو يرفض التصريح بناءً على:
  - الساعة الكوكبية الحالية
  - المنزلة القمرية
  - توافقها مع النية والمسار

يستخدم Skyfield إن كانت متاحة، وإلا يُقرّب (6 ص / 6 م).
═══════════════════════════════════════════════════════════════════
"""

from datetime import datetime as dt, timedelta
from typing import Dict, Optional

# ── Skyfield (اختياري) ───────────────────────────────────────────
try:
    from skyfield import api as _sky
    from skyfield import almanac as _alm
    _SKYFIELD = True
except ImportError:
    _SKYFIELD = False

# ============================================================================
# بيانات الكواكب والأيام
# ============================================================================
PLANET_ORDER    = ['زحل','المشتري','المريخ','الشمس','الزهرة','عطارد','القمر']
PLANET_ORDER_EN = ['saturn','jupiter','mars','sun','venus','mercury','moon']

DAY_START_PLANET = {
    0: 'الشمس',   # الأحد
    1: 'القمر',   # الاثنين
    2: 'المريخ',  # الثلاثاء
    3: 'عطارد',   # الأربعاء
    4: 'المشتري', # الخميس
    5: 'الزهرة',  # الجمعة
    6: 'زحل',     # السبت
}

LUNAR_MANSIONS = {
    1:  {"name":"الشرطين",    "element":"نار",  "ruling":"نحسة"},
    2:  {"name":"البطين",     "element":"تراب", "ruling":"سعيدة"},
    3:  {"name":"الثريا",     "element":"هواء", "ruling":"مسعودة"},
    4:  {"name":"الدبران",    "element":"ماء",  "ruling":"نحسة"},
    5:  {"name":"الهقعة",     "element":"نار",  "ruling":"مسعودة"},
    6:  {"name":"الهنعة",     "element":"تراب", "ruling":"ممتزجة"},
    7:  {"name":"الذراع",     "element":"هواء", "ruling":"سعيدة"},
    8:  {"name":"النثرة",     "element":"ماء",  "ruling":"مسعودة"},
    9:  {"name":"الطرفة",     "element":"نار",  "ruling":"نحسة"},
    10: {"name":"الجبهة",     "element":"تراب", "ruling":"سعيدة"},
    11: {"name":"الزبرة",     "element":"هواء", "ruling":"مسعودة"},
    12: {"name":"الصرفة",     "element":"ماء",  "ruling":"سعيدة"},
    13: {"name":"العواء",     "element":"نار",  "ruling":"مسعودة"},
    14: {"name":"السماك",     "element":"تراب", "ruling":"نحسة"},
    15: {"name":"الغفر",      "element":"هواء", "ruling":"سعيدة جداً"},
    16: {"name":"الزباني",    "element":"ماء",  "ruling":"ممتزجة"},
    17: {"name":"الإكليل",    "element":"نار",  "ruling":"ممتزجة"},
    18: {"name":"القلب",      "element":"تراب", "ruling":"نحسة"},
    19: {"name":"الشولة",     "element":"هواء", "ruling":"نحسة"},
    20: {"name":"النعائم",    "element":"ماء",  "ruling":"سعيدة"},
    21: {"name":"البلدة",     "element":"نار",  "ruling":"مسعودة"},
    22: {"name":"سعد الذابح","element":"تراب", "ruling":"نحسة"},
    23: {"name":"سعد بلع",   "element":"هواء", "ruling":"ممتزجة"},
    24: {"name":"سعد السعود","element":"ماء",  "ruling":"سعيدة"},
    25: {"name":"سعد الأخبية","element":"نار",  "ruling":"نحسة"},
    26: {"name":"فرغ المقدم","element":"تراب", "ruling":"مسعودة"},
    27: {"name":"فرغ المؤخر","element":"هواء", "ruling":"ممتزجة"},
    28: {"name":"الرشاء",     "element":"ماء",  "ruling":"سعيدة"},
}

INTENT_PLANET_COMPAT = {
    "attraction": ["الزهرة","المشتري","القمر"],
    "control":    ["المريخ","زحل","الشمس"],
    "separation": ["المريخ","زحل"],
    "protection": ["القمر","عطارد","المشتري"],
    "knowledge":  ["عطارد","الشمس","المشتري"],
    "wealth":     ["المشتري","الزهرة","الشمس"],
    "chaos":      [],
    # ── جديد: أغراض الأسماء الحسنى ─────────────────────────────
    "محبة وزواج":  ["الزهرة","القمر","المشتري"],
    "رزق ومال":   ["المشتري","الزهرة","الشمس"],
    "حماية وحفظ": ["القمر","المشتري","عطارد"],
    "علم ودراسة": ["عطارد","الشمس","المشتري"],
    "شفاء ومرض":  ["القمر","الزهرة","المشتري"],
    "هيبة وسلطة": ["الشمس","المريخ","المشتري"],
    "قهر وانتقام":["المريخ","زحل"],
    "توبة وغفران":["المشتري","القمر","الزهرة"],
    "طاقة وهمة":  ["الشمس","المريخ","المشتري"],
    "صبر وثبات":  ["زحل","المشتري","القمر"],
}

# شروط شرف الكواكب للأسماء الحسنى — مستخرجة من المخطوطة
ASMA_PLANET_EXALTATION = {
    'شرف القمر':    {
        'planet': 'القمر',
        'best_day': 'الاثنين',
        'asma': ['الرحمن','المهيمن','السميع','الودود','الحليم','الرقيب','الباسط'],
        'condition': 'القمر في السرطان أو حوت غير محترق',
    },
    'شرف المريخ':   {
        'planet': 'المريخ',
        'best_day': 'الثلاثاء',
        'asma': ['العزيز','الجبار','القهار','القوي','المنتقم','المتكبر','القادر'],
        'condition': 'المريخ في الجدي غير محترق',
    },
    'شرف المشتري':  {
        'planet': 'المشتري',
        'best_day': 'الخميس',
        'asma': ['المهيمن','المؤمن','القدوس','الرزاق','الغني','المغني','الصمد'],
        'condition': 'المشتري في السرطان أو القوس',
    },
    'شرف زحل':      {
        'planet': 'زحل',
        'best_day': 'السبت',
        'asma': ['الغفار','القابض','الخافض','المذل','الصبور','المتين'],
        'condition': 'زحل في الميزان غير محترق',
    },
    'شرف عطارد':    {
        'planet': 'عطارد',
        'best_day': 'الأربعاء',
        'asma': ['العليم','الحكيم','الخبير','اللطيف','البديع'],
        'condition': 'عطارد في السنبلة غير محترق',
    },
    'شرف الشمس':    {
        'planet': 'الشمس',
        'best_day': 'الأحد',
        'asma': ['الملك','الرافع','المعز','النور','الفتاح','الظاهر','العظيم'],
        'condition': 'الشمس في الحمل — شرف الشمس الأعظم',
    },
    'شرف الزهرة':   {
        'planet': 'الزهرة',
        'best_day': 'الجمعة',
        'asma': ['الودود','الرحيم','المصور','البديع','الرؤوف'],
        'condition': 'الزهرة في الثور أو الجدي غير محترقة',
    },
}

# ============================================================================
# حساب الشروق والغروب
# ============================================================================

def _get_sunrise_sunset_approx(now: dt):
    return now.replace(hour=6, minute=0, second=0), now.replace(hour=18, minute=0, second=0)


def _get_sunrise_sunset_skyfield(now: dt, lat: float = 30.04, lon: float = 31.24):
    if not _SKYFIELD:
        return _get_sunrise_sunset_approx(now)
    try:
        d_naive = now.replace(tzinfo=None) if now.tzinfo else now
        ts  = _sky.load.timescale()
        eph = _sky.load('de421.bsp')
        obs = _sky.wgs84.latlon(lat, lon)
        t0  = ts.utc(d_naive.year, d_naive.month, d_naive.day, 0, 0, 0)
        t1  = ts.utc(d_naive.year, d_naive.month, d_naive.day, 23, 59, 59)
        f   = _alm.sunrise_sunset(eph, obs)
        times, events = _alm.find_discrete(t0, t1, f)
        sunrise = sunset = None
        for t, e in zip(times, events):
            d = t.utc_datetime().replace(tzinfo=None)
            if e == 1 and sunrise is None: sunrise = d
            if e == 0 and sunset  is None: sunset  = d
        if sunrise and sunset:
            return sunrise, sunset
    except Exception:
        pass
    return _get_sunrise_sunset_approx(now)


def get_planetary_hour_info(now: dt, lat: float = 30.04, lon: float = 31.24) -> Dict:
    # نضمن naive datetime لتجنب خطأ المقارنة
    now = now.replace(tzinfo=None) if now.tzinfo else now
    sunrise, sunset = _get_sunrise_sunset_skyfield(now, lat, lon)

    if now < sunrise:
        prev_sunset = sunset - timedelta(days=1)
        start, end, part = prev_sunset, sunrise, "night"
    elif sunrise <= now < sunset:
        start, end, part = sunrise, sunset, "day"
    else:
        next_sunrise = sunrise + timedelta(days=1)
        start, end, part = sunset, next_sunrise, "night"

    period = max((end - start).total_seconds(), 1)
    hour_len = period / 12.0
    elapsed  = (now - start).total_seconds()
    hour_num = min(12, max(1, int(elapsed // hour_len) + 1))

    islamic_weekday = (now.weekday() + 1) % 7   # 0=الأحد
    start_planet = DAY_START_PLANET[islamic_weekday]
    start_idx    = PLANET_ORDER.index(start_planet)
    planet_idx   = (start_idx + hour_num - 1) % 7
    planet       = PLANET_ORDER[planet_idx]

    return {
        "hour_number":  hour_num,
        "planet":       planet,
        "day_part":     part,
        "hour_length":  round(hour_len / 60, 1),
        "sunrise":      sunrise.isoformat(),
        "sunset":       sunset.isoformat(),
        "weekday":      islamic_weekday,
        "method":       "skyfield" if _SKYFIELD else "approximate",
    }


def get_lunar_mansion(now: dt) -> Dict:
    now = now.replace(tzinfo=None) if now.tzinfo else now
    ref = dt(2000, 1, 6)
    lunar_day = ((now - ref).days % 28) + 1
    m = dict(LUNAR_MANSIONS.get(lunar_day, LUNAR_MANSIONS[1]))
    m["lunar_day"] = lunar_day
    return m

# ============================================================================
# منطق المنع / المنح
# ============================================================================

def check_clearance(intent_type: str, path_name: str,
                    current_planet: str, lunar_mansion: Dict) -> Dict:
    # فوضى → رفض تلقائي
    if intent_type == "chaos":
        return {
            "granted": False,
            "reason":  "❌ النية غير واضحة (فوضى). وضّح هدفك أولاً.",
            "suggested_wait": None,
        }

    # فحص الكوكب
    compat = INTENT_PLANET_COMPAT.get(intent_type, [])
    if compat and current_planet not in compat:
        return {
            "granted": False,
            "reason": (
                f"❌ رفض كوني — كوكب {current_planet} لا يتوافق مع نية '{intent_type}'. "
                f"الكواكب المناسبة: {' أو '.join(compat[:3])}"
            ),
            "suggested_wait": f"انتظر حتى ساعة {compat[0] if compat else 'مناسبة'}",
        }

    # فحص المنزلة القمرية
    ruling = lunar_mansion.get("ruling", "")
    if "نحسة" in ruling and intent_type in ["attraction", "wealth"]:
        return {
            "granted": False,
            "reason": (
                f"❌ المنزلة القمرية ({lunar_mansion['name']}) نحسة. "
                "لا تصلح لأعمال المحبة أو الرزق الآن."
            ),
            "suggested_wait": "انتظر دخول منزلة سعيدة (الثريا، الهقعة، النعائم...)",
        }

    # حماية في منزلة نحسة — مسموح مع تحذير
    if path_name == "shielding" and "نحسة" in ruling:
        return {
            "granted": True,
            "reason": (
                f"⚠️ تصريح مشروط — المنزلة ({lunar_mansion['name']}) نحسة، "
                "لكن أعمال الحماية قد تكون فعّالة. يُنصح بالتحصين المضاعف."
            ),
            "suggested_wait": None,
        }

    # كل شيء مناسب
    return {
        "granted": True,
        "reason": (
            f"✅ تصريح إلهي — كوكب {current_planet} متوافق، "
            f"والمنزلة {lunar_mansion['name']} مناسبة."
        ),
        "suggested_wait": None,
    }

# ============================================================================
# الدالة الرئيسية
# ============================================================================

def astro_gatekeeper(intent_type: str, path_name: str,
                     current_time: Optional[dt] = None,
                     lat: float = 30.04, lon: float = 31.24) -> Dict:
    """
    الحارس الفلكي الرئيسي — يُستدعى من app.py قبل التنفيذ.
    يمنح أو يرفض التصريح بناءً على الوقت والمنزلة والنية.
    """
    from datetime import timezone as _tz
    now = (current_time or dt.now(_tz.utc)).replace(tzinfo=None)
    hour_info     = get_planetary_hour_info(now, lat, lon)
    lunar_mansion = get_lunar_mansion(now)
    clearance     = check_clearance(intent_type, path_name,
                                    hour_info["planet"], lunar_mansion)
    return {
        "granted":       clearance["granted"],
        "reason":        clearance["reason"],
        "suggested_wait":clearance["suggested_wait"],
        "timestamp":     now.isoformat(),
        "planetary_hour":hour_info,
        "lunar_mansion": lunar_mansion,
        "intent":        intent_type,
        "path":          path_name,
    }


if __name__ == "__main__":
    r = astro_gatekeeper("attraction", "influence")
    print(f"Granted: {r['granted']}")
    print(f"Planet:  {r['planetary_hour']['planet']}")
    print(f"Mansion: {r['lunar_mansion']['name']}")
    print(f"Reason:  {r['reason']}")
