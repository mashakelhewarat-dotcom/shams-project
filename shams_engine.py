# -*- coding: utf-8 -*-
"""
shams_engine.py — المحرك الرئيسي الكامل المدمج (النسخة النهائية)
يشمل:
  - الساعات الكوكبية الكاملة
  - ضغط الأعداد small_abjad
  - توصيات المعادن
  - بروتوكولات السيادة (السواقط، الأوراد، الخواتم)
  - الدالة الرئيسية process_void المدمجة
  - دوال الرصد المتقدم (حساب الأبراج)
⚠️ لا تُعدَّل الخوارزميات دون مرجع من المخطوطة.
"""

from datetime import datetime as dt, timedelta
from typing import Dict, Optional, Tuple

# ── استيرادات البيانات الموسعة ──
from shams_data_extended import (
    ASMA_AL_HUSNA_EXTENDED, SERVANTS_EXTENDED,
    GEOMANCY_AUSPICIOUS, GEOMANCY_INAUSPICIOUS,
    FALLEN_LETTERS, DAILY_WIRDS, PROPHETIC_SEALS, TWISTED_TALISMANS,
    METAL_ADVICE, small_abjad, get_metal_advice,
)
from geomancy_engine import process_signals, analyze_chart, get_recommendation
from zairja_engine   import ask as zairja_ask, approximate_ascendant
from talisman_engine import get_talisman_from_recommendation, get_context_images

# ── Skyfield (اختياري) ──
try:
    from skyfield import api as _skyfield_api
    _SKYFIELD = True
except ImportError:
    _SKYFIELD = False

# ============================================================================
# 0. الساعات الكوكبية
# ============================================================================
PLANET_ORDER = ['saturn','jupiter','mars','sun','venus','mercury','moon']
PLANET_NAMES_AR = {
    'sun':'الشمس','moon':'القمر','mars':'المريخ','mercury':'عطارد',
    'jupiter':'المشتري','venus':'الزهرة','saturn':'زحل',
}
DAY_PLANET_INDEX = {
    0: PLANET_ORDER.index('saturn'),   # السبت
    1: PLANET_ORDER.index('sun'),      # الأحد
    2: PLANET_ORDER.index('moon'),     # الاثنين
    3: PLANET_ORDER.index('mars'),     # الثلاثاء
    4: PLANET_ORDER.index('mercury'),  # الأربعاء
    5: PLANET_ORDER.index('jupiter'),  # الخميس
    6: PLANET_ORDER.index('venus'),    # الجمعة
}
FORBIDDEN_HOURS = {
    0: {5, 7}, 1: {2, 4, 7, 12}, 2: set(),
    3: {2, 5, 10}, 4: {2, 7, 9}, 5: {12}, 6: {3},
}

def _get_user_weekday(d: dt) -> int:
    return (d.weekday() + 2) % 7

def _get_sunrise_sunset(d: dt, lat: float = 30.0444, lon: float = 31.2357) -> Tuple[dt, dt]:
    # نضمن naive datetime دائماً لتجنب خطأ المقارنة
    d_naive = d.replace(tzinfo=None) if d.tzinfo else d
    if _SKYFIELD:
        try:
            from skyfield import almanac as _alm
            ts  = _skyfield_api.load.timescale()
            eph = _skyfield_api.load('de421.bsp')
            obs = _skyfield_api.wgs84.latlon(lat, lon)
            t0  = ts.utc(d_naive.year, d_naive.month, d_naive.day, 0, 0, 0)
            t1  = ts.utc(d_naive.year, d_naive.month, d_naive.day, 23, 59, 59)
            f   = _alm.sunrise_sunset(eph, obs)
            times, events = _alm.find_discrete(t0, t1, f)
            sunrise = sunset = None
            for t, e in zip(times, events):
                utc_d = t.utc_datetime().replace(tzinfo=None)
                if e == 1 and sunrise is None: sunrise = utc_d
                if e == 0 and sunset  is None: sunset  = utc_d
            if sunrise and sunset:
                return sunrise, sunset
        except Exception:
            pass
    return (d_naive.replace(hour=6,  minute=0, second=0, microsecond=0),
            d_naive.replace(hour=18, minute=0, second=0, microsecond=0))

def get_planetary_hour_info(
    now: dt,
    lat: float = 30.0444,
    lon: float = 31.2357,
) -> dict:
    # نضمن naive datetime لتجنب خطأ المقارنة مع sunrise/sunset
    now = now.replace(tzinfo=None) if now.tzinfo else now
    sunrise, sunset = _get_sunrise_sunset(now, lat, lon)
    if now < sunrise:
        day_part = 'night'
        yest = now - timedelta(days=1)
        _, prev_sunset = _get_sunrise_sunset(yest, lat, lon)
        start, end = prev_sunset, sunrise
    elif sunrise <= now < sunset:
        day_part = 'day'
        start, end = sunrise, sunset
    else:
        day_part = 'night'
        start = sunset
        tmrw  = now + timedelta(days=1)
        next_sunrise, _ = _get_sunrise_sunset(tmrw, lat, lon)
        end = next_sunrise
    period  = max(1, (end - start).total_seconds())
    hourlen = period / 12.0
    elapsed = max(0, (now - start).total_seconds())
    hour_n  = min(12, int(elapsed // hourlen) + 1)
    weekday = _get_user_weekday(now)
    pindex  = (DAY_PLANET_INDEX[weekday] + hour_n - 1) % 7
    pkey    = PLANET_ORDER[pindex]
    return {
        'hour_number':        hour_n,
        'planet_name':        PLANET_NAMES_AR[pkey],
        'planet_key':         pkey,
        'is_forbidden':       hour_n in FORBIDDEN_HOURS.get(weekday, set()),
        'day_part':           day_part,
        'hour_length_seconds':hourlen,
        'sunrise':            str(sunrise),
        'sunset':             str(sunset),
        'weekday':            weekday,
    }

def get_precise_planetary_time() -> dict:
    now = dt.now()
    peak_minutes = [15, 33, 45, 55]
    is_peak = now.minute in peak_minutes
    return {
        'current_minute': now.minute,
        'is_peak_minute': is_peak,
        'timing_advice':  "الوقت في ذروته الفلكية — تنفيذ الآن!" if is_peak else "وقت اعتيادي، يمكن التنفيذ.",
    }

# ============================================================================
# 1. بروتوكولات السيادة
# ============================================================================
def apply_system_overrides(weekday: int, intent: str) -> dict:
    overrides = {}
    fallen = FALLEN_LETTERS.get(weekday, {})
    if fallen:
        overrides['shadow_override'] = {
            'letter':      fallen['letter'],
            'action':      fallen['action'],
            'instruction': f"استخدم حرف '{fallen['letter']}' لـ {fallen['action']} في حالة وجود عوائق.",
        }
    wird_data = DAILY_WIRDS.get(weekday, {})
    if wird_data:
        overrides['carrier_wave'] = {
            'wird':        wird_data['wird'],
            'tahateel':    wird_data['tahateel'],
            'instruction': f"اقرأ الورد ({wird_data['wird']}) مع الطهطيل ({wird_data['tahateel']}) لتفعيل الطلسم.",
        }
    if intent and any(w in intent for w in ['حماية','رصد','خفاء','سر','إخفاء']):
        overrides['hardcode_seal'] = {
            **TWISTED_TALISMANS['hakim_knot'],
            'image_url': '/static/images/talisman/hakim_knot_0.png',
        }
    else:
        imgs = [f'/static/images/{p}' for p in PROPHETIC_SEALS['solomon_seal']['images']]
        overrides['hardcode_seal'] = {
            **PROPHETIC_SEALS['solomon_seal'],
            'images_urls': imgs,
        }
    return overrides

# ============================================================================
# 2. دوال مساعدة
# ============================================================================
def _calc_abjad(text: str) -> int:
    from data import ABJAD_VALUES
    return sum(ABJAD_VALUES.get(c, 0) for c in text)

def _merge_asma(asma_name: str) -> dict:
    try:
        from data import ASMA_AL_HUSNA
        base = dict(ASMA_AL_HUSNA.get(asma_name, {}))
    except Exception:
        base = {}
    ext    = dict(ASMA_AL_HUSNA_EXTENDED.get(asma_name, {}))
    merged = {**ext, **base}
    merged['name'] = asma_name
    return merged

# ============================================================================
# 3. الدالة الرئيسية process_void
# ============================================================================
def process_void(signals: Dict, user_input: str = "") -> Dict:
    from datetime import timezone as _tz
    now = dt.now(_tz.utc).replace(tzinfo=None)  # naive UTC
    hour_info = get_planetary_hour_info(now)
    timing    = get_precise_planetary_time()
    geo_result = process_signals(signals)
    analysis   = geo_result['analysis']
    rec        = geo_result['recommendation']
    zairja_answer = None
    if user_input.strip():
        asc = approximate_ascendant(
            signals.get('hour',   now.hour),
            signals.get('minute', now.minute),
        )
        zairja_answer = zairja_ask(user_input, asc)
    asma_name = rec.get('asma', 'الفتاح')
    asma_data = _merge_asma(asma_name)
    total_raw        = asma_data.get('abjad', 0)
    if total_raw == 0:
        total_raw    = int(signals.get('char_count', 14) * 10)
    total_compressed = small_abjad(total_raw)
    wafq_type = rec.get('wafq', 'المثلث')
    if '4x4' in str(wafq_type) or 'المربع' in str(wafq_type):
        wafq_type = 'المربع'
    elif '5x5' in str(wafq_type) or 'المخمس' in str(wafq_type):
        wafq_type = 'المخمس'
    elif '6x6' in str(wafq_type) or 'المسدس' in str(wafq_type):
        wafq_type = 'المسدس'
    else:
        wafq_type = 'المثلث'
    is_empty_center  = rec.get('gate', 0) in [6, 8, 12, 13]
    center_value     = small_abjad(asma_data.get('abjad', total_raw) % 9 or 9)
    planet_name = hour_info.get('planet_name', 'الشمس')
    metal_info  = get_metal_advice(planet_name)
    metal_text  = f"المعدن المناسب: {metal_info['metal']} — {metal_info['description']}"
    rec.update({
        'wafq_type':         wafq_type,
        'total_value':       total_compressed,
        'is_empty_center':   is_empty_center,
        'center_value':      center_value,
        'angels':            ['جبرائيل', 'ميكائيل', 'إسرافيل', 'عزرائيل'],
        'planet':            asma_data.get('planet', planet_name),
        'hour_info':         hour_info,
        'is_forbidden_hour': hour_info['is_forbidden'],
        'metal_info':        metal_info,
    })
    talisman_url = get_talisman_from_recommendation({**rec, 'asma': asma_name})
    sura_wafq = None
    if user_input.strip():
        try:
            from data import get_sura_wafq_by_intent
            sura_wafq = get_sura_wafq_by_intent(user_input)
        except Exception:
            pass
    try:
        from data import estimate_lunar_day, get_solar_mansion, LUNAR_MANSIONS
        lunar_day     = estimate_lunar_day(now)
        solar_mansion = get_solar_mansion(now)
        lunar_mansion = LUNAR_MANSIONS.get(solar_mansion.get('number', 1), {})
    except Exception:
        lunar_day, solar_mansion, lunar_mansion = 1, {}, {}
    weekday          = now.weekday()
    system_overrides = apply_system_overrides(weekday, user_input)
    warnings = []
    if hour_info['is_forbidden']:
        warnings.append(f"⚠️ الساعة {hour_info['hour_number']} مذمومة في هذا اليوم. الأفضل تأجيل العمل أو استخدام باب التحصين (4 أو 9).")
    if is_empty_center:
        warnings.append("⚡ باب ظلماني — يُستخدم وفق خالي الوسط. تأكد من الطهارة الكاملة.")
    extra_images = get_context_images('mizan' if wafq_type in ['المربع','المخمس'] else 'cinematic', 2)
    return {
        'geomancy':          geo_result,
        'recommendation':    {**rec, 'asma_full': asma_data},
        'zairja_answer':     zairja_answer,
        'talisman_url':      talisman_url,
        'extra_images':      extra_images,
        'asma_data':         asma_data,
        'sura_wafq':         sura_wafq,
        'lunar_day':         lunar_day,
        'lunar_mansion':     lunar_mansion,
        'solar_mansion':     solar_mansion,
        'hidden_intent':     analysis.get('hidden_intent', ''),
        'time_data':         analysis.get('time_data', {}),
        'summary':           analysis.get('summary', {}),
        'shadow_protocol':   system_overrides.get('shadow_override', {}),
        'execution_mantra':  system_overrides.get('carrier_wave', {}),
        'root_privilege':    system_overrides.get('hardcode_seal', {}),
        'precise_timing':    timing,
        'wafq_type':         wafq_type,
        'total_value':       total_compressed,
        'is_empty_center':   is_empty_center,
        'center_value':      center_value,
        'hour_info':         hour_info,
        'metal_recommendation': metal_text,
        'metal_info':        metal_info,
        'warnings':          warnings,
    }

# ============================================================================
# 4. enrich_recommendation — إثراء التوصية النهائية
# ============================================================================
def enrich_recommendation(result: dict) -> str:
    lines = []
    hour  = result.get('hour_info', {})
    rec   = result.get('recommendation', {})
    if hour.get('is_forbidden'):
        lines.append(f"⚠️ الساعة {hour.get('hour_number')} مذمومة — استخدم باب التحصين.")
    else:
        lines.append(f"✅ الساعة {hour.get('hour_number')} مناسبة — كوكب {hour.get('planet_name')}.")
    metal = result.get('metal_recommendation', '')
    if metal:
        lines.append(f"🔩 {metal}")
    mansion = result.get('lunar_mansion', {})
    if mansion.get('name'):
        lines.append(f"🌙 منزلة {mansion['name']} ({mansion.get('ruling','')}) — {mansion.get('usage','')[:60]}")
    asma = rec.get('asma', '')
    if asma:
        lines.append(f"📿 الاسم الحسنى: {asma} — {rec.get('advice','')}")
    lines.append(f"🔢 نوع الوفق: {result.get('wafq_type','')} | المجموع المضغوط: {result.get('total_value','')}")
    for w in result.get('warnings', []):
        lines.append(w)
    return "\n".join(lines)

def get_metal_recommendation(planet_name: str) -> str:
    adv = get_metal_advice(planet_name)
    return f"المعدن المناسب: {adv['metal']} — {adv['description']}"

# ============================================================================
# 5. نظام الرصد المتقدم – حساب الأبراج (الفصل الرابع)
# ============================================================================
def calculate_sun_zodiac(day: int, month: int) -> dict:
    zodiac_ranges = {
        "الحمل": {"start": (3, 21), "end": (4, 19), "planet": "المريخ", "element": "ناري"},
        "الثور": {"start": (4, 20), "end": (5, 20), "planet": "الزهرة", "element": "ترابي"},
        "الجوزاء": {"start": (5, 21), "end": (6, 20), "planet": "عطارد", "element": "هوائي"},
        "السرطان": {"start": (6, 21), "end": (7, 22), "planet": "القمر", "element": "مائي"},
        "الأسد": {"start": (7, 23), "end": (8, 22), "planet": "الشمس", "element": "ناري"},
        "السنبلة": {"start": (8, 23), "end": (9, 22), "planet": "عطارد", "element": "ترابي"},
        "الميزان": {"start": (9, 23), "end": (10, 22), "planet": "الزهرة", "element": "هوائي"},
        "العقرب": {"start": (10, 23), "end": (11, 21), "planet": "المريخ", "element": "مائي"},
        "القوس": {"start": (11, 22), "end": (12, 21), "planet": "المشتري", "element": "ناري"},
        "الجدي": {"start": (12, 22), "end": (1, 19), "planet": "زحل", "element": "ترابي"},
        "الدلو": {"start": (1, 20), "end": (2, 18), "planet": "زحل", "element": "هوائي"},
        "الحوت": {"start": (2, 19), "end": (3, 20), "planet": "المشتري", "element": "مائي"},
    }
    for name, data in zodiac_ranges.items():
        start_month, start_day = data["start"]
        end_month, end_day = data["end"]
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return {"name": name, "planet": data["planet"], "element": data["element"], "type": "شمسي"}
    return {"name": "غير معروف", "planet": "غير معروف", "element": "غير معروف", "type": "شمسي"}

def calculate_moon_zodiac(day: int, month: int, year: int) -> dict:
    month_numbers = {1:0, 2:4, 3:4, 4:8, 5:11, 6:14, 7:17, 8:21, 9:24, 10:27, 11:3, 12:6}
    year_numbers = {2000:2, 2020:5, 2021:16, 2022:27, 2023:9, 2024:20, 2025:1, 2026:12}
    month_num = month_numbers.get(month, 0)
    year_num = year_numbers.get(year, 0)
    total = day + month_num + year_num
    if total > 28:
        total = total % 28
    moon_map = {0:"الحمل",1:"الثور",2:"الجوزاء",3:"السرطان",4:"الأسد",5:"السنبلة",6:"الميزان",7:"العقرب",8:"القوس",9:"الجدي",10:"الدلو",11:"الحوت"}
    zodiac_name = moon_map.get(total % 12, "الحمل")
    zodiac_info = {"الحمل":{"planet":"المريخ","element":"ناري"}, "الثور":{"planet":"الزهرة","element":"ترابي"}, "الجوزاء":{"planet":"عطارد","element":"هوائي"}, "السرطان":{"planet":"القمر","element":"مائي"}, "الأسد":{"planet":"الشمس","element":"ناري"}, "السنبلة":{"planet":"عطارد","element":"ترابي"}, "الميزان":{"planet":"الزهرة","element":"هوائي"}, "العقرب":{"planet":"المريخ","element":"مائي"}, "القوس":{"planet":"المشتري","element":"ناري"}, "الجدي":{"planet":"زحل","element":"ترابي"}, "الدلو":{"planet":"زحل","element":"هوائي"}, "الحوت":{"planet":"المشتري","element":"مائي"}}
    info = zodiac_info.get(zodiac_name, {"planet":"غير معروف","element":"غير معروف"})
    return {"name": zodiac_name, "planet": info["planet"], "element": info["element"], "type": "قمري", "calculation_value": total}

def calculate_spiritual_zodiac(name: str, mother_name: str) -> dict:
    from data import ABJAD_VALUES
    def calc(s): return sum(ABJAD_VALUES.get(c,0) for c in s)
    total = calc(name) + calc(mother_name)
    remainder = total % 12
    spiritual_map = {1:"الحمل",2:"الثور",3:"الجوزاء",4:"السرطان",5:"الأسد",6:"السنبلة",7:"الميزان",8:"العقرب",9:"القوس",10:"الجدي",11:"الدلو",0:"الحوت"}
    zodiac_name = spiritual_map.get(remainder, "الحوت")
    zodiac_info = {"الحمل":{"planet":"المريخ","element":"ناري"}, "الثور":{"planet":"الزهرة","element":"ترابي"}, "الجوزاء":{"planet":"عطارد","element":"هوائي"}, "السرطان":{"planet":"القمر","element":"مائي"}, "الأسد":{"planet":"الشمس","element":"ناري"}, "السنبلة":{"planet":"عطارد","element":"ترابي"}, "الميزان":{"planet":"الزهرة","element":"هوائي"}, "العقرب":{"planet":"المريخ","element":"مائي"}, "القوس":{"planet":"المشتري","element":"ناري"}, "الجدي":{"planet":"زحل","element":"ترابي"}, "الدلو":{"planet":"زحل","element":"هوائي"}, "الحوت":{"planet":"المشتري","element":"مائي"}}
    info = zodiac_info.get(zodiac_name, {"planet":"غير معروف","element":"غير معروف"})
    return {"name": zodiac_name, "planet": info["planet"], "element": info["element"], "type": "روحاني", "calculation_value": total, "remainder": remainder}

# ============================================================================
# ✦ v11.0 — نظام التوافق والتنافر العنصري + حرف الميزان
# المصدر: الفصل الثاني من شمس المعارف (الطبائع والتراكيب)
# ⚠️ لا تُعدَّل دون مرجع من المخطوطة
# ============================================================================

from shams_data_extended import (
    ELEMENTAL_FRIENDS, ELEMENTAL_ENEMIES, MEDIATOR_LETTERS
)

# عربي → إنجليزي للطبائع
_ELEM_AR_TO_EN = {
    'ناري': 'fire', 'نارى': 'fire',
    'هوائي': 'air', 'هوائى': 'air',
    'مائي': 'water', 'مائى': 'water',
    'ترابي': 'earth', 'ترابى': 'earth',
}
_ELEM_EN_TO_AR = {
    'fire': 'ناري', 'air': 'هوائي',
    'water': 'مائي', 'earth': 'ترابي',
}


def check_elemental_compatibility(el1_ar: str, el2_ar: str) -> dict:
    """
    ✦ فحص التوافق والتنافر العنصري — v11.0
    ═══════════════════════════════════════
    الطبائع الصديقة:  النار ↔ الهواء  |  الماء ↔ التراب
    الطبائع المتعادية: النار ↔ الماء   |  التراب ↔ الهواء

    المدخل: طبعان بالعربي (مثل 'ناري', 'مائي')
    المخرج: {status, mediator, message, recommendation}

    المصدر: شمس المعارف الكبرى — الفصل الثاني، باب الطبائع الأربعة.
    """
    el1 = _ELEM_AR_TO_EN.get(el1_ar, el1_ar)
    el2 = _ELEM_AR_TO_EN.get(el2_ar, el2_ar)

    if el1 == el2:
        return {
            'status': 'identical',
            'status_ar': 'تطابق',
            'message': f'كلا الطبعين {el1_ar} — تطابق تام في الطبيعة.',
            'score_modifier': +20,
            'mediator': None,
            'recommendation': 'لا حاجة لحرف وسيط — الطبعان متطابقان.',
        }

    if ELEMENTAL_FRIENDS.get(el1) == el2:
        return {
            'status': 'friend',
            'status_ar': 'صديق',
            'message': f'{el1_ar} و{el2_ar} طبعان صديقان — {el1_ar} يزيد {el2_ar}.',
            'score_modifier': +15,
            'mediator': None,
            'recommendation': 'العمل مناسب — الطبعان يتعاونان ولا يتعارضان.',
        }

    if ELEMENTAL_ENEMIES.get(el1) == el2:
        mediator_key = (el1, el2)
        med = MEDIATOR_LETTERS.get(mediator_key, {})
        med_letter = med.get('letter', 'س')
        med_reason = med.get('reason', 'يكسر التضاد بين الطبعين')
        med_el_ar  = _ELEM_EN_TO_AR.get(med.get('element', 'water'), 'مائي')

        return {
            'status': 'enemy',
            'status_ar': 'تضاد',
            'message': (
                f'⚡ تضاد عنصري ({el1_ar}/{el2_ar}) — '
                f'هذان الطبعان متعاديان ويتنافران.'
            ),
            'score_modifier': -25,
            'mediator': {
                'letter':  med_letter,
                'element': med_el_ar,
                'reason':  med_reason,
            },
            'recommendation': (
                f'يُنصح بإضافة حرف الميزان "{med_letter}" ({med_el_ar}) '
                f'لضبط الوفق وكسر التضاد. {med_reason}.'
            ),
        }

    # محايد (لا صداقة ولا عداوة)
    return {
        'status': 'neutral',
        'status_ar': 'محايد',
        'message': f'{el1_ar} و{el2_ar} طبعان محايدان — لا تعاون ولا تعارض.',
        'score_modifier': 0,
        'mediator': None,
        'recommendation': 'الطبعان محايدان — العمل يُنفَّذ لكن بلا دفعة إضافية.',
    }


def calculate_affinity_v11(d1: dict, d2: dict) -> dict:
    """
    ✦ حساب التوافق المحسّن — v11.0
    يدمج النتيجة القديمة مع فحص التوافق العنصري الجديد.
    """
    # النتيجة الأساسية (v10 — محفوظة)
    score = 0
    if d1.get('dominant') == d2.get('dominant'):
        score += 40
    score += max(0, 28 - abs(d1.get('spirit', 14) - d2.get('spirit', 14)))
    score += max(0, 12 - abs(d1.get('station', 6) - d2.get('station', 6)))
    if d1.get('planet') == d2.get('planet'):
        score += 10

    # التوافق العنصري (v11 — جديد)
    el_compat = check_elemental_compatibility(
        d1.get('dominant', 'ناري'),
        d2.get('dominant', 'ناري'),
    )
    score += el_compat['score_modifier']
    score = max(0, min(100, score))

    if score >= 80:
        label = 'توافق ممتاز — تناغم نادر'
    elif score >= 60:
        label = 'توافق جيد — انسجام واضح'
    elif score >= 40:
        label = 'توافق متوسط — تباين منتج'
    else:
        label = 'توافق محدود — تضاد في الطبائع'

    return {
        'score':              score,
        'label':              label,
        'elemental_compat':   el_compat,
        'has_conflict':       el_compat['status'] == 'enemy',
        'mediator_letter':    el_compat.get('mediator'),
        'recommendation':     el_compat['recommendation'],
    }
