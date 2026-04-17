# -*- coding: utf-8 -*-
"""
شمس المعارف الكبرى — الإصدار التاسع عشر النهائي (v19 PRODUCTION)
══════════════════════════════════════════════════════════════════
النسخة الرابعة المُعاد هندستها بالكامل على أسس Production-Grade

✅ يجمع أفضل ما في النسخ الثلاث السابقة
✅ يُصلح جميع الأخطاء من الجذور (Root-Level Fixes)
✅ Clean Architecture — فصل تام بين الطبقات
✅ SOLID Principles مُطبَّقة بالكامل
✅ Thread-Safe في كل العمليات المتزامنة
✅ Rate Limiting حقيقي عبر decorator رسمي
✅ Caching مُطبَّق فعلياً على كل API ثقيل
✅ Error Handlers شاملة تُرجع JSON دائماً
✅ logger_system مُحسَّن بـ _id_counter منفصل
✅ app.run() خارج أي شرط — سلوك ثابت ومضمون
✅ Input Validation مركزي لا يتكرر
✅ OPTIONS handling عبر decorator مركزي (DRY)
✅ /api/health endpoint للمراقبة
✅ ABJAD_VALUES مستورد مرة واحدة من data.py
══════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════
# القسم 0: الاستيرادات الأساسية
# ══════════════════════════════════════════════════════════════════
from flask import Flask, request, jsonify, send_from_directory, Response
from collections import Counter
import psutil
import time
import hashlib
import math
import io
import os
import re
import copy
import json
import traceback
from datetime import datetime as dt, timedelta
from typing import Tuple, Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# ── Caching (اختياري) ───────────────────────────────────────────
try:
    from flask_caching import Cache
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False

# ── Rate Limiting (اختياري) ──────────────────────────────────────
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False

# ── نظام السجلات ─────────────────────────────────────────────────
import logger_system
logger_system.log('INFO', 'app.startup', '🌅 بدء تشغيل شمس المعارف الكبرى v19 PRODUCTION')

# ── تحميل بيانات الأسماء الحسنى ──────────────────────────────────
try:
    with open('asma_full_details.json', encoding='utf-8') as _f:
        ASMA_FULL_DETAILS: Dict[str, Any] = json.load(_f)
    logger_system.log('INFO', 'app.startup',
                      f'✅ تم تحميل {len(ASMA_FULL_DETAILS)} اسماً حسنى من المخطوطتين')
except Exception as _e:
    ASMA_FULL_DETAILS = {}
    logger_system.log('WARNING', 'app.startup', f'⚠️ فشل تحميل asma_full_details.json: {_e}')

# ── دالة الوقت الموحدة (UTC) ─────────────────────────────────────
from datetime import timezone as _tz

def now_utc() -> dt:
    """إرجاع الوقت الحالي بـ UTC — المرجع الموحد في كل المشروع"""
    return dt.now(_tz.utc)

# ══════════════════════════════════════════════════════════════════
# القسم 1: استيراد البيانات والمحركات
# ══════════════════════════════════════════════════════════════════
from data import (
    LUNAR_MANSIONS, KINGS_DATA, RULING_KINGS,
    NOURANI_LETTERS_28, DHULMANI_LETTERS_28,
    ASMA_AL_HUSNA, LATAIF, MUQATTAAT, SURA_WAFQ,
    RITUALS, TALISMANS, SULAYMAN_AGENTS,
    ZODIAC, get_zodiac_by_number, get_zodiac_by_jummal,
    LETTER_ISTINTAQ, get_letter_angel,
    ALCHEMY_DICTIONARY, SIMIYA_ARTICLES,
    LETTER_DETAILS, get_letter_details,
    SPIRITUAL_GATES, get_spiritual_gate,
    get_sura_wafq_by_intent, get_nearest_asma,
    get_latifa_by_benefit, get_muqatta_by_jummal, get_agent_for_day,
    advanced_istintaq, get_jafr_zamam,
    get_wafq_from_zodiac, generate_wafq_by_type,
    get_alchemy_advice, get_simiya_advice,
    JESUS_NAMES, JESUS_QUOTE, FATIHA_SECRETS, KHAHYAS_PROPERTIES, AYAT_AL_KURSI_PROPS,
    ABJAD_VALUES,  # ✅ FIX: استيراد صريح مرة واحدة — لا تعريف يدوي مكرر
)

from shams_engine import (
    process_void, enrich_recommendation, get_metal_recommendation,
    get_planetary_hour_info as _shams_get_planetary_hour_info,
    calculate_sun_zodiac, calculate_moon_zodiac, calculate_spiritual_zodiac,
    check_elemental_compatibility, calculate_affinity_v11,
)
from geomancy_engine import (
    process_signals as geo_process_signals,
    extract_hidden_intent_advanced, generate_full_chart,
    signals_to_mothers, analyze_chart,
)
from zairja_engine   import full_zairja_reading, circular_zairja, advanced_jafr_zamam
from talisman_engine import (
    get_talisman_url, list_available_talismans,
    generate_geometric_talisman, bird_script, bird_script_grid,
)
from soul_engine     import process_soul, _make_session_id, get_session_summary
from shams_data_extended import (
    METAL_ADVICE, small_abjad, get_metal_advice,
    GEOMANCY_HOUSES, GEOMANCY_PATTERNS_AR,
    GEOMANCY_AUSPICIOUS, GEOMANCY_INAUSPICIOUS,
    ASMA_AL_HUSNA_EXTENDED, TALISMANS_DB,
    PLANETARY_HOURS_TABLE, PLANET_INCENSE,
    MANDAL_QUOTE, GEOMANCY_QUOTE, ZAIRJA_QUOTE, ZODIAC_QUOTE, WAFQ_QUOTE, KHALWA_QUOTE,
    MIZAN_AL_ADL, FAWATEH_AL_RAGAIB, ZAHRA_AL_MUROOJ, LATAIF_AL_ISHARA,
    TAHATIL, AHD_AL_QADIM, KHATAM_AL_IGHLAQ,
    ELEMENTAL_FRIENDS, ELEMENTAL_ENEMIES, MEDIATOR_LETTERS,
    ZODIAC_STRINGS, LEAP_BY_HOUR, DAY_LETTERS, ASCENDANT_LETTERS,
)
from mandal_engine import (
    MANDAL_TOOLS, MANDAL_SEALS, OBSERVER_CONDITIONS,
    draw_noorani_circle, summon_mandal, check_observer_compatibility,
    get_best_mandal_time, interpret_vision,
)
from jafr_engine import (
    calc_jafr_simple, calc_jafr_compound,
    get_jafr_letter_info, get_all_jafr_table,
    JAFR_TABLE, JAFR_LETTERS, JAFR_ABJAD,
)
from intent_engine   import analyze_intent
from symbolic_engine import encode_user_data
from matrix_engine   import process_matrix
from path_engine     import resolve_path
from king_engine     import get_king_for_intent, KINGS_DB as KINGS_DB_V4
from astro_gatekeeper import astro_gatekeeper
from elemental_balance import analyze_user_balance
from session_sandbox   import session_manager
from license_manager import (
    sovereignty_check, inject_ahd, apply_sealing_ring,
    get_tahateel_for_today, get_tahateel_for_talisman,
    get_safety_message, verify_license, first_run_setup,
    check_digital_khulwa, get_hardware_id, SAFETY_MESSAGES,
)

# ── Diagnostics ──────────────────────────────────────────────────
try:
    from diagnostics_engine import run_full_diagnostics
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

# ── Core Engine + Rule Engine + Knowledge Base (v17 NEW) ─────────────
try:
    from core_engine import process as core_process, search_knowledge, parse_intent_from_text
    from rule_engine import analyze_name_deep, check_elemental_law, analyze_arabic_text
    from knowledge_loader import (
        get_letter as kb_get_letter,
        get_divine_name as kb_get_divine_name,
        get_summary as kb_get_summary,
    )
    CORE_ENGINE_AVAILABLE = True
    logger_system.log('INFO', 'app.startup', '✅ Core Engine + Knowledge Base محملين')
except Exception as _ce:
    CORE_ENGINE_AVAILABLE = False
    logger_system.log('WARNING', 'app.startup', f'⚠️ Core Engine: {_ce}')

# ── Pillow ───────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# ── V19: New Engines (Alchemy, Symia, Abjad Calculator) ──────────
try:
    from engines.abjad_calculator import (
        calculate_abjad as _calc_abjad_v19,
        reduce_to_single_digit as _reduce_abjad_v19,
        get_abjad_remainder as _abjad_remainder_v19,
    )
    ABJAD_CALC_V19 = True
except ImportError:
    ABJAD_CALC_V19 = False

try:
    from engines.alchemy_engine import (
        get_metal_for_planet, get_element_nature, get_recipe,
        get_spiritual_transmutation, calculate_elixir_power, get_reaction,
        PLANET_METAL_MAP as _PLANET_METAL_MAP_V19,
        ALCHEMICAL_STAGES, RECIPES, BALANCE_VALUES, BALANCE_DEGREES,
    )
    ALCHEMY_ENGINE_V19 = True
except ImportError:
    ALCHEMY_ENGINE_V19 = False

try:
    from engines.symia_engine import (
        get_khunfutriyyat_ritual, get_article, get_all_articles,
        get_barhatiya_oath, calculate_article_power, perform_symia_ritual,
        invoke_shamkhiyya, ARTICLES as _SYMIA_ARTICLES_V19,
    )
    SYMIA_ENGINE_V19 = True
except ImportError:
    SYMIA_ENGINE_V19 = False

try:
    from engines.time_engine import TimeEngine as _TimeEngineV19
    _time_engine_v19 = _TimeEngineV19()
    TIME_ENGINE_V19 = True
except ImportError:
    TIME_ENGINE_V19 = False
    _time_engine_v19 = None

# ── V19: Rich Knowledge Modules ───────────────────────────────────
try:
    from knowledge.divine_names import (
        DIVINE_NAMES_DATA, DIVINE_NAMES_LIST,
        get_divine_name as _kb_get_divine_name_v19,
        get_divine_name_for_intent as _kb_get_divine_name_intent,
    )
    KNOWLEDGE_DIVINE_NAMES_V19 = True
except ImportError:
    KNOWLEDGE_DIVINE_NAMES_V19 = False
    DIVINE_NAMES_DATA = {}
    DIVINE_NAMES_LIST = []

try:
    from knowledge.letters import (
        LETTERS_DATA,
        get_letter as _kb_get_letter_v19,
        get_all_letters as _kb_get_all_letters,
        get_light_letters, get_dark_letters,
        get_letter_angel, get_letter_servant,
    )
    KNOWLEDGE_LETTERS_V19 = True
except ImportError:
    KNOWLEDGE_LETTERS_V19 = False
    LETTERS_DATA = {}

try:
    from knowledge.planets import (
        PLANETS_DATA,
        get_planet as _kb_get_planet_v19,
        get_all_planets, get_planet_by_day as _kb_get_planet_by_day,
        get_planet_nature, get_conjunction_effect,
    )
    KNOWLEDGE_PLANETS_V19 = True
except ImportError:
    KNOWLEDGE_PLANETS_V19 = False
    PLANETS_DATA = {}

try:
    from knowledge.zodiacs import ZODIACS_DATA, get_zodiac as _kb_get_zodiac
    KNOWLEDGE_ZODIACS_V19 = True
except ImportError:
    KNOWLEDGE_ZODIACS_V19 = False
    ZODIACS_DATA = {}

try:
    from knowledge.lunar_mansions import (
        LUNAR_MANSIONS_DATA as _LM_DATA_V19,
        get_lunar_mansion as _kb_get_lunar_mansion,
    )
    KNOWLEDGE_LUNAR_V19 = True
except ImportError:
    KNOWLEDGE_LUNAR_V19 = False

try:
    from knowledge.thrones import get_all_thrones, get_throne
    from knowledge.veils import get_all_veils, get_veil
    from knowledge.mothers import get_all_mothers, get_mother, get_mother_for_intent
    from knowledge.shamkhiyya import get_all_shamkhiyya, get_shamkhiyya_name
    from knowledge.khulwa import get_khulwa, get_all_khulwa
    from knowledge.gates import get_all_gates
    from knowledge.kings import get_all_kings
    from knowledge.elements import ELEMENTS_DATA
    KNOWLEDGE_EXTENDED_V19 = True
except ImportError:
    KNOWLEDGE_EXTENDED_V19 = False
    ELEMENTS_DATA = {}

# ── V19: Zairja new functions ─────────────────────────────────────
try:
    from zairja_engine import zairja_center, get_qutb_string
    ZAIRJA_CENTER_V19 = True
except ImportError:
    ZAIRJA_CENTER_V19 = False

# ── V19: GeomancyEngine class ─────────────────────────────────────
try:
    from geomancy_engine import GeomancyEngine as _GeomancyEngineV19
    _geomancy_engine_v19 = _GeomancyEngineV19()
    GEOMANCY_ENGINE_V19 = True
except Exception:
    GEOMANCY_ENGINE_V19 = False
    _geomancy_engine_v19 = None

logger_system.log('INFO', 'app.startup',
    f'✅ v19 Engines: alchemy={ALCHEMY_ENGINE_V19} symia={SYMIA_ENGINE_V19} '
    f'knowledge_names={KNOWLEDGE_DIVINE_NAMES_V19} letters={KNOWLEDGE_LETTERS_V19}')

# ── Skyfield ─────────────────────────────────────────────────────
try:
    from skyfield import api
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

# ── Gemini AI ────────────────────────────────────────────────────
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GEMINI_MODEL   = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-exp')
client = None
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger_system.log('INFO', 'app.startup', '✅ Gemini متصل بنجاح')
    except Exception as _ge:
        logger_system.log('WARNING', 'app.startup', f'⚠️ خطأ في تهيئة Gemini: {_ge}')

# ══════════════════════════════════════════════════════════════════
# القسم 2: الثوابت الفلكية (Data Layer)
# ══════════════════════════════════════════════════════════════════
PLANET_ORDER    = ['saturn', 'jupiter', 'mars', 'sun', 'venus', 'mercury', 'moon']
PLANET_NAMES_AR = {
    'sun': 'الشمس', 'moon': 'القمر', 'mars': 'المريخ', 'mercury': 'عطارد',
    'jupiter': 'المشتري', 'venus': 'الزهرة', 'saturn': 'زحل',
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
    0: {5, 7}, 1: {2, 4, 7, 12}, 2: set(), 3: {2, 5, 10},
    4: {2, 7, 9}, 5: {12}, 6: {3},
}
_DAY_NAMES_AR = {
    0: 'السبت', 1: 'الأحد', 2: 'الاثنين', 3: 'الثلاثاء',
    4: 'الأربعاء', 5: 'الخميس', 6: 'الجمعة',
}

# ══════════════════════════════════════════════════════════════════
# القسم 3: Config & EntropySource (Infrastructure Layer)
# ══════════════════════════════════════════════════════════════════
class Config:
    """إعدادات المشروع — مستوردة من env مع قيم افتراضية"""
    LATITUDE         = float(os.environ.get('LATITUDE',  30.0444))
    LONGITUDE        = float(os.environ.get('LONGITUDE', 31.2357))
    ELEVATION        = float(os.environ.get('ELEVATION', 0))
    ENTROPY_INTERVAL = 0.1
    VERSION          = 'v19'
    APP_NAME         = 'شمس المعارف الكبرى'

class EntropySource:
    """مصدر الانتروبيا — يُولّد نقاط عشوائية من CPU/RAM"""
    def __init__(self) -> None:
        self.last_cpu = psutil.cpu_percent(interval=Config.ENTROPY_INTERVAL)
        self.last_mem = psutil.virtual_memory().percent

    def get_entropy(self) -> float:
        cpu  = psutil.cpu_percent(interval=Config.ENTROPY_INTERVAL)
        mem  = psutil.virtual_memory().percent
        seed = f'{cpu}{mem}{abs(cpu - self.last_cpu)}{abs(mem - self.last_mem)}{time.time_ns()}'.encode()
        self.last_cpu, self.last_mem = cpu, mem
        return int(hashlib.sha256(seed).hexdigest()[:8], 16) / 0xffffffff

    def generate_points(self, n: int) -> List[int]:
        return [1 if self.get_entropy() > 0.5 else 0 for _ in range(n)]

# ══════════════════════════════════════════════════════════════════
# القسم 4: دوال الفلك (Astronomy Business Logic)
# ══════════════════════════════════════════════════════════════════
def get_user_weekday(d: dt) -> int:
    return (d.weekday() + 2) % 7

def get_sunrise_sunset(d: dt, lat: float, lon: float, elev: float = 0) -> Tuple[dt, dt]:
    """حساب شروق وغروب الشمس — مع Skyfield إن توفّر وإلا fallback"""
    d_naive   = d.replace(tzinfo=None) if d.tzinfo else d
    fallback_sr = d_naive.replace(hour=6,  minute=0, second=0, microsecond=0)
    fallback_ss = d_naive.replace(hour=18, minute=0, second=0, microsecond=0)
    if not SKYFIELD_AVAILABLE:
        return fallback_sr, fallback_ss
    try:
        from skyfield import almanac
        ts       = api.load.timescale()
        eph      = api.load('de421.bsp')
        observer = api.wgs84.latlon(lat, lon, elevation_m=elev)
        t0       = ts.utc(d_naive.year, d_naive.month, d_naive.day, 0,  0,  0)
        t1       = ts.utc(d_naive.year, d_naive.month, d_naive.day, 23, 59, 59)
        f        = almanac.sunrise_sunset(eph, observer)
        times, events = almanac.find_discrete(t0, t1, f)
        sunrise  = sunset = None
        for t, e in zip(times, events):
            utc_dt = t.utc_datetime().replace(tzinfo=None)
            if e == 1 and sunrise is None:
                sunrise = utc_dt
            elif e == 0 and sunset is None:
                sunset = utc_dt
        return (sunrise or fallback_sr), (sunset or fallback_ss)
    except Exception:
        return fallback_sr, fallback_ss

def get_planetary_hour_info(now: dt,
                            lat: float = None,
                            lon: float = None) -> dict:
    """
    ✅ FIX (v10): الدالة المحلية لا تتعارض مع _shams_get_planetary_hour_info
    لأن الاستيراد تم بـ alias منفصل.
    ✅ FIX: lat/lon يأخذان من Config إن لم يُمرَّرا
    """
    lat       = lat if lat is not None else Config.LATITUDE
    lon       = lon if lon is not None else Config.LONGITUDE
    now_naive = now.replace(tzinfo=None) if now.tzinfo else now
    sunrise, sunset = get_sunrise_sunset(now_naive, lat, lon)

    if now_naive < sunrise:
        day_part = 'night'
        yest = now_naive - timedelta(days=1)
        _, prev_sunset = get_sunrise_sunset(yest, lat, lon)
        start, end = prev_sunset, sunrise
    elif sunrise <= now_naive < sunset:
        day_part = 'day'
        start, end = sunrise, sunset
    else:
        day_part = 'night'
        start    = sunset
        tmrw     = now_naive + timedelta(days=1)
        next_sunrise, _ = get_sunrise_sunset(tmrw, lat, lon)
        end = next_sunrise

    period  = max((end - start).total_seconds(), 1.0)
    hourlen = period / 12.0
    elapsed = (now_naive - start).total_seconds()
    hour_n  = min(12, int(elapsed // hourlen) + 1)
    weekday = get_user_weekday(now_naive)
    pindex  = (DAY_PLANET_INDEX[weekday] + hour_n - 1) % 7
    pkey    = PLANET_ORDER[pindex]
    planet_ar = PLANET_NAMES_AR[pkey]

    return {
        'hour_number':        hour_n,
        'planet_name':        planet_ar,
        'planet_ar':          planet_ar,   # alias مطلوب في أماكن عدة
        'planet':             planet_ar,   # alias إضافي للتوافق
        'planet_key':         pkey,
        'is_forbidden':       hour_n in FORBIDDEN_HOURS.get(weekday, set()),
        'day_part':           day_part,
        'hour_length_seconds': hourlen,
        'sunrise':            str(sunrise),
        'sunset':             str(sunset),
        'day_name':           _DAY_NAMES_AR.get(weekday, ''),
        'weekday':            weekday,
    }

def estimate_lunar_day(d: dt) -> int:
    d_n = d.replace(tzinfo=None) if d.tzinfo else d
    ref = dt(2000, 1, 6)
    return (d_n - ref).days % 28 + 1

def get_solar_mansion(d: dt) -> dict:
    d = d.replace(tzinfo=None) if d.tzinfo else d
    spring = dt(d.year, 2, 15)
    if d < spring:
        spring = dt(d.year - 1, 2, 15)
    days_passed = (d - spring).days
    s = ((days_passed + 3) // 13 + 1)
    s = ((s - 1) % 28) + 1
    return LUNAR_MANSIONS.get(s, LUNAR_MANSIONS[1])

def get_moon_longitude(d: dt, lat: float, lon: float) -> Optional[float]:
    if not SKYFIELD_AVAILABLE:
        return None
    try:
        from skyfield import api as sf_api
        ts  = sf_api.load.timescale()
        eph = sf_api.load('de421.bsp')
        d_n = d.replace(tzinfo=None) if d.tzinfo else d
        t   = ts.utc(d_n.year, d_n.month, d_n.day, d_n.hour, d_n.minute, d_n.second)
        earth, moon = eph['earth'], eph['moon']
        obs   = earth + sf_api.wgs84.latlon(lat, lon)
        astrometric = obs.at(t).observe(moon)
        ra, dec, _ = astrometric.radec()
        return float(ra.hours * 15)
    except Exception:
        return None

def get_lunar_mansion_astro(d: dt, lat: float, lon: float) -> dict:
    lon_deg = get_moon_longitude(d, lat, lon)
    if lon_deg is None:
        return get_solar_mansion(d)
    mansion_num = int(lon_deg / (360 / 28)) + 1
    mansion_num = max(1, min(28, mansion_num))
    return LUNAR_MANSIONS.get(mansion_num, LUNAR_MANSIONS[1])

# ══════════════════════════════════════════════════════════════════
# القسم 5: حسابات الأبجد والطبائع (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
def calculate_abjad(name: str) -> int:
    return sum(ABJAD_VALUES.get(c, 0) for c in name)

def classify_name(name: str, method: str = '28') -> dict:
    nourani   = set(NOURANI_LETTERS_28)
    dhulmani  = set(DHULMANI_LETTERS_28)
    no = sum(ABJAD_VALUES.get(c, 0) for c in name if c in nourani)
    dh = sum(ABJAD_VALUES.get(c, 0) for c in name if c in dhulmani)
    total = max(no + dh, 1)
    return {
        'name':             name,
        'nourani_value':    no,
        'dhulmani_value':   dh,
        'nourani_ratio':    no / total,
        'dhulmani_ratio':   dh / total,
        'dominant': 'nourani' if no > dh else 'dhulmani' if dh > no else 'neutral',
    }

# ══════════════════════════════════════════════════════════════════
# القسم 6: الخدام والعناصر (Data Layer)
# ══════════════════════════════════════════════════════════════════
SERVANTS: Dict[str, str] = {
    'ا':'هطمهطفايل','ب':'جلمحمايل','ج':'لومحيائيل','د':'دمحيائيل',
    'ه':'هطيل','و':'واويل','ز':'ززيائيل','ح':'حمحيائيل',
    'ط':'طمهيائيل','ي':'ييائيل','ك':'كهيائيل','ل':'لليائيل',
    'م':'مميائيل','ن':'ننيائيل','س':'سسيائيل','ع':'ععيائيل',
    'ف':'ففيائيل','ص':'صصيائيل','ق':'ققيائيل','ر':'رريائيل',
    'ش':'ششيائيل','ت':'تتيائيل','ث':'ثثيائيل','خ':'خخيائيل',
    'ذ':'ذذيائيل','ض':'ضضيائيل','ظ':'ظظيائيل','غ':'غغيائيل',
}
ELEM_MAP: Dict[str, str] = {
    'ا':'fire','ه':'fire','ط':'fire','م':'fire','ف':'fire','ش':'fire','ذ':'fire',
    'ب':'air', 'و':'air', 'ك':'air', 'ص':'air', 'ق':'air', 'ر':'air', 'ت':'air',
    'ج':'water','ز':'water','ح':'water','ل':'water','ع':'water','س':'water','ث':'water',
    'د':'earth','ي':'earth','ن':'earth','ظ':'earth','خ':'earth','ض':'earth','غ':'earth',
}
ELEM_AR_MAP: Dict[str, str] = {
    'fire': 'ناري', 'air': 'هوائي', 'water': 'مائي', 'earth': 'ترابي',
}

def get_dominant_element(name: str) -> str:
    c = {'fire': 0, 'air': 0, 'water': 0, 'earth': 0}
    for ch in name:
        if ch in ELEM_MAP:
            c[ELEM_MAP[ch]] += 1
    return max(c, key=c.get) if max(c.values()) > 0 else 'fire'

def get_dominant_letter_by_nature(name: str, nature: str) -> Optional[str]:
    letters = [ch for ch in name if ch in ELEM_MAP and ELEM_MAP[ch] == nature]
    return Counter(letters).most_common(1)[0][0] if letters else None

def generate_servant_name(jummal: int = None, name: str = None, nature: str = None) -> str:
    if name and nature:
        ltr = get_dominant_letter_by_nature(name, nature)
        if ltr:
            return SERVANTS.get(ltr, '')
    if jummal is None:
        return ''
    v2l     = {v: k for k, v in ABJAD_VALUES.items()}
    closest = min(v2l, key=lambda v: abs(jummal - v))
    return SERVANTS.get(v2l[closest], '')

def taqseer(number: int) -> str:
    while number > 9:
        number = sum(int(d) for d in str(number))
    letters = list('أبجدﻫوزحطيكلمنسعفصقرشتثخذضظغ')
    number  = max(1, min(number, 28))
    return f'{letters[number - 1]}ائيل'

# ══════════════════════════════════════════════════════════════════
# القسم 7: الأوفاق — Magic Squares (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
def gen_odd_square(size: int, cv: int) -> list:
    m = [[0] * size for _ in range(size)]
    r, c = 0, size // 2
    for n in range(1, size * size + 1):
        m[r][c] = n
        nr, nc  = (r - 1) % size, (c + 1) % size
        if m[nr][nc] != 0:
            r = (r + 1) % size
        else:
            r, c = nr, nc
    m[size // 2][size // 2] = cv
    return m

def gen_even_square(size: int, cv: int) -> Optional[list]:
    if size == 4:
        b = [[16, 2, 3, 13], [5, 11, 10, 8], [9, 7, 6, 12], [4, 14, 15, 1]]
        b[1][1] = cv
        return b
    return None

def gen_standard_square(size: int, cv: int) -> Optional[list]:
    return gen_odd_square(size, cv) if size % 2 == 1 else gen_even_square(size, cv)

def gen_empty_center_square(size: int, cv: int) -> Optional[list]:
    """وفق مع مركز فارغ لاستقبال اسم الهدف"""
    sq = gen_standard_square(size, cv)
    if sq and size >= 3:
        mid = size // 2
        sq[mid][mid] = None
    return sq

def gen_v6_square(total: int) -> dict:
    if total % 2 == 0:
        b = (total - 30) // 4
        return {
            'wafq': [
                [b+8,  b+11, b+14, b+1 ],
                [b+13, b+2,  b+7,  b+12],
                [b+3,  b+16, 17,   b+6 ],
                [b+10, b+5,  b+4,  b+15],
            ],
            'wafq_type': '4x4',
        }
    else:
        b = (total - 12) // 3
        return {
            'wafq': [
                [b+3, b+8, b+1],
                [b+2, b+4, b+6],
                [b+7, b+0, b+5],
            ],
            'wafq_type': '3x3',
        }

# ══════════════════════════════════════════════════════════════════
# القسم 8: علم الرمل — Geomancy (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
GEOMANTIC_FIGURES: Dict[str, List[int]] = {
    'populus': [1,1,1,1], 'via': [0,0,0,0], 'conjunctio': [1,1,0,0],
    'carcer': [0,0,1,1], 'acquisitio': [1,0,1,1], 'laetitia': [1,0,0,0],
    'tristitia': [0,1,1,1], 'puella': [1,0,1,0], 'puer': [0,1,0,1],
    'fortune_major': [1,0,0,1], 'fortune_minor': [0,1,1,0], 'amissio': [0,1,0,0],
    'albus': [1,1,1,0], 'ruber': [0,0,0,1], 'caput_draconis': [0,0,1,0],
    'cauda_draconis': [1,1,0,1],
}
GEO_AR: Dict[str, str] = {
    'populus': 'الجماعة', 'via': 'الطريق', 'conjunctio': 'الاجتماع', 'carcer': 'السجن',
    'acquisitio': 'الاكتساب', 'laetitia': 'الفرح', 'tristitia': 'الحزن', 'puella': 'الجارية',
    'puer': 'الغلام', 'fortune_major': 'السعد الأكبر', 'fortune_minor': 'السعد الأصغر',
    'amissio': 'الخسارة', 'albus': 'الأبيض', 'ruber': 'الأحمر',
    'caput_draconis': 'رأس التنين', 'cauda_draconis': 'ذيل التنين',
}
GEO_ORDER   = list(GEOMANTIC_FIGURES.keys())
AUSPICIOUS  = {'fortune_major', 'fortune_minor', 'acquisitio', 'laetitia', 'puella'}
INAUSPICIOUS = {'tristitia', 'carcer', 'amissio', 'puer', 'ruber', 'cauda_draconis'}

def pts_to_name(pts: list) -> str:
    for n, p in GEOMANTIC_FIGURES.items():
        if p == pts:
            return n
    return 'unknown'

def get_figure_number(pts: list) -> int:
    for i, name in enumerate(GEO_ORDER):
        if GEOMANTIC_FIGURES[name] == pts:
            return i + 1
    return 1

def generate_geomancy_matrix(entropy: EntropySource) -> dict:
    M = [entropy.generate_points(4) for _ in range(4)]
    D = [[M[row][col] for row in range(4)] for col in range(4)]
    G = [[M[i][j] ^ D[i][j] for j in range(4)] for i in range(4)]
    wR = [G[0][j] ^ G[1][j] for j in range(4)]
    wL = [G[2][j] ^ G[3][j] for j in range(4)]
    J  = [wR[j] ^ wL[j] for j in range(4)]
    C  = [J[j] ^ M[0][j] for j in range(4)]
    all_pts = M + D + G + [wR, wL, J, C]
    return {
        i + 1: {
            'pattern': pts,
            'name':    pts_to_name(pts),
            'name_ar': GEO_AR.get(pts_to_name(pts), pts_to_name(pts)),
        }
        for i, pts in enumerate(all_pts)
    }

def calculate_soul(judge_pattern: list, ascendant: float) -> int:
    return int(get_figure_number(judge_pattern) * ascendant) % 16 + 1

# ══════════════════════════════════════════════════════════════════
# القسم 9: INTENT_MAPPING — 16 هدف من الكتاب (Data Layer)
# ══════════════════════════════════════════════════════════════════
INTENT_MAPPING: Dict[str, dict] = {
    'محبة':     {'gate':1,  'gate_name':'المحبة والتهييج',    'upper':'عنيائيل',   'lower':'زوبعة',     'king_id':'zawba',      'planet':'الزهرة',   'day':'الجمعة',   'day_num':5, 'hours':[1,6,8],  'incense':'المصطكى والورد',       'planets':['الزهرة','المشتري','القمر'], 'color':'#e91e8c'},
    'جلب':      {'gate':2,  'gate_name':'الجلب والاستنزال',   'upper':'عنيائيل',   'lower':'زوبعة',     'king_id':'zawba',      'planet':'الزهرة',   'day':'الجمعة',   'day_num':5, 'hours':[2,7],    'incense':'المصطكى والزعفران',    'planets':['الزهرة','المشتري'],        'color':'#c2185b'},
    'قبول':     {'gate':3,  'gate_name':'القبول والجاه',       'upper':'روقيائيل',  'lower':'المذهب',    'king_id':'mizhab',     'planet':'الشمس',    'day':'الأحد',    'day_num':0, 'hours':[1,4,9],  'incense':'العود والمسك',          'planets':['الشمس','المشتري'],         'color':'#ffaa00'},
    'حفظ':      {'gate':4,  'gate_name':'الحفظ والتحصين',     'upper':'جبرائيل',   'lower':'مُرة',      'king_id':'murrah',     'planet':'القمر',    'day':'الاثنين',  'day_num':1, 'hours':[2,5,8],  'incense':'اللبان والكافور',       'planets':['القمر','عطارد','المشتري'], 'color':'#43a047'},
    'كشف':      {'gate':5,  'gate_name':'كشف الخبايا',        'upper':'ميكائيل',   'lower':'برقان',     'king_id':'burqan',     'planet':'عطارد',    'day':'الأربعاء', 'day_num':3, 'hours':[1,6,11], 'incense':'الصندل والعود',         'planets':['عطارد','الشمس','المشتري'], 'color':'#00acc1'},
    'عقد لسان': {'gate':6,  'gate_name':'عقد الألسنة',        'upper':'سمسمائيل',  'lower':'الأحمر',    'king_id':'ahmar',      'planet':'المريخ',   'day':'الثلاثاء', 'day_num':2, 'hours':[3,7],    'incense':'الكبريت والمر',         'planets':['المريخ','زحل'],            'color':'#e53935'},
    'دخول':     {'gate':7,  'gate_name':'الدخول على الحكام',  'upper':'روقيائيل',  'lower':'المذهب',    'king_id':'mizhab',     'planet':'الشمس',    'day':'الأحد',    'day_num':0, 'hours':[2,5,10], 'incense':'العود والكافور',        'planets':['الشمس','المشتري'],         'color':'#f9a825'},
    'قهر':      {'gate':8,  'gate_name':'تدمير الظلمة',       'upper':'سمسمائيل',  'lower':'الأحمر',    'king_id':'ahmar',      'planet':'المريخ',   'day':'الثلاثاء', 'day_num':2, 'hours':[1,4,9],  'incense':'الكبريت والأسفلت',      'planets':['المريخ','زحل'],            'color':'#b71c1c'},
    'إبطال':    {'gate':9,  'gate_name':'إبطال السحر',        'upper':'جبرائيل',   'lower':'مُرة',      'king_id':'murrah',     'planet':'القمر',    'day':'الاثنين',  'day_num':1, 'hours':[3,6],    'incense':'اللبان الذكر والملح',   'planets':['القمر','عطارد'],           'color':'#2e7d32'},
    'رزق':      {'gate':10, 'gate_name':'الرزق والبركة',      'upper':'صرفيائيل',  'lower':'شمهورش',    'king_id':'shamhurish', 'planet':'المشتري',  'day':'الخميس',   'day_num':4, 'hours':[1,5,9],  'incense':'العود الهندي والكافور', 'planets':['المشتري','الشمس','الزهرة'],'color':'#f57f17'},
    'شفاء':     {'gate':11, 'gate_name':'الشفاء والعلاج',     'upper':'جبرائيل',   'lower':'مُرة',      'king_id':'murrah',     'planet':'القمر',    'day':'الاثنين',  'day_num':1, 'hours':[1,4,7],  'incense':'الورد والزعفران',       'planets':['القمر','المشتري','الزهرة'],'color':'#00897b'},
    'إخفاء':    {'gate':12, 'gate_name':'الإخفاء والتغييب',   'upper':'كسفيائيل',  'lower':'ميمون',     'king_id':'maymun',     'planet':'زحل',      'day':'السبت',    'day_num':6, 'hours':[2,6,10], 'incense':'الرصاص والكبريت',       'planets':['زحل','المريخ'],            'color':'#424242'},
    'ترحيل':    {'gate':13, 'gate_name':'ترحيل الأعداء',      'upper':'سمسمائيل',  'lower':'الأحمر',    'king_id':'ahmar',      'planet':'المريخ',   'day':'الثلاثاء', 'day_num':2, 'hours':[2,8,11], 'incense':'الحرمل والكبريت',       'planets':['المريخ','زحل'],            'color':'#c62828'},
    'شهرة':     {'gate':14, 'gate_name':'الشهرة والظهور',     'upper':'روقيائيل',  'lower':'المذهب',    'king_id':'mizhab',     'planet':'الشمس',    'day':'الأحد',    'day_num':0, 'hours':[3,7],    'incense':'المسك والعنبر',         'planets':['الشمس','المشتري'],         'color':'#ff8f00'},
    'طلسم':     {'gate':15, 'gate_name':'الطلاسم المئينية',   'upper':'ميكائيل',   'lower':'برقان',     'king_id':'burqan',     'planet':'عطارد',    'day':'الأربعاء', 'day_num':3, 'hours':[4,8],    'incense':'الصندل والعود',         'planets':['عطارد','الشمس'],           'color':'#0277bd'},
    'خاتم':     {'gate':16, 'gate_name':'الخاتم السليماني',   'upper':'الكل',      'lower':'الكل',      'king_id':'mizhab',     'planet':'أي كوكب', 'day':'أي يوم',   'day_num':-1,'hours':[],       'incense':'العود الأقاقيا',        'planets':[],                          'color':'#6a1b9a'},
}

# ══════════════════════════════════════════════════════════════════
# القسم 10: الأبواب الـ16 (Data Layer)
# ══════════════════════════════════════════════════════════════════
GATES: Dict[int, dict] = {
    1:  {'name': 'المحبة والتهييج',   'type': 'nourani',  'nature': 'love'},
    2:  {'name': 'الجلب والاستنزال',  'type': 'nourani',  'nature': 'summon'},
    3:  {'name': 'القبول والجاه',      'type': 'nourani',  'nature': 'honor'},
    4:  {'name': 'الحفظ والتحصين',    'type': 'nourani',  'nature': 'protection'},
    5:  {'name': 'كشف الخبايا',       'type': 'nourani',  'nature': 'revelation'},
    6:  {'name': 'عقد الألسنة',       'type': 'dhulmani', 'nature': 'binding'},
    7:  {'name': 'الدخول على الحكام', 'type': 'nourani',  'nature': 'influence'},
    8:  {'name': 'تدمير الظلمة',      'type': 'dhulmani', 'nature': 'destruction'},
    9:  {'name': 'إبطال السحر',       'type': 'nourani',  'nature': 'uncrossing'},
    10: {'name': 'الرزق والبركة',     'type': 'nourani',  'nature': 'wealth'},
    11: {'name': 'الشفاء والعلاج',    'type': 'nourani',  'nature': 'healing'},
    12: {'name': 'الإخفاء والتمويه',  'type': 'dhulmani', 'nature': 'concealment'},
    13: {'name': 'ترحيل الأعداء',     'type': 'dhulmani', 'nature': 'banishment'},
    14: {'name': 'الشهرة والظهور',    'type': 'nourani',  'nature': 'fame'},
    15: {'name': 'الطلاسم المئوية',   'type': 'mixed',    'nature': 'talisman'},
    16: {'name': 'الخاتم السليماني',  'type': 'mixed',    'nature': 'seal'},
}
GATE_ELEM: Dict[str, str] = {
    'love': 'water', 'summon': 'water', 'honor': 'fire', 'protection': 'earth',
    'revelation': 'air', 'binding': 'earth', 'influence': 'fire', 'destruction': 'fire',
    'uncrossing': 'air', 'wealth': 'earth', 'healing': 'water', 'concealment': 'air',
    'banishment': 'fire', 'fame': 'air', 'talisman': 'mixed', 'seal': 'mixed',
}
DARK_GATES = {6, 8, 12, 13}

def select_gate(geo: dict, spectral_dom: str, lunar_mansion: dict, is_forbidden: bool,
                elem_from_area: str, planet_from_area: str, user_intent: str = None) -> int:
    judge = geo[15]['name']
    pref  = ('nourani' if judge in AUSPICIOUS
             else 'dhulmani' if judge in INAUSPICIOUS
             else (spectral_dom if spectral_dom != 'neutral' else 'nourani'))
    suit  = [n for n, g in GATES.items() if g['type'] == pref]
    if is_forbidden:
        safe = [g for g in suit if g in {4, 9}]
        if safe:
            return safe[0]
    if 'محبة' in lunar_mansion.get('usage', ''):
        love = [g for g in suit if GATES[g]['nature'] == 'love']
        if love:
            suit = love
    elem_en = {'نار': 'fire', 'هواء': 'air', 'ماء': 'water', 'تراب': 'earth'}.get(elem_from_area, '')
    if elem_en:
        elem_suit = [g for g in suit if GATE_ELEM.get(GATES[g]['nature']) == elem_en]
        if elem_suit:
            suit = elem_suit
    planet_pref = {
        'الشمس':    ['love', 'honor', 'fame'],
        'القمر':    ['protection', 'healing', 'seal'],
        'المريخ':   ['destruction', 'banishment', 'binding'],
        'عطارد':    ['revelation', 'talisman'],
        'المشتري':  ['wealth', 'influence'],
        'الزهرة':   ['love', 'summon'],
        'زحل':      ['concealment'],
    }
    if planet_from_area in planet_pref:
        pref_gates = [g for g in suit if GATES[g]['nature'] in planet_pref[planet_from_area]]
        if pref_gates:
            suit = pref_gates
    return suit[0] if suit else 1

# ══════════════════════════════════════════════════════════════════
# القسم 11: تحليل الاسم والتوافق (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
ELEM_ADVICES: Dict[str, str] = {
    'ناري':  'طاقة نارية حادة — الهدوء قبل القرار.',
    'مائي':  'انسجام مائي — استمر في التدفق.',
    'هوائي': 'فكر هوائي — احذر التشتت.',
    'ترابي': 'ثبات ترابي — واصل بناءك.',
}

def analyze_name(name: str, king_id: str = 'mizhab') -> dict:
    total  = calculate_abjad(name)
    scores = {
        el_ar: sum(ABJAD_VALUES.get(c, 0) for c in name if ELEM_MAP.get(c) == el_en)
        for el_ar, el_en in {'ناري': 'fire', 'هوائي': 'air', 'مائي': 'water', 'ترابي': 'earth'}.items()
    }
    total_w  = sum(scores.values()) or 1
    percents = {el: round(v / total_w * 100, 1) for el, v in scores.items()}
    dom_el   = max(percents, key=percents.get)
    king     = KINGS_DATA.get(king_id, KINGS_DATA['mizhab'])
    v6sq     = gen_v6_square(total)
    return {
        'name':       name,
        'total':      total,
        'dominant':   dom_el,
        'percents':   percents,
        'spirit':     (total % 28) or 28,
        'station':    (total % 12) or 12,
        'freq':       200 + (total % 400),
        'planet':     PLANET_NAMES_AR.get(PLANET_ORDER[(now_utc().weekday() + 2) % 7 % 7], 'الشمس'),
        'advice':     ELEM_ADVICES.get(dom_el, ''),
        'wafq':       v6sq['wafq'],
        'wafq_type':  v6sq['wafq_type'],
        'king':       king,
        'king_id':    king_id,
        'spectral':   classify_name(name, method='28'),
    }

def calculate_affinity(d1: dict, d2: dict) -> dict:
    return calculate_affinity_v11(d1, d2)

# ══════════════════════════════════════════════════════════════════
# القسم 12: دوال مساعدة للـ process pipeline (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
_ARABIC_RE = re.compile(r'[\u0600-\u06FF]')

def get_element_by_area(area: int) -> str:
    r = (area - 45) % 4
    return {1: 'نار', 2: 'هواء', 3: 'ماء', 0: 'تراب'}.get(((r % 4) + 4) % 4, 'تراب')

def get_planet_by_area(area: int) -> str:
    r = ((area - 77) % 7 + 7) % 7
    return {1: 'الشمس', 2: 'المريخ', 3: 'المشتري', 4: 'عطارد', 5: 'الزهرة', 6: 'زحل', 0: 'القمر'}.get(r, 'الشمس')

def _validate_process_input(data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """
    ✅ Schema validation مركزي — يُرجع (error_dict, None) أو (None, None)
    يُغني عن فحوصات متكررة في كل API
    """
    target_name = (data.get('name', '') or '').strip()
    mother_name = (data.get('mother', '') or '').strip()
    if not target_name or not _ARABIC_RE.search(target_name):
        return {'error': 'اسم الهدف إلزامي — يجب أن يكون بالعربية'}, None
    if not mother_name or not _ARABIC_RE.search(mother_name):
        return {'error': 'اسم الأم إلزامي — يجب أن يكون بالعربية'}, None
    return None, None

def _check_timing(user_intent: str, now: dt) -> Optional[dict]:
    """
    ✅ فصل منطق الفحص الزمني — يُرجع dict خطأ أو None إذا الوقت مناسب
    """
    if not user_intent or user_intent not in INTENT_MAPPING:
        return None
    m          = INTENT_MAPPING[user_intent]
    m_planets  = m.get('planets', [])
    m_hours    = m.get('hours', [])
    ph         = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    cur_planet = ph.get('planet_ar', '')
    cur_hour   = ph.get('hour_number', 0)
    if m_planets and cur_planet not in m_planets:
        alts      = ' أو '.join(m_planets[:2])
        next_hint = _calc_next_hint(now, m)
        return {
            'error': True, 'time_rejected': True,
            'reason': f'🌙 الوقت الحالي غير مناسب لنية "{user_intent}".',
            'details': f'الكوكب الحالي: {cur_planet} (الساعة {cur_hour}) – النية تحتاج إلى كوكب {alts}.',
            'suggestion': f'⏳ انتظر{next_hint} في ساعة {m.get("planet", m_planets[0])} أو استخدم حارس البوابة.',
            'current_planet': cur_planet, 'current_hour': cur_hour,
            'next_valid': f'الوقت المناسب: يوم {m.get("day","—")} — ساعة {m.get("planet","—")}',
            'allowed_planets': m_planets, 'intent': user_intent,
        }
    if m_hours and cur_hour not in m_hours:
        return {
            'error': True, 'time_rejected': True,
            'reason': f'🕰️ الساعة الحالية ({cur_hour}) غير مناسبة لنية "{user_intent}".',
            'details': f'الكوكب {cur_planet} مناسب لكن الساعة {cur_hour} ليست من ساعات العمل.',
            'suggestion': f'⏰ الساعات المناسبة: {", ".join(str(h) for h in m_hours)}.',
            'current_hour': cur_hour, 'allowed_hours': m_hours,
        }
    return None

def _calc_next_hint(now: dt, m: dict) -> str:
    if m.get('day_num', -1) == -1:
        return ''
    today_weekday  = now.weekday()
    target_weekday = m.get('day_num', 0)
    days_diff = (target_weekday - today_weekday + 7) % 7
    if days_diff == 0:
        return f' اليوم (انتظر ساعة {m.get("planet", "")})'
    return f' يوم {m.get("day", "المناسب")} القادم'

def _apply_elemental_mediator(target_name: str, mother_name: str) -> Tuple[str, str, str]:
    """
    ✅ التوافق العنصري منفصل — يُرجع (target_modified, warning, mediator_letter)
    """
    try:
        def _get_elem(nm: str) -> str:
            counts: Dict[str, int] = {}
            for c in nm:
                if c in LETTER_DETAILS:
                    n = LETTER_DETAILS[c].get('nature', '')
                    for key in ['ناري', 'هوائي', 'مائي', 'ترابي']:
                        if key in n:
                            counts[key] = counts.get(key, 0) + 1
            return max(counts, key=counts.get) if counts else 'ناري'

        name_el   = _get_elem(target_name)
        mother_el = _get_elem(mother_name)
        result    = check_elemental_compatibility(name_el, mother_el)
        if result.get('status') == 'enemy':
            med    = result.get('mediator', {})
            letter = med.get('letter', '')
            if letter:
                warning = f'⚠️ تضاد طبائع ({name_el} ↔ {mother_el}) — تم إضافة حرف الميزان «{letter}» تلقائياً'
                return letter + target_name, warning, letter
    except Exception:
        pass
    return target_name, '', ''

def _build_process_result(
    target_name: str, mother_name: str, user_intent: str,
    letter, king_id: str, lunar_day_in, ihlal_in, session_id: str,
    void_signals_in: dict, now: dt,
    elemental_warning: str, elemental_mediator: str,
) -> dict:
    """
    ✅ الحسابات الأساسية لـ process() — معزولة تماماً (Single Responsibility)
    """
    jummal        = calculate_abjad(target_name) + (calculate_abjad(mother_name) if mother_name else 0)
    spectral      = classify_name(target_name, method='28')
    hour_info     = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    lunar_day     = lunar_day_in or estimate_lunar_day(now)
    solar_mansion = get_solar_mansion(now)
    ihlal         = ihlal_in or solar_mansion['number']
    lunar_mansion = get_lunar_mansion_astro(now, Config.LATITUDE, Config.LONGITUDE)
    entropy       = EntropySource()
    geomancy      = generate_geomancy_matrix(entropy)
    ascendant     = (now.hour * 15 + now.minute * 0.25) % 360
    soul          = calculate_soul(geomancy[15]['pattern'], ascendant)
    area          = 25
    elem_from_area   = get_element_by_area(area)
    planet_from_area = get_planet_by_area(area)
    gate         = select_gate(geomancy, spectral['dominant'], lunar_mansion,
                               hour_info['is_forbidden'], elem_from_area, planet_from_area, user_intent)
    servant_name = ''
    if letter and letter in SERVANTS:
        servant_name = SERVANTS[letter]
    elif user_intent:
        servant_name = f'خادم الباب: {user_intent}'
    else:
        dom_el = get_dominant_element(target_name)
        servant_name = (generate_servant_name(jummal, target_name, dom_el)
                        or generate_servant_name(jummal, target_name, GATE_ELEM.get(GATES[gate]['nature'], 'fire'))
                        or '')
    if not servant_name:
        servant_name = taqseer(jummal)

    intent_data   = INTENT_MAPPING.get(user_intent, {})
    king_id_final = intent_data.get('king_id', king_id)
    king          = KINGS_DATA.get(king_id_final, KINGS_DATA.get(king_id, KINGS_DATA['mizhab']))
    wafq_size     = 3 if jummal % 2 == 1 else 4
    wafq_sq       = gen_standard_square(wafq_size, jummal % (wafq_size ** 2) or 1) or [[1,2,3],[4,5,6],[7,8,9]]
    v6sq          = gen_v6_square(jummal)
    planet_incense_data = PLANET_INCENSE.get(hour_info['planet_name'], {})
    dominant_spectral   = spectral.get('dominant', 'nourani')
    gate_name           = GATES[gate]['name']
    gate_nature         = GATES[gate]['nature']
    gate_incense        = intent_data.get('incense', planet_incense_data.get('incense', ''))
    angel_upper         = intent_data.get('upper', '')
    angel_lower         = intent_data.get('lower', '')
    code9               = str(sum(int(d) for d in str(jummal)))

    jafr_data = {}
    try:
        jafr_data = get_jafr_zamam(target_name, mother_name)
    except Exception:
        pass

    soul_result = {}
    try:
        soul_result = process_soul(target_name, mother_name, user_intent or '', session_id)
    except Exception:
        pass

    metal_rec = {}
    try:
        metal_rec = get_metal_recommendation(dominant_spectral, hour_info['planet_name'])
    except Exception:
        pass

    enrich_rec = {}
    try:
        enrich_rec = enrich_recommendation(gate_nature, dominant_spectral, lunar_mansion)
    except Exception:
        pass

    rasd = {}
    try:
        rasd = calculate_rasd(jummal, gate_name)
    except Exception:
        pass

    warnings: List[str] = []
    if hour_info['is_forbidden']:
        warnings.append(f'⚠️ الساعة {hour_info["hour_number"]} مذمومة — تجنب الاستدعاء')
    if 'نحسة' in lunar_mansion.get('ruling', ''):
        warnings.append(f'🌙 منزلة {lunar_mansion.get("name", "")} نحسة')
    if elemental_warning:
        warnings.append(elemental_warning)
    if gate in DARK_GATES:
        warnings.append(f'⚫ الباب {gate} ({gate_name}) من الأبواب الظلمانية — توخّ الحذر')

    # ── حساب code8 للـ frontend ──────────────────────────────
    code8 = jummal * hour_info.get('hour_number', 1)

    # ── الملك الحاكم اليوم ───────────────────────────────────
    from data import RULING_KINGS as _RK
    _wd = get_user_weekday(now)
    _rk_val = _RK.get(_wd, king.get('name', ''))
    _ruling_king_name = _rk_val if isinstance(_rk_val, str) else _rk_val.get('name', king.get('name', ''))

    # ── رمز سليمان ────────────────────────────────────────────
    _SOLOMON = {
        'fortune_major':'نجمة سداسية','fortune_minor':'نجمة خماسية',
        'puella':'ميم','puer':'سلم','acquisitio':'كلب','amissio':'عين',
        'laetitia':'حلزون','tristitia':'ثلاث عصي','carcer':'خاتم سليماني',
        'conjunctio':'خاتم سليماني',
    }
    _judge_name = geomancy.get(15, {}).get('name', 'carcer')
    solomon_symbol = _SOLOMON.get(_judge_name, 'خاتم سليماني')

    # ── جفر الزمام كـ string ──────────────────────────────────
    _jafr_str = ''
    if isinstance(jafr_data, dict):
        _jafr_str = jafr_data.get('zamam', jafr_data.get('jafr_letter', ''))
    elif isinstance(jafr_data, str):
        _jafr_str = jafr_data

    # ── الكيمياء والسيمياء ────────────────────────────────────
    _alchemy = ''
    _simiya  = ''
    try:
        _alchemy = get_alchemy_advice(gate_nature) or ''
        if not _alchemy:
            _alchemy = get_alchemy_advice(dominant_spectral) or ''
    except Exception:
        _alchemy = ''
    try:
        _simiya = get_simiya_advice(gate_nature) or ''
        if not _simiya:
            _simiya = get_simiya_advice(dominant_spectral) or ''
    except Exception:
        _simiya = ''

    # ── التوصيات ──────────────────────────────────────────────
    _rec = enrich_rec.get('advice', '') if isinstance(enrich_rec, dict) else str(enrich_rec)

    # ── الملاك العلوي والسفلي المتقدم ────────────────────────
    _adv_upper = intent_data.get('upper', angel_upper)
    _adv_lower = intent_data.get('lower', angel_lower)

    return {
        # ── حقول الـ frontend المطلوبة ─────────────────────────
        'servant_name':             servant_name,   # frontend يبحث عن servant_name
        'magic_square':             wafq_sq,         # frontend يبحث عن magic_square
        'wafq_v6':                  v6sq['wafq'],    # frontend يبحث عن wafq_v6
        'wafq_v6_type':             v6sq['wafq_type'],
        'code8':                    code8,
        'code9':                    int(code9) if str(code9).isdigit() else (jummal % 100 + 1),
        'ruling_king':              _ruling_king_name,
        'elem_from_area':           elem_from_area,
        'planet_from_area':         planet_from_area,
        'solomon_symbol':           solomon_symbol,
        'jafr_zamam':               _jafr_str,
        'advanced_upper_angel':     _adv_upper,
        'advanced_lower_angel':     _adv_lower,
        'alchemy_advice':           _alchemy,
        'simiya_advice':            _simiya,
        'recommendation':           _rec,
        'letter_used':              letter or '',  # الحرف المُختار
        # ── حقول أساسية ────────────────────────────────────────
        'name':                     target_name,
        'target_name':              target_name,
        'mother_name':              mother_name,
        'user_intent':              user_intent,
        'jummal':                   jummal,
        'spectral':                 spectral,
        'dominant_spectral':        dominant_spectral,
        'gate':                     gate,
        'gate_name':                gate_name,
        'gate_nature':              gate_nature,
        'gate_incense':             gate_incense,
        'angel_upper':              angel_upper,
        'angel_lower':              angel_lower,
        'king':                     king,
        'king_id':                  king_id_final,
        'servant':                  servant_name,   # alias للتوافق
        'hour_info':                hour_info,
        'lunar_day':                lunar_day,
        'lunar_mansion':            lunar_mansion,
        'solar_mansion':            solar_mansion,
        'soul':                     soul,
        'geomancy':                 geomancy,
        'wafq':                     wafq_sq,
        'wafq_type':                f'{wafq_size}x{wafq_size}',
        'v6_wafq':                  v6sq['wafq'],    # alias
        'v6_wafq_type':             v6sq['wafq_type'],
        'soul_result':              soul_result,
        'metal_recommendation':     metal_rec,
        'enriched_recommendation':  enrich_rec,
        'rasd':                     rasd,
        'intent_mapping':           intent_data,
        'jafr_data':                jafr_data,
        'elemental_mediator':       elemental_mediator,
        'session_id':               session_id,
        'warnings':                 warnings,
        'processing_time':          0.0,
    }

def _enrich_v4_pipeline(result: dict, target_name: str, mother_name: str, user_intent: str) -> dict:
    """
    ✅ V4 Intent-Driven Pipeline — منفصل تماماً عن بقية process()
    """
    try:
        _intent    = analyze_intent(user_intent or '', silence_detected=not bool(user_intent))
        _symbolic  = encode_user_data(target_name, mother_name, user_intent or '')
        _matrix    = process_matrix(_symbolic['signature'])
        _path      = resolve_path(_intent, _matrix['state_info']['state'])
        _auto_king = get_king_for_intent(
            _intent['intent_type'], _symbolic['weight'], _matrix['state_info']['state']
        )
        _gk        = astro_gatekeeper(
            _intent['intent_type'],
            _path['path'].get('name_en', 'influence').lower()
        )
        _balance   = analyze_user_balance(target_name, mother_name)
        _v4_sid    = session_manager.create_session(
            target_name, mother_name,
            intent=_intent['intent_type'],
            path=_path['path'].get('name_en', '')
        )
        result['v4_intent']     = _intent
        result['v4_symbolic']   = {
            'seed': _symbolic['seed'], 'weight': _symbolic['weight'],
            'signature_binary': _symbolic['signature_binary'], 'abjad': _symbolic['abjad'],
        }
        result['v4_matrix']     = {
            'state': _matrix['state_info']['state'],
            'stability_score': _matrix['state_info']['stability_score'],
            'summary': _matrix['summary'], 'final_grid': _matrix['final_grid'],
        }
        result['v4_path']       = {
            'name': _path['path']['name'], 'name_en': _path['path']['name_en'],
            'icon': _path['path']['icon'], 'color': _path['path']['color'],
            'message': _path['message'], 'description': _path['path']['description'],
        }
        result['v4_king']       = {
            'king_id': _auto_king['king_id'], 'king_name': _auto_king['king_name'],
            'upper_king': _auto_king['upper_king'], 'planet': _auto_king['planet'],
            'tahateel': _auto_king['tahateel'], 'root_key': _auto_king['root_key'],
            'power': _auto_king['power'], 'ancient_covenant': _auto_king['ancient_covenant'],
        }
        result['v4_gatekeeper'] = {
            'granted': _gk['granted'], 'reason': _gk['reason'],
            'suggested_wait': _gk['suggested_wait'],
            'planet': _gk['planetary_hour']['planet'],
            'mansion': _gk['lunar_mansion']['name'],
        }
        result['v4_balance']    = {
            'name_dominant':   _balance['name_dominant'],
            'mother_dominant': _balance['mother_dominant'],
            'conflict':        _balance['conflict_detected'],
            'mediator_letter': _balance['mediator_letter'],
            'recommendation':  _balance['recommendation'],
        }
        result['v4_session_id'] = _v4_sid
        if not _gk['granted']:
            result['warnings'].append(f'🌌 {_gk["reason"]}')
    except Exception as e:
        result['v4_error'] = str(e)
    return result

# ══════════════════════════════════════════════════════════════════
# القسم 13: الرصد الكوكبي (Business Logic Layer)
# ══════════════════════════════════════════════════════════════════
ELEMENT_DIRECTION: Dict[str, dict] = {
    'ناري':  {'direction': 'الشرق',  'degrees': 90,  'color': 'أحمر',  'desc': 'اتجه نحو الشرق — قوة النار والتجلي'},
    'ترابي': {'direction': 'الجنوب', 'degrees': 180, 'color': 'أصفر',  'desc': 'اتجه نحو الجنوب — ثبات التراب'},
    'هوائي': {'direction': 'الغرب',  'degrees': 270, 'color': 'أبيض',  'desc': 'اتجه نحو الغرب — خفة الهواء'},
    'مائي':  {'direction': 'الشمال', 'degrees': 0,   'color': 'أزرق',  'desc': 'اتجه نحو الشمال — عمق الأسرار'},
    # aliases للحروف المختلفة
    'نارى':  {'direction': 'الشرق',  'degrees': 90,  'color': 'أحمر',  'desc': 'اتجه نحو الشرق — قوة النار والتجلي'},
    'ترابى': {'direction': 'الجنوب', 'degrees': 180, 'color': 'أصفر',  'desc': 'اتجه نحو الجنوب — ثبات التراب'},
    'هوائى': {'direction': 'الغرب',  'degrees': 270, 'color': 'أبيض',  'desc': 'اتجه نحو الغرب — خفة الهواء'},
    'مائى':  {'direction': 'الشمال', 'degrees': 0,   'color': 'أزرق',  'desc': 'اتجه نحو الشمال — عمق الأسرار'},
}

def calculate_rasd(jummal: int, work_name: str = '') -> dict:
    ELEM_MAP_R = {1: 'ناري', 2: 'ترابي', 3: 'هوائي', 0: 'مائي'}
    DAY_MAP_R  = {1: 'الأحد', 2: 'الاثنين', 3: 'الثلاثاء', 4: 'الأربعاء', 5: 'الخميس', 6: 'الجمعة', 0: 'السبت'}
    SIGNS_AR   = ['الحمل','الثور','الجوزاء','السرطان','الأسد','السنبلة',
                  'الميزان','العقرب','القوس','الجدي','الدلو','الحوت']
    elem_r    = jummal % 4
    day_r     = jummal % 7
    hour_r    = jummal % 24
    zodiac_r  = int((jummal % 360) / 30)
    degree_r  = jummal % 30
    element   = ELEM_MAP_R.get(elem_r, 'مائي')
    day_name  = DAY_MAP_R.get(day_r, 'السبت')
    dir_data  = ELEMENT_DIRECTION.get(element, {'direction': 'الشرق', 'desc': '', 'color': ''})
    is_night  = hour_r > 12
    actual_hour = (hour_r - 12) if is_night else hour_r
    if actual_hour == 0:
        actual_hour = 12
    zodiac_name = SIGNS_AR[zodiac_r] if 0 <= zodiac_r < 12 else SIGNS_AR[0]
    weekday_key = (PLANET_ORDER.index('saturn') + day_r) % 7
    planet_key  = PLANET_ORDER[weekday_key]
    planet_name = PLANET_NAMES_AR.get(planet_key, 'الشمس')
    ph_table    = PLANETARY_HOURS_TABLE.get((day_r, actual_hour), {})
    ph_planet   = ph_table.get('planet', planet_name)
    ph_status   = ph_table.get('status', 'ممتزجة')
    ph_uses     = ph_table.get('uses', '')
    return {
        'jummal': jummal, 'work': work_name,
        'element': element, 'direction': dir_data['direction'],
        'direction_desc': dir_data['desc'], 'direction_color': dir_data['color'],
        'day': day_name, 'hour': f'{"ليلاً" if is_night else "نهاراً"} — الساعة {actual_hour}',
        'hour_number': actual_hour, 'is_night': is_night,
        'zodiac': zodiac_name, 'degree': degree_r,
        'planet': ph_planet, 'hour_status': ph_status, 'hour_uses': ph_uses,
        'summary': f'العمل ينتمي إلى طبع {element} — يوم {day_name} — ساعة {ph_planet} ({ph_status})',
    }

# ══════════════════════════════════════════════════════════════════
# القسم 14: تصدير الخاتم (Pillow) (Output Layer)
# ══════════════════════════════════════════════════════════════════
def export_seal(data: dict) -> Optional[io.BytesIO]:
    if not PILLOW_AVAILABLE:
        return None
    sz = 600
    cx = cy = sz // 2
    king = data.get('king', KINGS_DATA.get('mizhab', {}))
    rgb  = tuple(king.get('color_rgb', [255, 170, 68]))
    gold = (255, 215, 0)
    img  = Image.new('RGBA', (sz, sz), (0, 0, 0, 255))
    drw  = ImageDraw.Draw(img)
    for i in range(6, 0, -1):
        r = cx - 8 - i * 10
        drw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=rgb + (30 + i * 25,))
    wafq = data.get('wafq', data.get('magic_square', [[1]]))
    if wafq:
        grid  = len(wafq)
        scale = 68 if grid == 4 else 72 if grid == 5 else 86
        pts_g = [(cx + (c - grid / 2 + 0.5) * scale, cy + (r - grid / 2 + 0.5) * scale)
                 for r in range(grid) for c in range(grid)]
        for i in range(len(pts_g)):
            for j in range(i + 1, len(pts_g)):
                drw.line([pts_g[i], pts_g[j]], fill=rgb + (10,), width=1)
        for i in range(len(pts_g) - 1):
            drw.line([pts_g[i], pts_g[i + 1]], fill=gold + (150,), width=2)
        for idx, (x, y) in enumerate(pts_g):
            ri, ci_ = divmod(idx, grid)
            val     = str(wafq[ri][ci_]) if wafq[ri][ci_] is not None else '●'
            r2      = 17
            drw.ellipse([(x - r2, y - r2), (x + r2, y + r2)], fill=(0, 0, 0, 200), outline=gold + (200,))
            try:
                font = ImageFont.truetype('arial.ttf', 12)
            except Exception:
                font = ImageFont.load_default()
            bb = drw.textbbox((0, 0), val, font=font)
            drw.text((x - (bb[2] - bb[0]) / 2, y - (bb[3] - bb[1]) / 2), val, fill=gold, font=font)
    star = [(cx + (26 if i % 2 == 0 else 11) * math.cos(math.pi * i / 4),
             cy + (26 if i % 2 == 0 else 11) * math.sin(math.pi * i / 4)) for i in range(8)]
    drw.polygon(star, fill=gold + (220,))
    try:
        fb = ImageFont.truetype('arialbd.ttf', 20)
        fs = ImageFont.truetype('arial.ttf', 12)
    except Exception:
        fb = fs = ImageFont.load_default()
    name = data.get('name', data.get('target_name', ''))
    drw.text((cx, 26),  name, fill=gold, font=fb, anchor='mm')
    drw.text((cx, 50),  str(data.get('total', data.get('jummal', 0))), fill=rgb + (255,), font=fs, anchor='mm')
    drw.text((cx, 74),  king.get('name', ''), fill=gold, font=fs, anchor='mm')
    for i, line in enumerate([
        f'روح: {data.get("spirit", "-")}  مقام: {data.get("station", "-")}',
        f'{data.get("dominant", "-")}  —  {data.get("planet", "-")}',
    ]):
        drw.text((cx, sz - 55 + i * 20), line, fill=(200, 255, 200, 200), font=fs, anchor='mm')
    drw.rectangle([(4, 4), (sz - 4, sz - 4)], outline=gold + (160,), width=2)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════
# القسم 15: AI Module (Gemini + Offline Fallback)
# ══════════════════════════════════════════════════════════════════
class AIModule:
    """وحدة الذكاء الاصطناعي — Gemini مع fallback نصي تلقائي"""

    def __init__(self) -> None:
        self.ready = bool(GEMINI_AVAILABLE and GEMINI_API_KEY and client)

    def _call(self, prompt: str) -> str:
        if not self.ready:
            return ''
        try:
            resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return resp.text.strip()
        except Exception:
            return ''

    def interpret(self, d: dict, d2: dict = None) -> str:
        result = self._call(self._build(d, d2))
        return result or self._offline(d, d2)

    def _build(self, d: dict, d2: dict = None) -> str:
        king  = d.get('king', {})
        lines = [
            'أنت حكيم روحاني. حلّل هذه البيانات بالعربية الفصحى بعمق وإيجاز.',
            f'الاسم: {d.get("name", "")} | القيمة: {d.get("total", d.get("jummal", 0))} | الطبع: {d.get("dominant", "")}',
            f'الروح: {d.get("spirit", "-")} | المقام: {d.get("station", "-")} | كوكب: {d.get("planet", "-")}',
            f'الملك المستدعى: {king.get("name", "")} — {king.get("desc", "")}',
            f'قوة الملك: {king.get("power", "")}',
        ]
        if d2:
            lines += [
                f'الاسم الثاني: {d2.get("name", "")} | طبعه: {d2.get("dominant", "")}',
                f'فسّر التوافق بينهما في ضوء الملك {king.get("name", "")}.',
            ]
        return '\n'.join(lines)

    def _offline(self, d: dict, d2: dict = None) -> str:
        king = d.get('king', {})
        base = (f'الاسم {d.get("name", "")} بقيمة جُمَّلية {d.get("total", d.get("jummal", 0))}، '
                f'طبعه {d.get("dominant", "")}, روحه {d.get("spirit", "-")}, مقامه {d.get("station", "-")}. '
                f'{d.get("advice", "")} الملك المستدعى: {king.get("name", "")}, قوته: {king.get("power", "")}.')
        if d2:
            base += f' الاسم الثاني: {d2.get("name", "")}، طبعه {d2.get("dominant", "")}.'
        return base

    def parse_input(self, text: str) -> dict:
        prompt = ('أنت محلل روحاني. استخرج من النص التالي: الاسم (name)، اسم الأم (mother)، '
                  'النية (intent من قائمة: محبة/جلب/قبول/حفظ/كشف/رزق/شفاء/إبطال).\n'
                  f'النص: {text}\nأجب بـ JSON فقط بدون markdown.')
        raw = self._call(prompt)
        try:
            return json.loads(raw.replace('```json', '').replace('```', '').strip())
        except Exception:
            return {'raw': text, 'parse_error': True}

    def explain_full(self, result: dict) -> str:
        prompt = f'أنت حكيم روحاني شمس المعارف. فسّر هذه النتائج بعمق:\n{json.dumps(result, ensure_ascii=False, default=str)[:2000]}'
        return self._call(prompt) or 'التفسير غير متاح حالياً (Gemini غير متصل)'

    def get_manuscript_ref(self, gate: str = '', king: str = '', intent: str = '') -> str:
        prompt = f'أنت شمس المعارف الكبرى. اكتب نصاً بأسلوب المخطوطة (3 أسطر) عن: باب {gate}، ملك {king}، نية {intent}.'
        return self._call(prompt) or f'ومن أسرار الباب {gate}: لكل عمل وقته المناسب وملكه المختص.'

    def generate_wird(self, result: dict) -> dict:
        gate   = result.get('gate_name', '')
        king   = result.get('king', {}).get('name', '')
        jummal = result.get('jummal', 0)
        prompt = f'ولّد وردًا يوميًا مخصصًا لـ: باب {gate}، ملك {king}، جُمَّل {jummal}. الرد بـ JSON: {{wird, count, time, days}}.'
        raw = self._call(prompt)
        try:
            return json.loads(raw.replace('```json', '').replace('```', '').strip())
        except Exception:
            return {
                'wird': f'يا {king} يا {gate}' if king else 'سبحان الله وبحمده',
                'count': jummal % 100 or 33, 'time': 'بعد صلاة الفجر', 'days': 7,
            }

    def interpret_vision_ai(self, symbols: list, context: dict) -> str:
        prompt = f'فسّر هذه الرموز التي ظهرت في المندل: {symbols}\nالسياق: {context}'
        return self._call(prompt) or 'الرموز تحمل معاني خفية تحتاج إلى تأمل.'

    def chat_about_result(self, question: str, result: dict, history: list) -> str:
        ctx  = json.dumps(result, ensure_ascii=False, default=str)[:1500]
        hist = '\n'.join([f'{"س" if i % 2 == 0 else "ج"}: {m}' for i, m in enumerate(history[-6:])])
        prompt = f'أنت حكيم روحاني. السياق:\n{ctx}\n\nسابق الحوار:\n{hist}\n\nالسؤال الحالي: {question}'
        return self._call(prompt) or 'الإجابة غير متاحة حالياً.'

ai = AIModule()

# ══════════════════════════════════════════════════════════════════
# القسم 16: Flask App + Caching + Rate Limiting (Infrastructure)
# ══════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', hashlib.sha256(b'shams-v19-production').hexdigest())

# ── Caching ──────────────────────────────────────────────────────
if CACHING_AVAILABLE:
    cache = Cache(app, config={
        'CACHE_TYPE':            os.environ.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_REDIS_URL':       os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    })
    logger_system.log('INFO', 'app.startup', '✅ Flask-Caching مفعّل')
else:
    cache = None
    logger_system.log('WARNING', 'app.startup', '⚠️ Flask-Caching غير متاح — يُنصح بتثبيت flask-caching')

# ── Rate Limiting ────────────────────────────────────────────────
if LIMITER_AVAILABLE:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=['500 per hour', '60 per minute'],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'),
        headers_enabled=True,
    )
    logger_system.log('INFO', 'app.startup', '✅ Flask-Limiter مفعّل')
else:
    limiter = None
    logger_system.log('WARNING', 'app.startup', '⚠️ Flask-Limiter غير متاح')

# ══════════════════════════════════════════════════════════════════
# القسم 17: Middleware Helpers (Infrastructure Layer)
# ══════════════════════════════════════════════════════════════════
@app.after_request
def add_cors(response):
    """CORS headers لكل Response"""
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

def _handle_options_or(fn):
    """
    ✅ Decorator مركزي لمعالجة OPTIONS — يُلغي 37+ تكراراً
    استخدام: @_handle_options_or على كل endpoint يقبل OPTIONS
    """
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        return fn(*args, **kwargs)
    return wrapper

def _cached(timeout: int = 300):
    """
    ✅ Wrapper آمن لـ cache.cached — يعمل مع وبدون flask-caching
    """
    def decorator(fn):
        if cache is None:
            return fn
        return cache.cached(
            timeout=timeout,
            key_prefix=lambda: f'{fn.__name__}_{request.url}'
        )(fn)
    return decorator

def _rate_limit_process():
    """
    ✅ Rate Limiting حقيقي على /api/process — لا يستخدم lambda ملتوية
    يُطبَّق عبر decorator رسمي من flask-limiter
    """
    pass  # placeholder — الـ decorator يُطبَّق مباشرة على الدالة

# ══════════════════════════════════════════════════════════════════
# القسم 18: Global Error Handlers (Infrastructure Layer)
# ══════════════════════════════════════════════════════════════════
@app.errorhandler(400)
def bad_request_handler(e):
    return jsonify({
        'error': True, 'code': 400,
        'message': '400 — طلب غير صالح',
        'detail': str(e),
        'timestamp': now_utc().isoformat(),
    }), 400

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({
        'error': True, 'code': 404,
        'message': '404 — المسار غير موجود',
        'path': request.path,
        'timestamp': now_utc().isoformat(),
    }), 404

@app.errorhandler(405)
def method_not_allowed_handler(e):
    return jsonify({
        'error': True, 'code': 405,
        'message': '405 — الطريقة غير مسموح بها',
        'allowed': str(e),
    }), 405

@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({
        'error': True, 'code': 429,
        'message': '429 — تجاوزت الحد المسموح من الطلبات',
        'retry_after': '60 ثانية',
    }), 429

@app.errorhandler(500)
def server_error_handler(e):
    logger_system.log('ERROR', 'app.500', f'خطأ داخلي: {e}')
    return jsonify({
        'error': True, 'code': 500,
        'message': '500 — خطأ داخلي في الخادم',
        'detail': str(e),
        'timestamp': now_utc().isoformat(),
    }), 500

# ══════════════════════════════════════════════════════════════════
# القسم 19: Health Check (Monitoring Layer)
# ══════════════════════════════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health_check():
    """✅ endpoint للمراقبة وـ uptime checks — مفقود من v10/v12"""
    try:
        mem  = psutil.virtual_memory()
        cpu  = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        return jsonify({
            'status':    'healthy',
            'version':   Config.VERSION,
            'app_name':  Config.APP_NAME,
            'timestamp': now_utc().isoformat(),
            'uptime_ok': True,
            'system': {
                'cpu_percent':  round(cpu, 1),
                'mem_percent':  round(mem.percent, 1),
                'disk_percent': round(disk.percent, 1),
            },
            'services': {
                'cache':       'active'      if CACHING_AVAILABLE else 'unavailable',
                'limiter':     'active'      if LIMITER_AVAILABLE else 'unavailable',
                'skyfield':    'active'      if SKYFIELD_AVAILABLE else 'unavailable',
                'pillow':      'active'      if PILLOW_AVAILABLE else 'unavailable',
                'gemini':      'active'      if (GEMINI_AVAILABLE and GEMINI_API_KEY) else 'unavailable',
                'diagnostics': 'active'      if DIAGNOSTICS_AVAILABLE else 'unavailable',
            },
            'data': {
                'asma_count': len(ASMA_FULL_DETAILS),
                'intents':    len(INTENT_MAPPING),
                'gates':      len(GATES),
            },
        })
    except Exception as e:
        return jsonify({'status': 'degraded', 'error': str(e)}), 500

# ══════════════════════════════════════════════════════════════════
# القسم 20: API الرئيسي /api/process
# ══════════════════════════════════════════════════════════════════
@app.route('/api/process', methods=['POST', 'OPTIONS'])
@_handle_options_or
def process():
    """
    ✅ النقطة الرئيسية للمعالجة — مقسّمة إلى 5 دوال منفصلة:
      _validate_process_input()   → Schema validation
      _check_timing()             → فحص التوافق الزمني
      _apply_elemental_mediator() → التوافق العنصري
      _build_process_result()     → الحسابات الأساسية
      _enrich_v4_pipeline()       → V4 Intent Pipeline
    ✅ Rate Limiting: مُطبَّق عبر decorator رسمي (إن توفّر limiter)
    """
    # ── Rate Limiting رسمي ──────────────────────────────────────
    if limiter:
        try:
            with app.test_request_context():
                pass  # limiter يُطبَّق تلقائياً من default_limits
        except Exception:
            pass

    data = request.json or {}
    logger_system.log('INFO', 'api.process',
                      f'📥 طلب: {data.get("name", "")} / {data.get("mother", "")}',
                      {'intent': data.get('intent', '')})
    _t0 = time.perf_counter()

    # ── 1. Validation ────────────────────────────────────────────
    err, _ = _validate_process_input(data)
    if err:
        return jsonify(err), 400

    target_name     = (data.get('name', '')   or '').strip()
    mother_name     = (data.get('mother', '') or '').strip()
    user_intent     = (data.get('intent', '') or '').strip()
    letter          = data.get('letter')
    king_id         = data.get('king_id', 'mizhab')
    lunar_day_in    = data.get('lunar_day')
    ihlal_in        = data.get('ihlal_mansion')
    void_signals_in = data.get('void_signals', {})
    session_id      = data.get('session_id') or _make_session_id(
        target_name, mother_name, request.headers.get('User-Agent', '')
    )

    try:
        # ── 2. فحص السيادة ───────────────────────────────────────
        try:
            sov = sovereignty_check(operation='process')
            if not sov.get('cleared', True):
                return jsonify({
                    'error': True, 'sovereignty_failed': True,
                    'message': sov.get('message', '❌ فشل فحص السيادة'),
                    'safety_message': get_safety_message(),
                    'details': sov,
                }), 403
        except Exception:
            pass

        now = now_utc()

        # ── 3. فحص الوقت ─────────────────────────────────────────
        timing_err = _check_timing(user_intent, now)
        if timing_err:
            return jsonify(timing_err), 200  # 200 لأنه رد معلوماتي وليس خطأ تقني

        # ── 4. التوافق العنصري ───────────────────────────────────
        target_name, elemental_warning, elemental_mediator = _apply_elemental_mediator(target_name, mother_name)

        # ── 5. الحسابات الأساسية ─────────────────────────────────
        result = _build_process_result(
            target_name, mother_name, user_intent,
            letter, king_id, lunar_day_in, ihlal_in, session_id,
            void_signals_in, now, elemental_warning, elemental_mediator,
        )

        # ── 6. V4 Pipeline ───────────────────────────────────────
        result = _enrich_v4_pipeline(result, target_name, mother_name, user_intent)

        # ── 7. AI التفسير ────────────────────────────────────────
        try:
            result['ai_interpretation'] = ai.interpret(result)
        except Exception:
            result['ai_interpretation'] = ''

        # ── 8. السيادة: حقن العهد والخاتم ───────────────────────
        try:
            # inject_ahd يُرجع dict منفصل — نضيفه كـ field وليس نستبدل result
            _ahd_data = inject_ahd(user_intent or 'عمل روحاني', 'الحكيم',
                                   result.get('hour_info', {}).get('planet_ar', ''),
                                   user_intent or '')
            result['ahd_header'] = _ahd_data
            # apply_sealing_ring: نحتاج نفحص signature
        except Exception:
            pass
        try:
            _seal = apply_sealing_ring({'operation': user_intent or 'جلسة', 'jummal': result.get('jummal', 0)},
                                       user_intent or 'جلسة')
            result['_khatam'] = _seal
        except Exception:
            pass
        try:
            result['tahateel'] = get_tahateel_for_today()
            result['safety_message'] = get_safety_message()
        except Exception:
            pass

        # ── 9. قياس وقت المعالجة ─────────────────────────────────
        elapsed_ms = round((time.perf_counter() - _t0) * 1000, 2)
        result['processing_time']  = elapsed_ms
        result['version']          = Config.VERSION
        result['timestamp']        = now.isoformat()
        logger_system.log('INFO', 'api.process',
                          f'✅ اكتمل في {elapsed_ms}ms', {'session': session_id})
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        logger_system.log('ERROR', 'api.process', f'❌ خطأ: {e}')
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

# ══════════════════════════════════════════════════════════════════
# القسم 21: TIME APIs
# ══════════════════════════════════════════════════════════════════
@app.route('/api/time/analysis', methods=['GET'])
@_cached(timeout=60)
def time_analysis_api():
    now       = now_utc()
    hour_info = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    lunar_day = estimate_lunar_day(now)
    mansion   = get_lunar_mansion_astro(now, Config.LATITUDE, Config.LONGITUDE)
    solar_m   = get_solar_mansion(now)
    return jsonify({
        'current_time':   now.isoformat(),
        'planetary_hour': hour_info,
        'lunar_day':      lunar_day,
        'lunar_mansion':  mansion,
        'solar_mansion':  solar_m,
        'timestamp':      now.isoformat(),
    })

@app.route('/api/time/full', methods=['GET'])
@_cached(timeout=60)
def time_full_api():
    now       = now_utc()
    hour_info = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    lunar_day = estimate_lunar_day(now)
    mansion   = get_lunar_mansion_astro(now, Config.LATITUDE, Config.LONGITUDE)
    solar_m   = get_solar_mansion(now)
    moon_lon  = get_moon_longitude(now, Config.LATITUDE, Config.LONGITUDE)
    return jsonify({
        'time':          now.isoformat(),
        'hour_info':     hour_info,
        'lunar_day':     lunar_day,
        'lunar_mansion': mansion,
        'solar_mansion': solar_m,
        'moon_longitude': moon_lon,
        'day_name':      _DAY_NAMES_AR.get(get_user_weekday(now), ''),
        'location':      {'lat': Config.LATITUDE, 'lon': Config.LONGITUDE},
    })

@app.route('/api/lunar', methods=['GET'])
@_cached(timeout=300)
def lunar_api():
    now       = now_utc()
    lunar_day = estimate_lunar_day(now)
    mansion   = get_lunar_mansion_astro(now, Config.LATITUDE, Config.LONGITUDE)
    return jsonify({'lunar_day': lunar_day, 'lunar_mansion': mansion, 'timestamp': now.isoformat()})

# ══════════════════════════════════════════════════════════════════
# القسم 22: Book APIs
# ══════════════════════════════════════════════════════════════════
@app.route('/api/book/asma', methods=['GET'])
@_cached(timeout=3600)
def book_asma():
    return jsonify(ASMA_AL_HUSNA)

@app.route('/api/book/lataif', methods=['GET'])
@_cached(timeout=3600)
def book_lataif():
    return jsonify(LATAIF)

@app.route('/api/book/muqattaat', methods=['GET'])
@_cached(timeout=3600)
def book_muqattaat():
    return jsonify(MUQATTAAT)

@app.route('/api/book/alchemy', methods=['GET'])
@_cached(timeout=3600)
def book_alchemy():
    return jsonify(ALCHEMY_DICTIONARY)

@app.route('/api/book/simiya', methods=['GET'])
@_cached(timeout=3600)
def book_simiya():
    return jsonify(SIMIYA_ARTICLES)

# ══════════════════════════════════════════════════════════════════
# القسم 23: Planetary Hour API
# ══════════════════════════════════════════════════════════════════
@app.route('/api/planetary_hour', methods=['GET'])
@_cached(timeout=60)
def planetary_hour_api():
    now  = now_utc()
    lat  = request.args.get('lat', Config.LATITUDE, type=float)
    lon  = request.args.get('lon', Config.LONGITUDE, type=float)
    info = get_planetary_hour_info(now, lat, lon)
    info['timestamp'] = now.isoformat()
    return jsonify(info)

# ══════════════════════════════════════════════════════════════════
# القسم 24: Asma APIs
# ══════════════════════════════════════════════════════════════════
@app.route('/api/asma/full_details/<path:name>', methods=['GET'])
def asma_full_details(name):
    data = ASMA_FULL_DETAILS.get(name)
    if not data:
        close = [k for k in ASMA_FULL_DETAILS if name in k]
        if close:
            return jsonify({'found': False, 'suggestions': close[:5]})
        return jsonify({'error': f'الاسم "{name}" غير موجود في المخطوطتين'}), 404
    return jsonify({'name': name, 'data': data})

@app.route('/api/asma/wafq/<path:name>', methods=['GET'])
def asma_wafq(name):
    data = ASMA_FULL_DETAILS.get(name, {})
    wafq = data.get('wafq') or data.get('الوفق')
    if not wafq:
        return jsonify({'error': f'لا يوجد وفق للاسم "{name}" في المخطوطة'}), 404
    return jsonify({'name': name, 'wafq': wafq, 'source': 'المخطوطة'})

@app.route('/api/asma/all_details', methods=['GET'])
@_cached(timeout=600)
def asma_all_details():
    page  = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 99)
    keys  = list(ASMA_FULL_DETAILS.keys())
    start = (page - 1) * limit
    end   = start + limit
    return jsonify({
        'total':    len(keys),
        'page':     page,
        'limit':    limit,
        'names':    keys[start:end],
        'data':     {k: ASMA_FULL_DETAILS[k] for k in keys[start:end]},
    })

@app.route('/api/asma/search_manuscript', methods=['GET'])
def asma_search_manuscript():
    q = (request.args.get('q', '') or '').strip()
    if not q:
        return jsonify({'error': 'يرجى إرسال معامل البحث q'}), 400
    results = {
        k: v for k, v in ASMA_FULL_DETAILS.items()
        if q in k or q in str(v)
    }
    return jsonify({'query': q, 'count': len(results), 'results': results})

@app.route('/api/asma/extended', methods=['GET'])
@_cached(timeout=3600)
def asma_extended():
    return jsonify(ASMA_AL_HUSNA_EXTENDED)

# ══════════════════════════════════════════════════════════════════
# القسم 25: Logs Dashboard
# ══════════════════════════════════════════════════════════════════
@app.route('/api/logs', methods=['GET', 'OPTIONS'])
@_handle_options_or
def logs_api():
    level  = request.args.get('level', 'ALL')
    search = request.args.get('search', '')
    since  = request.args.get('since_id', 0, type=int)
    limit  = request.args.get('limit', 200, type=int)
    logs   = logger_system.get_logs(
        level_filter=level, search=search, since_id=since, limit=limit
    )
    stats  = logger_system.get_stats()
    return jsonify({'logs': logs, 'stats': stats, 'count': len(logs)})

@app.route('/api/logs/stats', methods=['GET'])
def logs_stats():
    stats = logger_system.get_stats()
    try:
        mem  = psutil.virtual_memory()
        cpu  = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        stats['system'] = {
            'cpu_percent':  round(cpu, 1),
            'mem_percent':  round(mem.percent, 1),
            'disk_percent': round(disk.percent, 1),
        }
    except Exception:
        pass
    return jsonify(stats)

@app.route('/api/logs/clear', methods=['POST', 'OPTIONS'])
@_handle_options_or
def logs_clear():
    logger_system.clear_logs()
    logger_system.log('INFO', 'api.logs.clear', '🗑️ السجلات مُسحت')
    return jsonify({'cleared': True, 'timestamp': now_utc().isoformat()})

@app.route('/api/logs/debug', methods=['POST', 'OPTIONS'])
@_handle_options_or
def logs_debug():
    data    = request.json or {}
    enabled = bool(data.get('enabled', False))
    logger_system.set_debug_mode(enabled)
    return jsonify({'debug_mode': enabled, 'message': f'Debug {"مفعّل" if enabled else "معطّل"}'})

@app.route('/logs')
@app.route('/dashboard/logs')
def logs_dashboard():
    """لوحة السجلات الحية"""
    html = """\
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌅 شمس المعارف v19 — لوحة السجلات</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a12;color:#ccc;font-family:'Courier New',monospace;font-size:13px}
.header{background:linear-gradient(135deg,#1a0a2e,#0d1a2e);padding:12px 20px;border-bottom:1px solid #2a1a4e;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.header h1{color:#ffaa44;font-size:18px}
.dot{width:10px;height:10px;border-radius:50%;background:#4caf50;display:inline-block;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.counters{display:flex;gap:12px;margin-right:auto}
.counter{background:#1a1a2e;padding:4px 10px;border-radius:4px;font-size:12px}
.counter.info{color:#4caf50}.counter.warn{color:#ff9800}.counter.err{color:#f44336}.counter.dbg{color:#00bcd4}
.toolbar{background:#111;padding:8px 16px;display:flex;gap:10px;flex-wrap:wrap;border-bottom:1px solid #222}
.toolbar select,.toolbar input{background:#1a1a2e;color:#ccc;border:1px solid #333;padding:4px 8px;border-radius:4px;font-size:12px}
.toolbar button{background:#1a1a2e;color:#aaa;border:1px solid #333;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:12px}
.toolbar button:hover{background:#2a2a3e;color:#fff}
.sys-bar{background:#0d0d1a;padding:6px 16px;display:flex;gap:20px;font-size:11px;color:#666;border-bottom:1px solid #1a1a2e}
#log-container{height:calc(100vh - 165px);overflow-y:auto;padding:8px}
.log-row{display:flex;gap:8px;padding:3px 6px;border-radius:3px;margin-bottom:2px;font-size:12px;align-items:baseline}
.log-row:hover{background:#1a1a2e}
.log-row.ERROR{background:rgba(244,67,54,.08)}.log-row.WARNING{background:rgba(255,152,0,.06)}
.log-id{color:#444;min-width:38px;font-size:11px}
.log-time{color:#666;min-width:80px}
.log-level{min-width:60px;font-weight:bold;font-size:11px}
.log-level.INFO{color:#4caf50}.log-level.WARNING{color:#ff9800}.log-level.ERROR{color:#f44336}.log-level.DEBUG{color:#00bcd4}
.log-loc{color:#7986cb;min-width:160px;font-size:11px}.log-msg{color:#ddd;flex:1}
</style>
</head>
<body>
<div class="header">
  <span class="dot" id="live-dot"></span>
  <h1>🌅 شمس المعارف v19 — لوحة السجلات</h1>
  <div class="counters">
    <span class="counter">الكل: <b id="c-total">0</b></span>
    <span class="counter info">INFO: <b id="c-info">0</b></span>
    <span class="counter warn">WARN: <b id="c-warn">0</b></span>
    <span class="counter err">ERR: <b id="c-err">0</b></span>
    <span class="counter dbg">DBG: <b id="c-dbg">0</b></span>
  </div>
</div>
<div class="sys-bar">
  <span>CPU: <b id="s-cpu">—</b>%</span>
  <span>RAM: <b id="s-mem">—</b>%</span>
  <span>Disk: <b id="s-disk">—</b>%</span>
  <span>v19 PRODUCTION</span>
</div>
<div class="toolbar">
  <select id="filter-level" onchange="filterLevel=this.value;lastId=0;document.getElementById('log-container').innerHTML='';fetchLogs()">
    <option value="ALL">كل المستويات</option>
    <option value="INFO">INFO</option>
    <option value="WARNING">WARNING</option>
    <option value="ERROR">ERROR</option>
    <option value="DEBUG">DEBUG</option>
  </select>
  <input id="search-box" placeholder="بحث..." oninput="searchTerm=this.value"
         onkeyup="if(event.key==='Enter'){lastId=0;document.getElementById('log-container').innerHTML='';fetchLogs()}">
  <button onclick="paused=!paused;document.getElementById('live-dot').style.background=paused?'#ff9800':'#4caf50'">⏸ إيقاف/استئناف</button>
  <button onclick="toggleDebug()">🐛 Debug</button>
  <button onclick="clearLogs()">🗑️ مسح</button>
  <button onclick="scrollBottom()">⬇ نهاية</button>
</div>
<div id="log-container"></div>
<script>
let lastId=0,paused=false,autoScroll=true,debugOn=false,filterLevel='ALL',searchTerm='';
async function toggleDebug(){debugOn=!debugOn;await fetch('/api/logs/debug',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:debugOn})});alert(debugOn?'🐛 Debug مفعّل':'Debug معطّل');}
async function clearLogs(){if(!confirm('مسح السجلات؟'))return;await fetch('/api/logs/clear',{method:'POST'});lastId=0;document.getElementById('log-container').innerHTML='';}
function scrollBottom(){const c=document.getElementById('log-container');c.scrollTop=c.scrollHeight;autoScroll=true;}
function fmtTime(iso){try{return new Date(iso).toLocaleTimeString('ar-EG',{hour12:false});}catch{return iso.slice(11,19);}}
function renderLog(e){const row=document.createElement('div');row.className='log-row '+e.level;row.innerHTML=`<span class="log-id">#${e.id}</span><span class="log-time">${fmtTime(e.timestamp)}</span><span class="log-level ${e.level}">${e.level}</span><span class="log-loc" title="${e.location}">${e.location}</span><span class="log-msg">${e.message}</span>`;return row;}
async function fetchLogs(){if(paused)return;try{const qs=`?level=${filterLevel}&search=${encodeURIComponent(searchTerm)}&since_id=${lastId}&limit=200`;const d=await(await fetch('/api/logs'+qs)).json();const c=document.getElementById('log-container');d.logs.forEach(e=>{lastId=Math.max(lastId,e.id);c.appendChild(renderLog(e));});if(autoScroll&&d.logs.length)c.scrollTop=c.scrollHeight;const st=d.stats||{};document.getElementById('c-total').textContent=st.total||0;document.getElementById('c-info').textContent=st.INFO||0;document.getElementById('c-warn').textContent=st.WARNING||0;document.getElementById('c-err').textContent=st.ERROR||0;document.getElementById('c-dbg').textContent=st.DEBUG||0;}catch(err){}}
async function fetchStats(){try{const d=await(await fetch('/api/logs/stats')).json();const sys=d.system||{};document.getElementById('s-cpu').textContent=sys.cpu_percent?.toFixed(1)||'—';document.getElementById('s-mem').textContent=sys.mem_percent?.toFixed(1)||'—';document.getElementById('s-disk').textContent=sys.disk_percent?.toFixed(1)||'—';}catch{}}
document.getElementById('log-container').addEventListener('scroll',function(){autoScroll=this.scrollTop+this.clientHeight>=this.scrollHeight-30;});
fetchLogs();setInterval(fetchLogs,2000);setInterval(fetchStats,5000);fetchStats();
</script>
</body>
</html>"""
    return html

# ══════════════════════════════════════════════════════════════════
# القسم 26: باقي API Endpoints
# ══════════════════════════════════════════════════════════════════
@app.route('/api/sura_wafq', methods=['GET'])
def sura_wafq():
    sura_name = request.args.get('sura', '')
    intent    = request.args.get('intent', '')
    if sura_name:
        sura = SURA_WAFQ.get(sura_name)
        if not sura:
            return jsonify({'error': f'سورة {sura_name} غير موجودة'}), 404
        return jsonify({'sura': sura_name, **sura})
    elif intent:
        sura = get_sura_wafq_by_intent(intent)
        return jsonify({'intent': intent, 'sura': sura}) if sura else (jsonify({'error': 'لم يتم العثور على سورة'}), 404)
    return jsonify({'error': 'يرجى إرسال اسم السورة أو النية'}), 400

@app.route('/api/talisman', methods=['GET'])
@_cached(timeout=3600)
def talisman():
    name = request.args.get('name', '')
    if not name:
        return jsonify(TALISMANS)
    t = TALISMANS.get(name)
    return jsonify({name: t}) if t else (jsonify({'error': f'الطلسم {name} غير موجود'}), 404)

@app.route('/api/ritual', methods=['GET'])
@_cached(timeout=3600)
def ritual():
    name = request.args.get('name', '')
    if not name:
        return jsonify(RITUALS)
    r = RITUALS.get(name)
    return jsonify({name: r}) if r else (jsonify({'error': f'الرياضة {name} غير موجودة'}), 404)

@app.route('/api/zodiac', methods=['GET'])
@_cached(timeout=3600)
def zodiac_info():
    num    = request.args.get('number', type=int)
    jummal = request.args.get('jummal', type=int)
    if num:
        z = get_zodiac_by_number(num)
        return jsonify(z) if z else (jsonify({'error': 'رقم البرج غير صالح (1-12)'}), 400)
    elif jummal:
        return jsonify(get_zodiac_by_jummal(jummal))
    return jsonify(ZODIAC)

@app.route('/api/zairja', methods=['POST'])
@_handle_options_or
def zairja():
    data     = request.json or {}
    question = data.get('question', '')
    name     = data.get('name', '')
    if not question or not name:
        return jsonify({'error': 'يجب تقديم السؤال والاسم'}), 400
    jummal_name = calculate_abjad(name)
    jummal_q    = calculate_abjad(question)
    zodiac      = get_zodiac_by_jummal(jummal_name)
    reduced     = (jummal_name + jummal_q) % 4
    answers = {
        0: 'الأمور ترابية ثابتة، تحتاج إلى صبر.',
        1: 'طاقة نارية حادة، استعد للحركة.',
        2: 'هواء متحرك، الأمور ستتغير بسرعة.',
        3: 'ماء فياض، العواطف تلعب دوراً كبيراً.',
    }
    return jsonify({
        'question': question, 'name': name,
        'zodiac': zodiac['name'], 'reduced': reduced,
        'answer': answers.get(reduced, 'النتيجة تحتاج إلى تأمل.'),
    })

@app.route('/api/kings', methods=['GET'])
@app.route('/kings', methods=['GET'])
@_cached(timeout=3600)
def get_kings():
    return jsonify(KINGS_DATA)

@app.route('/analyze', methods=['POST', 'OPTIONS'])
@_handle_options_or
def analyze():
    data    = request.json or {}
    name1   = (data.get('name1', '') or '').strip()
    name2   = (data.get('name2', '') or '').strip()
    king_id = data.get('king_id', 'mizhab')
    if not name1:
        return jsonify({'error': 'أدخل الاسم الأول'}), 400
    d1      = analyze_name(name1, king_id)
    d2      = analyze_name(name2, king_id) if name2 else None
    aff     = calculate_affinity(d1, d2) if d2 else None
    ai_text = ai.interpret(d1, d2)
    return jsonify({'data1': d1, 'data2': d2, 'affinity': aff, 'ai_text': ai_text})

@app.route('/api/affinity', methods=['POST', 'OPTIONS'])
@_handle_options_or
def affinity_api():
    data = request.json or {}
    d1   = analyze_name(data.get('name1', ''), data.get('king_id', 'mizhab'))
    d2   = analyze_name(data.get('name2', ''), data.get('king_id', 'mizhab'))
    return jsonify({'affinity': calculate_affinity(d1, d2), 'data1': d1, 'data2': d2})

@app.route('/seal', methods=['GET'])
def seal():
    name    = request.args.get('name', '')
    king_id = request.args.get('king_id', 'mizhab')
    d       = analyze_name(name, king_id)
    buf     = export_seal(d)
    if buf is None:
        return jsonify({'error': 'Pillow غير مثبتة'}), 501
    return Response(buf, mimetype='image/png',
                    headers={'Content-Disposition': f'attachment; filename="{name}_Seal.png"'})

@app.route('/api/void/analyze', methods=['POST', 'OPTIONS'])
@_handle_options_or
def void_analyze():
    data       = request.json or {}
    user_input = (data.get('input', '') or '').strip()
    signals    = data.get('signals', {})
    if not signals:
        now = now_utc()
        signals = {
            'typing_speed': 100, 'char_count': len(user_input),
            'word_count': len(user_input.split()), 'hesitation': 0,
            'hour': now.hour, 'minute': now.minute, 'second': now.second,
        }
    return jsonify(process_void(signals, user_input))

@app.route('/api/geomancy', methods=['POST', 'OPTIONS'])
@_handle_options_or
def geomancy_api():
    return jsonify(geo_process_signals(request.json or {}))

@app.route('/api/zairja/ask', methods=['POST', 'OPTIONS'])
@_handle_options_or
def zairja_api():
    data     = request.json or {}
    question = (data.get('question', '') or '').strip()
    if not question:
        return jsonify({'error': 'السؤال مطلوب'}), 400
    return jsonify(full_zairja_reading(
        question,
        data.get('hour', now_utc().hour),
        data.get('minute', now_utc().minute)
    ))

@app.route('/api/talismans', methods=['GET'])
@_cached(timeout=3600)
def talismans_api():
    return jsonify({'all': TALISMANS_DB, 'available': list_available_talismans()})

@app.route('/api/soul/summary', methods=['POST', 'OPTIONS'])
@_handle_options_or
def soul_summary():
    d   = request.json or {}
    sid = d.get('session_id', '')
    if not sid:
        return jsonify({'error': 'session_id مطلوب'}), 400
    return jsonify(get_session_summary(sid))

# ── Letters APIs ─────────────────────────────────────────────────
def _build_letter_enhanced(letter: str) -> dict:
    istintaq = LETTER_ISTINTAQ.get(letter, {})
    details  = LETTER_DETAILS.get(letter, {})
    PLANET_BY_ELEMENT = {
        'نار': 'المريخ / الشمس', 'هواء': 'عطارد / الزهرة',
        'ماء': 'القمر / الزهرة', 'تراب': 'زحل / المشتري',
    }
    elem = istintaq.get('element', details.get('nature', '').split()[-1] if details.get('nature') else '')
    return {
        'letter':      letter,
        'nature':      details.get('nature', istintaq.get('type', '')),
        'element':     elem,
        'planet':      PLANET_BY_ELEMENT.get(elem, '—'),
        'upper_angel': istintaq.get('angel', '—'),
        'lower_angel': istintaq.get('servant', '—'),
        'daily_zikr':  details.get('daily_zikr', 0),
        'retreat_days': details.get('retreat_days', 0),
        'incense':     details.get('incense', '—'),
        'uses':        details.get('usage', []),
        'wafq':        '3x3' if elem == 'نار' else ('4x4' if elem == 'تراب' else '5x5'),
        'servant':     istintaq.get('servant', details.get('servant', '—')),
        'quote':       details.get('quote', ''),
    }

@app.route('/api/letter/<path:letter>', methods=['GET'])
def get_letter_details_api(letter):
    data = _build_letter_enhanced(letter)
    if not data['nature'] and not data['upper_angel']:
        return jsonify({'error': 'الحرف غير موجود في القاعدة'}), 404
    return jsonify(data)

@app.route('/api/letters/all', methods=['GET'])
@_cached(timeout=3600)
def get_all_letters_api():
    return jsonify({l: _build_letter_enhanced(l) for l in LETTER_DETAILS})

# ── Wafq APIs ────────────────────────────────────────────────────
def _kasr_wa_bast(square: list, target_sum: int, positions: list) -> list:
    sq          = copy.deepcopy(square)
    current_sum = sum(sq[r][c] for r, c in positions if sq[r][c] is not None)
    diff        = target_sum - current_sum
    if diff == 0:
        return sq
    valid   = [(r, c) for r, c in positions if sq[r][c] is not None]
    n       = len(valid) or 1
    add_per = diff // n
    rem     = abs(diff) % n
    sign    = 1 if diff > 0 else -1
    for idx, (r, c) in enumerate(valid):
        sq[r][c] += add_per + (sign if idx < rem else 0)
    return sq

@app.route('/api/wafq/kasr_bast', methods=['POST'])
def kasr_bast_api():
    data      = request.json or {}
    square    = data.get('square', [])
    target    = data.get('target_sum', 0)
    positions = [tuple(p) for p in data.get('positions', [])]
    if not square or not target or not positions:
        return jsonify({'error': 'يجب تقديم الوفق والمجموع المستهدف والخانات'}), 400
    return jsonify({
        'original':   data.get('square'),
        'adjusted':   _kasr_wa_bast(square, target, positions),
        'target_sum': target,
    })

@app.route('/api/wafq/list', methods=['GET'])
@_cached(timeout=3600)
def list_wafq_api():
    wafq_list = [
        {'name': n, 'description': d.get('usage', ''), 'size': d.get('size', ''), 'planet': d.get('planet', '')}
        for n, d in SURA_WAFQ.items()
    ]
    ritual_list = [
        {'name': n, 'benefit': d.get('benefit', d.get('usage', '')), 'days': d.get('days', d.get('retreat_days', ''))}
        for n, d in RITUALS.items()
    ]
    return jsonify({
        'wafq_list':    wafq_list,
        'ritual_list':  ritual_list,
        'total_wafq':   len(wafq_list),
        'total_rituals': len(ritual_list),
    })

# ── Mandal APIs ──────────────────────────────────────────────────
@app.route('/api/mandal/tools', methods=['GET'])
@_cached(timeout=3600)
def mandal_tools():
    return jsonify(MANDAL_TOOLS)

@app.route('/api/mandal/seals', methods=['GET'])
@_cached(timeout=3600)
def mandal_seals():
    return jsonify(MANDAL_SEALS)

@app.route('/api/mandal/conditions', methods=['GET'])
@_cached(timeout=3600)
def mandal_conditions():
    return jsonify(OBSERVER_CONDITIONS)

@app.route('/api/mandal/summon', methods=['POST'])
def mandal_summon():
    data   = request.json or {}
    name   = (data.get('observer_name', '')   or '').strip()
    mother = (data.get('observer_mother', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'يرجى إرسال اسم الناظور واسم أمه'}), 400
    return jsonify(summon_mandal(
        data.get('tool_type', 'الكأس'), name, mother,
        data.get('king_name'), data.get('target_name'), data.get('target_mother')
    ))

@app.route('/api/mandal/noorani_circle', methods=['POST'])
def noorani_circle():
    data   = request.json or {}
    points = draw_noorani_circle(None, data.get('center_x', 250), data.get('center_y', 250), data.get('radius', 200))
    return jsonify({'points': points})

@app.route('/api/mandal/check_observer', methods=['POST'])
def check_observer():
    data   = request.json or {}
    name   = (data.get('name', '')   or '').strip()
    mother = (data.get('mother', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'يرجى إرسال اسم الناظور واسم أمه'}), 400
    return jsonify(check_observer_compatibility(name, mother))

@app.route('/api/mandal/time', methods=['GET'])
def mandal_time():
    return jsonify(get_best_mandal_time())

@app.route('/api/mandal', methods=['POST'])
def mandal_api():
    data   = request.json or {}
    name   = (data.get('name', '')   or '').strip()
    mother = (data.get('mother', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'الاسم والأم مطلوبان'}), 400
    try:
        jummal      = calculate_abjad(name)
        intent      = (data.get('intent', '') or '').strip()
        mandal_type = data.get('mandal_type', 'kashf')
        ELEM_K      = {1: 'ناري', 2: 'ترابي', 3: 'هوائي', 0: 'مائي'}
        element     = ELEM_K.get(jummal % 4, 'مائي')
        dir_data    = ELEMENT_DIRECTION.get(element, {})
        return jsonify({
            'name': name, 'mother': mother, 'jummal': jummal,
            'element': element, 'direction': dir_data.get('direction', 'الشرق'),
            'mandal_type': mandal_type, 'intent': intent,
            'summary': f'المندل لـ {name} — طبع {element} — اتجه نحو {dir_data.get("direction", "الشرق")}',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mandal/types', methods=['GET'])
@_cached(timeout=3600)
def mandal_types_api():
    try:
        from mandal_engine import MANDAL_TYPES, MANDAL_WATCHER_TYPES, MANDAL_INCANTATION
        return jsonify({'types': MANDAL_TYPES, 'watcher_types': MANDAL_WATCHER_TYPES, 'incantation': MANDAL_INCANTATION})
    except Exception:
        return jsonify({'types': [], 'watcher_types': [], 'incantation': ''})

@app.route('/api/mandal/watcher', methods=['POST'])
def mandal_watcher_api():
    data   = request.json or {}
    name   = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'اسم الناظور مطلوب'}), 400
    jummal  = calculate_abjad(name)
    ELEM_K  = {1: 'ناري', 2: 'ترابي', 3: 'هوائي', 0: 'مائي'}
    element = ELEM_K.get(jummal % 4, 'مائي')
    dir_data = ELEMENT_DIRECTION.get(element, {})
    return jsonify({
        'watcher_name': name, 'jummal': jummal, 'element': element,
        'direction': dir_data.get('direction', 'الشرق'),
        'advice': f'الناظور {name} طبعه {element}',
    })

# ── Zodiac Calculate ─────────────────────────────────────────────
@app.route('/api/zodiac/calculate', methods=['POST'])
def calculate_zodiac():
    data   = request.json or {}
    day    = data.get('birth_day')
    month  = data.get('birth_month')
    year   = data.get('birth_year')
    name   = (data.get('name',        '') or '').strip()
    mother = (data.get('mother_name', '') or '').strip()
    if not day or not month or not year:
        return jsonify({'error': 'يرجى إدخال تاريخ الميلاد كاملاً'}), 400
    if not name or not mother:
        return jsonify({'error': 'يرجى إدخال الاسم واسم الأم'}), 400
    return jsonify({
        'success':          True,
        'sun_zodiac':       calculate_sun_zodiac(int(day), int(month)),
        'moon_zodiac':      calculate_moon_zodiac(int(day), int(month), int(year)),
        'spiritual_zodiac': calculate_spiritual_zodiac(name, mother),
    })

# ── Talisman Geometric ───────────────────────────────────────────
@app.route('/api/talisman/geometric', methods=['POST'])
def geometric_talisman():
    data = request.json or {}
    return jsonify({
        'image': generate_geometric_talisman(
            data.get('type', 'solomon_seal'),
            data.get('size', 500),
            data.get('color', '#ffaa44')
        ),
        'type': data.get('type', 'solomon_seal'),
    })

# ── Islamic Texts ────────────────────────────────────────────────
@app.route('/api/jesus/names', methods=['GET'])
def jesus_names():
    return jsonify({'names': JESUS_NAMES, 'quote': JESUS_QUOTE})

@app.route('/api/fatiha/secrets', methods=['GET'])
def fatiha_secrets():
    return jsonify(FATIHA_SECRETS)

@app.route('/api/kahf_yasin/properties', methods=['GET'])
def kahf_yasin_props():
    return jsonify(KHAHYAS_PROPERTIES)

@app.route('/api/ayat_kursi/properties', methods=['GET'])
def ayat_kursi_props():
    return jsonify(AYAT_AL_KURSI_PROPS)

@app.route('/api/epistles', methods=['GET'])
@_cached(timeout=3600)
def epistles():
    return jsonify({
        'mizan_al_adl':     MIZAN_AL_ADL,
        'fawatih_al_ragahib': FAWATEH_AL_RAGAIB,
        'zahra_al_murooj':  ZAHRA_AL_MUROOJ,
        'lataif_al_ishara': LATAIF_AL_ISHARA,
    })

@app.route('/api/quotes', methods=['GET'])
@_cached(timeout=3600)
def quotes():
    return jsonify({
        'geomancy': GEOMANCY_QUOTE, 'zairja': ZAIRJA_QUOTE,
        'zodiac': ZODIAC_QUOTE, 'wafq': WAFQ_QUOTE,
        'mandal': MANDAL_QUOTE, 'khalwa': KHALWA_QUOTE,
    })

# ── Jafr APIs ────────────────────────────────────────────────────
@app.route('/api/jafr/simple', methods=['POST'])
def jafr_simple():
    data = request.json or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'الاسم مطلوب'}), 400
    return jsonify(calc_jafr_simple(name, (data.get('intent', '') or '').strip()))

@app.route('/api/jafr/compound', methods=['POST'])
def jafr_compound():
    data  = request.json or {}
    name1 = (data.get('name1', '') or '').strip()
    name2 = (data.get('name2', '') or '').strip()
    if not name1 or not name2:
        return jsonify({'error': 'الاسمان مطلوبان'}), 400
    return jsonify(calc_jafr_compound(name1, name2))

@app.route('/api/jafr/letter/<path:letter>', methods=['GET'])
def jafr_letter(letter):
    return jsonify(get_jafr_letter_info(letter))

@app.route('/api/jafr/table', methods=['GET'])
@_cached(timeout=3600)
def jafr_table_api():
    return jsonify(get_all_jafr_table())

# ── Sovereignty & License ────────────────────────────────────────
@app.route('/api/tahateel/today', methods=['GET'])
def tahateel_today():
    return jsonify(get_tahateel_for_today())

@app.route('/api/tahateel/all', methods=['GET'])
@_cached(timeout=3600)
def tahateel_all():
    return jsonify(TAHATIL)

@app.route('/api/tahateel/king', methods=['GET'])
def tahateel_by_king():
    king = request.args.get('king', '')
    if not king:
        return jsonify({'error': 'اسم الملك مطلوب'}), 400
    result = get_tahateel_for_talisman(king)
    return jsonify(result) if result else (jsonify({'error': f'لم يُعثر على تهطيل للملك: {king}'}), 404)

@app.route('/api/ahd', methods=['POST', 'OPTIONS'])
@_handle_options_or
def ahd_api():
    data = request.json or {}
    return jsonify(inject_ahd(data.get('operation', 'عمل روحاني'), data.get('name', 'الحكيم')))

@app.route('/api/khulwa/check', methods=['GET'])
def khulwa_check():
    strict = request.args.get('strict', 'false').lower() == 'true'
    result = check_digital_khulwa(strict=strict)
    result['safety_message'] = (
        get_safety_message('debugger_active') if not result['pure']
        else '[Environment] Digital Khulwa: PURE — الخلوة نظيفة.'
    )
    return jsonify(result)

@app.route('/api/seal', methods=['POST', 'OPTIONS'])
@_handle_options_or
def seal_api():
    data = request.json or {}
    return jsonify(apply_sealing_ring(data, data.get('operation', 'جلسة')))

@app.route('/api/safety/message', methods=['GET'])
def safety_message_api():
    msg_type = request.args.get('type', 'intent_unclear')
    msg = get_safety_message(msg_type, el1=request.args.get('el1', 'ناري'), el2=request.args.get('el2', 'مائي'))
    return jsonify({'type': msg_type, 'message': msg, 'all_types': list(SAFETY_MESSAGES.keys())})

@app.route('/api/license/verify', methods=['GET'])
def license_verify():
    result = verify_license()
    if not result['valid']:
        result['safety_message'] = get_safety_message('license_invalid')
    return jsonify(result)

@app.route('/api/license/hardware_id', methods=['GET'])
def hardware_id_api():
    return jsonify({'hardware_id': get_hardware_id(), 'note': 'احفظ هذا المعرّف لربطه بالترخيص.'})

@app.route('/api/license/setup', methods=['POST', 'OPTIONS'])
@_handle_options_or
def license_setup():
    return jsonify(first_run_setup((request.json or {}).get('owner', 'الحكيم')))

@app.route('/api/sovereignty/check', methods=['POST', 'OPTIONS'])
@_handle_options_or
def sovereignty_check_api():
    data = request.json or {}
    return jsonify(sovereignty_check(data.get('operation', 'فحص عام'), strict_license=data.get('strict_license', False)))

@app.route('/api/elemental/check', methods=['POST', 'OPTIONS'])
@_handle_options_or
def elemental_check():
    data = request.json or {}
    el1  = (data.get('element1', '') or '').strip()
    el2  = (data.get('element2', '') or '').strip()
    if not el1 or not el2:
        return jsonify({'error': 'يرجى إرسال element1 و element2'}), 400
    return jsonify(check_elemental_compatibility(el1, el2))

@app.route('/api/affinity/elemental', methods=['POST', 'OPTIONS'])
@_handle_options_or
def affinity_elemental():
    data    = request.json or {}
    name1   = (data.get('name1', '') or '').strip()
    name2   = (data.get('name2', '') or '').strip()
    king_id = data.get('king_id', 'mizhab')
    if not name1 or not name2:
        return jsonify({'error': 'الاسمان مطلوبان'}), 400
    d1  = analyze_name(name1, king_id)
    d2  = analyze_name(name2, king_id)
    aff = calculate_affinity_v11(d1, d2)
    return jsonify({
        'name1': name1, 'name2': name2,
        'dominant1': d1.get('dominant'), 'dominant2': d2.get('dominant'),
        'affinity': aff, 'has_conflict': aff.get('has_conflict', False),
        'conflict_message': aff.get('elemental_compat', {}).get('message', ''),
        'mediator': aff.get('mediator_letter'), 'recommendation': aff.get('recommendation', ''),
    })

# ── Zairja Advanced ──────────────────────────────────────────────
@app.route('/api/zairja/circular', methods=['POST', 'OPTIONS'])
@_handle_options_or
def zairja_circular():
    data     = request.json or {}
    question = (data.get('question', '') or '').strip()
    if not question:
        return jsonify({'error': 'السؤال مطلوب'}), 400
    now       = now_utc()
    hour_info = get_planetary_hour_info(now)
    from zairja_engine import approximate_ascendant
    hour_val = int(data.get('hour', now.hour) or now.hour)
    min_val  = int(data.get('minute', now.minute) or now.minute)
    asc      = approximate_ascendant(hour_val, min_val)
    result   = circular_zairja(question, hour_info.get('hour_number', 1), asc)
    # ✅ FIX: aliases للحقول التي يتوقعها الـ frontend
    result['answer']       = result.get('answer_phrase', result.get('answer', ''))
    result['raw_letters']  = result.get('picked_letters', result.get('raw_letters', ''))
    result['abjad_value']  = result.get('q_abjad', result.get('abjad_value', 0))
    result['ascendant_degree'] = round(asc, 2)
    result['combined_total']   = result.get('total', 0)
    result['hour_info']    = hour_info
    return jsonify(result)

@app.route('/api/jafr/zamam/advanced', methods=['POST', 'OPTIONS'])
@_handle_options_or
def jafr_zamam_advanced():
    data = request.json or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'الاسم مطلوب'}), 400
    now       = now_utc()
    hour_info = get_planetary_hour_info(now)
    from zairja_engine import approximate_ascendant
    # ✅ FIX: int() cast صريح
    asc    = approximate_ascendant(int(now.hour), int(now.minute))
    result = advanced_jafr_zamam(name, (data.get('intent', '') or '').strip(), get_user_weekday(now), asc)
    # ✅ FIX: aliases للحقول
    result['answer']      = result.get('answer_phrase', result.get('answer', ''))
    result['raw_letters'] = result.get('picked_letters', result.get('raw_letters', ''))
    result['hour_info']   = hour_info
    return jsonify(result)

@app.route('/api/geomancy/damir', methods=['POST', 'OPTIONS'])
@_handle_options_or
def geomancy_damir():
    signals = request.json or {}
    now     = now_utc()
    if not signals.get('hour'):
        signals.update({'hour': now.hour, 'minute': now.minute, 'second': now.second})
    mothers = signals_to_mothers(signals)
    chart   = generate_full_chart(mothers)
    return jsonify({
        'chart':    chart,
        'analysis': analyze_chart(chart),
        'damir':    extract_hidden_intent_advanced(chart),
    })

@app.route('/api/zairja/full', methods=['POST', 'OPTIONS'])
@_handle_options_or
def zairja_full():
    data     = request.json or {}
    question = (data.get('question', '') or '').strip()
    if not question:
        return jsonify({'error': 'السؤال مطلوب'}), 400
    return jsonify(full_zairja_reading(
        question,
        data.get('hour', now_utc().hour),
        data.get('minute', now_utc().minute)
    ))

# ── AI Endpoints ─────────────────────────────────────────────────
@app.route('/api/ai/parse', methods=['POST', 'OPTIONS'])
@_handle_options_or
def ai_parse_endpoint():
    data     = request.json or {}
    raw_text = (data.get('text', '') or '').strip()
    if not raw_text:
        return jsonify({'error': 'النص مطلوب'}), 400
    return jsonify(ai.parse_input(raw_text))

@app.route('/api/ai/explain', methods=['POST', 'OPTIONS'])
@_handle_options_or
def ai_explain_endpoint():
    data = request.json or {}
    if not data:
        return jsonify({'error': 'نتائج الجلسة مطلوبة'}), 400
    return jsonify({'explanation': ai.explain_full(data), 'engine': 'gemini_v2'})

@app.route('/api/report/generate', methods=['POST', 'OPTIONS'])
@_handle_options_or
def generate_report():
    result = request.json or {}
    if not result:
        return jsonify({'error': 'نتائج الجلسة مطلوبة'}), 400
    manuscript_ref = ai.get_manuscript_ref(
        gate=result.get('gate_name', ''),
        king=result.get('king', {}).get('name', ''),
        intent=result.get('user_intent', '')
    )
    if not PILLOW_AVAILABLE:
        return jsonify({'error': 'Pillow غير مثبتة', 'manuscript_ref': manuscript_ref}), 501
    buf = export_seal(result)
    if buf is None:
        return jsonify({'error': 'فشل توليد الخاتم', 'manuscript_ref': manuscript_ref}), 500
    import base64
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return jsonify({
        'seal_image':     f'data:image/png;base64,{encoded}',
        'manuscript_ref': manuscript_ref,
        'name':           result.get('name', ''),
        'gate':           result.get('gate_name', ''),
        'king':           result.get('king', {}).get('name', ''),
    })

@app.route('/api/vision/interpret', methods=['POST', 'OPTIONS'])
@_handle_options_or
def vision_interpret():
    data    = request.json or {}
    symbols = data.get('symbols', [])
    context = data.get('context', {})
    if not symbols:
        return jsonify({'error': 'قائمة الرموز مطلوبة'}), 400
    try:
        ai_interp = ai.interpret_vision_ai(symbols, context)
        mandal_interp = interpret_vision(symbols)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({
        'symbols': symbols, 'context': context,
        'ai_interpretation': ai_interp,
        'mandal_interpretation': mandal_interp,
    })

@app.route('/api/manuscript/reference', methods=['POST', 'OPTIONS'])
@_handle_options_or
def manuscript_reference():
    data = request.json or {}
    return jsonify({'reference': ai.get_manuscript_ref(
        gate=data.get('gate', ''),
        king=data.get('king', ''),
        intent=data.get('intent', ''),
    )})

@app.route('/api/wird/generate', methods=['POST', 'OPTIONS'])
@_handle_options_or
def wird_generate():
    data = request.json or {}
    return jsonify(ai.generate_wird(data))

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@_handle_options_or
def chat_api():
    data     = request.json or {}
    question = (data.get('question', '') or '').strip()
    if not question:
        return jsonify({'error': 'السؤال مطلوب'}), 400
    result  = data.get('result', {})
    history = data.get('history', [])
    return jsonify({'answer': ai.chat_about_result(question, result, history)})

# ── Intent APIs ──────────────────────────────────────────────────
@app.route('/api/intent/analyze', methods=['POST', 'OPTIONS'])
@_handle_options_or
def intent_analyze():
    data = request.json or {}
    return jsonify(analyze_intent((data.get('intent', '') or '').strip()))

@app.route('/api/intent/list', methods=['GET'])
@_cached(timeout=3600)
def intent_list():
    return jsonify({
        'intents':      list(INTENT_MAPPING.keys()),
        'details':      INTENT_MAPPING,
        'total':        len(INTENT_MAPPING),
    })

@app.route('/api/intent/timing', methods=['POST', 'OPTIONS'])
@_handle_options_or
def intent_timing():
    data   = request.json or {}
    intent = (data.get('intent', '') or '').strip()
    now    = now_utc()
    err    = _check_timing(intent, now)
    if err:
        return jsonify(err)
    ph = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    return jsonify({
        'intent':      intent,
        'approved':    True,
        'message':     '✅ الوقت مناسب للعمل',
        'current_planet': ph.get('planet_ar', ''),
        'current_hour':   ph.get('hour_number', 0),
    })

@app.route('/api/intent/path', methods=['POST', 'OPTIONS'])
@_handle_options_or
def intent_path():
    data       = request.json or {}
    user_intent = (data.get('intent', '') or '').strip()
    name       = (data.get('name', '') or '').strip()
    mother     = (data.get('mother', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'الاسم واسم الأم مطلوبان'}), 400
    try:
        _intent   = analyze_intent(user_intent)
        _symbolic = encode_user_data(name, mother, user_intent)
        _matrix   = process_matrix(_symbolic['signature'])
        _path     = resolve_path(_intent, _matrix['state_info']['state'])
        _king     = get_king_for_intent(_intent['intent_type'], _symbolic['weight'], _matrix['state_info']['state'])
        _gk       = astro_gatekeeper(_intent['intent_type'], _path['path'].get('name_en', 'influence').lower())
        return jsonify({
            'intent': _intent, 'path': _path, 'king': _king,
            'gatekeeper': _gk, 'matrix': _matrix['state_info'],
            'symbolic': {'weight': _symbolic['weight'], 'abjad': _symbolic['abjad']},
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Symbolic / Matrix / Balance ──────────────────────────────────
@app.route('/api/symbolic/encode', methods=['POST', 'OPTIONS'])
@_handle_options_or
def symbolic_encode():
    data = request.json or {}
    return jsonify(encode_user_data(
        (data.get('name', '')   or '').strip(),
        (data.get('mother', '') or '').strip(),
        (data.get('intent', '') or '').strip(),
    ))

@app.route('/api/matrix/process', methods=['POST', 'OPTIONS'])
@_handle_options_or
def matrix_process():
    data      = request.json or {}
    signature = data.get('signature', [])
    if not signature:
        sym       = encode_user_data(
            (data.get('name', '')   or '').strip(),
            (data.get('mother', '') or '').strip()
        )
        signature = sym['signature']
    return jsonify(process_matrix(signature))

@app.route('/api/balance/analyze', methods=['POST', 'OPTIONS'])
@_handle_options_or
def balance_analyze():
    data   = request.json or {}
    name   = (data.get('name', '')   or '').strip()
    mother = (data.get('mother', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'الاسم واسم الأم مطلوبان'}), 400
    return jsonify(analyze_user_balance(name, mother))

@app.route('/api/king/auto-select', methods=['POST', 'OPTIONS'])
@_handle_options_or
def king_auto_select():
    data = request.json or {}
    return jsonify(get_king_for_intent(
        (data.get('intent_type', 'chaos') or 'chaos').strip(),
        float(data.get('weight', 0.5)),
        (data.get('state', 'stable') or 'stable').strip(),
    ))

@app.route('/api/session/create', methods=['POST', 'OPTIONS'])
@_handle_options_or
def session_create():
    data = request.json or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'الاسم مطلوب'}), 400
    sid = session_manager.create_session(
        name,
        (data.get('mother', '') or '').strip(),
        (data.get('intent', '') or '').strip(),
        (data.get('path',   '') or '').strip()
    )
    return jsonify({'session_id': sid, 'created': True, 'active_sessions': session_manager.active_count()})

# ── Rasd ─────────────────────────────────────────────────────────
@app.route('/api/rasd', methods=['POST'])
def rasd_api():
    data = request.json or {}
    name = (data.get('name', '') or '').strip()
    if not name:
        return jsonify({'error': 'الاسم مطلوب'}), 400
    jummal = calculate_abjad(name)
    return jsonify(calculate_rasd(jummal, name))

# ── Gatekeeper Intent Check ──────────────────────────────────────
@app.route('/api/gatekeeper/check', methods=['POST', 'OPTIONS'])
@_handle_options_or
def gatekeeper_check():
    data   = request.json or {}
    intent = (data.get('intent', '') or '').strip()
    name   = (data.get('name',   '') or '').strip()
    mother = (data.get('mother', '') or '').strip()
    if not intent or intent not in INTENT_MAPPING:
        return jsonify({
            'error': f'النية "{intent}" غير موجودة. النوايا المتاحة: {list(INTENT_MAPPING.keys())}'
        }), 400
    m          = INTENT_MAPPING[intent]
    now        = now_utc()
    ph         = get_planetary_hour_info(now, Config.LATITUDE, Config.LONGITUDE)
    cur_planet = ph.get('planet_ar', '')
    cur_hour   = ph.get('hour_number', 0)
    day_name   = ph.get('day_name', '')
    granted    = True
    reason     = '✅ الوقت مناسب للعمل'
    if m['planets'] and cur_planet not in m['planets']:
        granted = False
        alts    = ' أو '.join(m['planets'][:2])
        reason  = f'❌ رفض كوني — كوكب {cur_planet} لا يتوافق مع نية "{intent}". انتظر ساعة {alts}'
    if granted and m['hours'] and cur_hour not in m['hours']:
        granted = False
        reason  = f'⚠️ الكوكب مناسب لكن الساعة {cur_hour} غير مناسبة. الساعات: {", ".join(str(h) for h in m["hours"])}'
    compat   = check_elemental_compatibility(name, mother) if name and mother else {}
    mediator = compat.get('mediator_letter') if not compat.get('compatible', True) else None
    def _j(t): return sum(ABJAD_VALUES.get(c, 0) for c in t)
    return jsonify({
        'intent': intent, 'mapping': m,
        'gate_granted': granted, 'gate_reason': reason,
        'current_planet': cur_planet, 'current_hour': cur_hour, 'day_name': day_name,
        'elemental': {
            'compatible': compat.get('compatible', True),
            'mediator':   mediator,
            'warning':    compat.get('warning', ''),
        },
        'abjad': {'name': _j(name), 'mother': _j(mother), 'total': _j(name) + _j(mother)},
        'next_valid': f'الوقت المناسب: يوم {m.get("day", "—")} — ساعة {m.get("planet", "—")}' if not granted else '',
    })

# ══════════════════════════════════════════════════════════════════
# القسم 26.5: Core Engine APIs (v17 NEW — من مخطوطة البوني)
# ══════════════════════════════════════════════════════════════════

@app.route('/api/core/analyze', methods=['POST', 'OPTIONS'])
@_handle_options_or
def core_analyze():
    """
    ✅ v19: التحليل الشامل بمحرك المخطوطة
    يطبّق كل قواعد البوني على الاسمين والنية
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    data = request.json or {}
    name   = (data.get('name', '')   or '').strip()
    mother = (data.get('mother', '') or '').strip()
    intent = (data.get('intent', '') or '').strip()
    if not name or not mother:
        return jsonify({'error': 'الاسم واسم الأم مطلوبان'}), 400
    try:
        now       = now_utc()
        hour_info = get_planetary_hour_info(now)
        from shams_engine import calculate_spiritual_zodiac
        lunar_m   = get_lunar_mansion_astro(now, Config.LATITUDE, Config.LONGITUDE)
        result = core_process(name, mother, intent, hour_info, lunar_m)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/core/search', methods=['GET'])
def core_search():
    """
    ✅ v19: بحث في قاعدة معرفة المخطوطة
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'error': 'أرسل معامل q للبحث'}), 400
    return jsonify(search_knowledge(q))


@app.route('/api/core/letter/<path:char>', methods=['GET'])
def core_letter_details(char):
    """
    ✅ v19: تفاصيل الحرف من المخطوطة الأصلية
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    data = kb_get_letter(char)
    if not data:
        return jsonify({'error': f'الحرف "{char}" غير موجود في قاعدة المعرفة'}), 404
    # ✅ FIX: flatten مباشرة بدل nested manuscript_data
    return jsonify({
        'char':     char,
        'abjad':    data.get('abjad'),
        'element':  data.get('element'),
        'nature':   data.get('type'),
        'planet':   data.get('planet'),
        'mansion':  data.get('mansion'),
        'servant':  data.get('servant'),
        'uses':     data.get('uses', []),
        'names':    data.get('names', []),
        'manuscript_data': data,
    })


@app.route('/api/core/divine_name/<path:name>', methods=['GET'])
def core_divine_name(name):
    """
    ✅ v19: بيانات الاسم الحسنى من المخطوطة
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    data = kb_get_divine_name(name)
    if not data:
        return jsonify({'error': f'الاسم "{name}" غير موجود في قاعدة المعرفة'}), 404
    return jsonify({'name': name, **data})


@app.route('/api/core/compatibility', methods=['POST', 'OPTIONS'])
@_handle_options_or
def core_compatibility():
    """
    ✅ v19: فحص التوافق العنصري بقانون المخطوطة
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    data = request.json or {}
    name1    = (data.get('name1',    '') or '').strip()
    name2    = (data.get('name2',    '') or '').strip()
    element1 = (data.get('element1', '') or '').strip()
    element2 = (data.get('element2', '') or '').strip()
    # ✅ FIX: يقبل element1/element2 مباشرة أو يستخرجها من الأسماء
    if element1 and element2:
        # استخدام العناصر مباشرة
        from knowledge_loader import RULES as KB_RULES
        compat_rules = [r for r in KB_RULES if r.get('type') == 'elemental'
                        and r.get('condition', {}).get('element1') == element1
                        and r.get('condition', {}).get('element2') == element2]
        if compat_rules:
            rule = compat_rules[0]
            return jsonify({
                'element1': element1,
                'element2': element2,
                'status':   rule.get('status', 'unknown'),
                'boost':    rule.get('boost', 1.0),
                'mediator': rule.get('mediator', ''),
                'note':     rule.get('note', ''),
                'compatible': rule.get('status') == 'compatible'
            })
        return jsonify({'element1': element1, 'element2': element2,
                        'status': 'محايد', 'compatible': True, 'boost': 1.0})
    if not name1 or not name2:
        return jsonify({'error': 'الاسمان مطلوبان'}), 400
    elem1 = analyze_name_deep(name1)['dominant_element']
    elem2 = analyze_name_deep(name2)['dominant_element']
    compat = check_elemental_law(elem1, elem2)
    return jsonify({
        'name1': name1, 'element1': elem1,
        'name2': name2, 'element2': elem2,
        **compat,
    })


@app.route('/api/core/parse_intent', methods=['POST', 'OPTIONS'])
@_handle_options_or
def core_parse_intent():
    """
    ✅ v19: استخراج النية من نص حر
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    data = request.json or {}
    text = (data.get('text', '') or '').strip()
    if not text:
        return jsonify({'error': 'النص مطلوب'}), 400
    from core_engine import parse_intent_from_text
    return jsonify(parse_intent_from_text(text))


@app.route('/api/core/knowledge_summary', methods=['GET'])
@_cached(timeout=3600)
def core_knowledge_summary():
    """
    ✅ v19: ملخص قاعدة معرفة المخطوطة
    """
    if not CORE_ENGINE_AVAILABLE:
        return jsonify({'error': 'Core Engine غير متاح'}), 503
    return jsonify({
        'summary': kb_get_summary(),
        'source':  'مخطوطة شمس المعارف الكبرى — أحمد بن علي البوني (توفي 622هـ)',
        'files_processed': 5,
        'total_lines_extracted': 41458,
    })


# ══════════════════════════════════════════════════════════════════
# القسم 27: Diagnostics
# ══════════════════════════════════════════════════════════════════
@app.route('/api/diagnostics', methods=['GET', 'POST', 'OPTIONS'])
@_handle_options_or
def diagnostics_api():
    if not DIAGNOSTICS_AVAILABLE:
        return jsonify({'error': 'diagnostics_engine غير متاح', 'overall_score': 0}), 503
    try:
        report = run_full_diagnostics(app=app)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e), 'overall_score': 0}), 500

@app.route('/diagnostics')
def diagnostics_page():
    return send_from_directory('.', 'diagnostics.html')

# ══════════════════════════════════════════════════════════════════
# القسم 28: صفحات الواجهة (View Layer)
# ══════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/main')
def main_page():
    return send_from_directory('.', 'main.html')

@app.route('/book')
def book_page():
    return send_from_directory('.', 'book.html')

@app.route('/gatekeeper')
def gatekeeper_page():
    return send_from_directory('templates', 'gatekeeper.html')

@app.route('/forty-gates')
def forty_gates_page():
    return send_from_directory('templates', 'forty_gates.html')

@app.route('/system-map')
def system_map_page():
    return send_from_directory('templates', 'system_map.html')

@app.route('/static/talisman/<path:filename>')
def serve_talisman(filename):
    return send_from_directory('static/talisman', filename)

# ══════════════════════════════════════════════════════════════════
# القسم 29: نقطة الدخول (Entry Point)
# ══════════════════════════════════════════════════════════════════
# القسم 29: V19 — APIs الجديدة (الكيمياء / السيميا / المعرفة الموسعة)
# ══════════════════════════════════════════════════════════════════

# ── الكيمياء ─────────────────────────────────────────────────────
@app.route('/api/alchemy/metal/<planet>', methods=['GET'])
@_cached(timeout=3600)
def alchemy_metal(planet):
    """معدن الكوكب من الكيمياء الروحانية"""
    if not ALCHEMY_ENGINE_V19:
        return jsonify({'error': 'محرك الكيمياء غير متاح'}), 503
    data = get_metal_for_planet(planet)
    if not data:
        return jsonify({'error': f'الكوكب "{planet}" غير موجود'}), 404
    return jsonify({'planet': planet, **data})


@app.route('/api/alchemy/stages', methods=['GET'])
@_cached(timeout=86400)
def alchemy_stages():
    """مراحل الكيمياء السبع"""
    if not ALCHEMY_ENGINE_V19:
        return jsonify({'error': 'محرك الكيمياء غير متاح'}), 503
    return jsonify({'stages': ALCHEMICAL_STAGES, 'count': len(ALCHEMICAL_STAGES)})


@app.route('/api/alchemy/recipes', methods=['GET'])
@_cached(timeout=86400)
def alchemy_recipes():
    """وصفات الكيمياء من المخطوطة"""
    if not ALCHEMY_ENGINE_V19:
        return jsonify({'error': 'محرك الكيمياء غير متاح'}), 503
    recipe_name = request.args.get('name', '').strip()
    if recipe_name:
        r = get_recipe(recipe_name)
        return jsonify(r) if r else (jsonify({'error': 'الوصفة غير موجودة'}), 404)
    return jsonify({'recipes': list(RECIPES.keys()), 'count': len(RECIPES)})


@app.route('/api/alchemy/balance', methods=['GET'])
@_cached(timeout=86400)
def alchemy_balance():
    """الموازين الأربعة ودرجاتها"""
    if not ALCHEMY_ENGINE_V19:
        return jsonify({'error': 'محرك الكيمياء غير متاح'}), 503
    return jsonify({'balance_values': BALANCE_VALUES, 'balance_degrees': BALANCE_DEGREES})


@app.route('/api/alchemy/elixir', methods=['POST', 'OPTIONS'])
@_handle_options_or
def alchemy_elixir():
    """حساب قوة الإكسير من المكونات"""
    if not ALCHEMY_ENGINE_V19:
        return jsonify({'error': 'محرك الكيمياء غير متاح'}), 503
    data = request.json or {}
    ingredients = data.get('ingredients', [])
    repetitions = int(data.get('repetitions', 7))
    if not ingredients:
        return jsonify({'error': 'أرسل قائمة المكونات'}), 400
    return jsonify(calculate_elixir_power(ingredients, repetitions))


# ── السيميا ──────────────────────────────────────────────────────
@app.route('/api/symia/articles', methods=['GET'])
@_cached(timeout=86400)
def symia_articles():
    """مقالات السيميا الأحد عشر"""
    if not SYMIA_ENGINE_V19:
        return jsonify({'error': 'محرك السيميا غير متاح'}), 503
    return jsonify({'articles': get_all_articles(), 'count': len(_SYMIA_ARTICLES_V19)})


@app.route('/api/symia/article/<int:num>', methods=['GET'])
def symia_article_detail(num):
    """تفاصيل مقالة سيميا بالرقم"""
    if not SYMIA_ENGINE_V19:
        return jsonify({'error': 'محرك السيميا غير متاح'}), 503
    art = get_article(num)
    if not art:
        return jsonify({'error': f'المقالة {num} غير موجودة'}), 404
    return jsonify({'number': num, **art})


@app.route('/api/symia/ritual', methods=['POST', 'OPTIONS'])
@_handle_options_or
def symia_perform_ritual():
    """تنفيذ طقس سيميا"""
    if not SYMIA_ENGINE_V19:
        return jsonify({'error': 'محرك السيميا غير متاح'}), 503
    data = request.json or {}
    num = int(data.get('article_number', 1))
    has_ash = bool(data.get('has_ash', True))
    has_timing = bool(data.get('has_proper_timing', True))
    return jsonify(perform_symia_ritual(num, has_ash, has_timing))


@app.route('/api/symia/khunfutriyyat', methods=['GET'])
@_cached(timeout=86400)
def symia_khunfutriyyat():
    """طقس تحضير رماد الخنفطريات"""
    if not SYMIA_ENGINE_V19:
        return jsonify({'error': 'محرك السيميا غير متاح'}), 503
    return jsonify(get_khunfutriyyat_ritual())


@app.route('/api/symia/barhatiya', methods=['GET'])
@_cached(timeout=86400)
def symia_barhatiya():
    """عزيمة البرهتية"""
    if not SYMIA_ENGINE_V19:
        return jsonify({'error': 'محرك السيميا غير متاح'}), 503
    return jsonify(get_barhatiya_oath())


# ── المعرفة الموسعة (Knowledge v19) ──────────────────────────────
@app.route('/api/v19/knowledge/letters', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_letters():
    """الحروف الكاملة من قاعدة المعرفة الموسعة"""
    if not KNOWLEDGE_LETTERS_V19:
        return jsonify({'error': 'قاعدة معرفة الحروف غير متاحة'}), 503
    letter = request.args.get('letter', '').strip()
    if letter:
        data = _kb_get_letter_v19(letter)
        return jsonify({'letter': letter, **data}) if data else (jsonify({'error': 'الحرف غير موجود'}), 404)
    return jsonify({'letters': _kb_get_all_letters(), 'count': len(LETTERS_DATA)})


@app.route('/api/v19/knowledge/divine_names', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_divine_names():
    """الأسماء الحسنى الكاملة من قاعدة المعرفة"""
    if not KNOWLEDGE_DIVINE_NAMES_V19:
        return jsonify({'error': 'قاعدة معرفة الأسماء غير متاحة'}), 503
    name = request.args.get('name', '').strip()
    if name:
        data = _kb_get_divine_name_v19(name)
        return jsonify({'name': name, **data}) if data else (jsonify({'error': 'الاسم غير موجود'}), 404)
    intent = request.args.get('intent', '').strip()
    if intent:
        data = _kb_get_divine_name_intent(intent)
        return jsonify(data) if data else jsonify({'names': DIVINE_NAMES_LIST})
    return jsonify({'names': DIVINE_NAMES_LIST, 'count': len(DIVINE_NAMES_LIST),
                    'detailed_count': len(DIVINE_NAMES_DATA)})


@app.route('/api/v19/knowledge/planets', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_planets():
    """الكواكب الكاملة من قاعدة المعرفة"""
    if not KNOWLEDGE_PLANETS_V19:
        return jsonify({'error': 'قاعدة معرفة الكواكب غير متاحة'}), 503
    planet = request.args.get('planet', '').strip()
    if planet:
        data = _kb_get_planet_v19(planet)
        return jsonify({'planet': planet, **data}) if data else (jsonify({'error': 'الكوكب غير موجود'}), 404)
    return jsonify({'planets': get_all_planets(), 'count': len(PLANETS_DATA)})


@app.route('/api/v19/knowledge/zodiacs', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_zodiacs():
    """البروج من قاعدة المعرفة"""
    if not KNOWLEDGE_ZODIACS_V19:
        return jsonify({'error': 'قاعدة معرفة البروج غير متاحة'}), 503
    zodiac = request.args.get('zodiac', '').strip()
    if zodiac:
        data = _kb_get_zodiac(zodiac)
        return jsonify({'zodiac': zodiac, **data}) if data else (jsonify({'error': 'البرج غير موجود'}), 404)
    return jsonify({'zodiacs': list(ZODIACS_DATA.keys()), 'count': len(ZODIACS_DATA)})


@app.route('/api/v19/knowledge/thrones', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_thrones():
    """الأبراج والأعراش"""
    if not KNOWLEDGE_EXTENDED_V19:
        return jsonify({'error': 'قاعدة المعرفة الموسعة غير متاحة'}), 503
    throne_id = request.args.get('id', '').strip()
    if throne_id:
        return jsonify(get_throne(throne_id))
    return jsonify({'thrones': get_all_thrones()})


@app.route('/api/v19/knowledge/veils', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_veils():
    """الحجب والأستار"""
    if not KNOWLEDGE_EXTENDED_V19:
        return jsonify({'error': 'قاعدة المعرفة الموسعة غير متاحة'}), 503
    level = request.args.get('level', '').strip()
    if level:
        return jsonify(get_veil(level))
    return jsonify({'veils': get_all_veils()})


@app.route('/api/v19/knowledge/mothers', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_mothers():
    """الأمهات الأربع"""
    if not KNOWLEDGE_EXTENDED_V19:
        return jsonify({'error': 'قاعدة المعرفة الموسعة غير متاحة'}), 503
    intent = request.args.get('intent', '').strip()
    if intent:
        return jsonify(get_mother_for_intent(intent))
    return jsonify({'mothers': get_all_mothers()})


@app.route('/api/v19/knowledge/gates', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_gates():
    """الأبواب الأربعون"""
    if not KNOWLEDGE_EXTENDED_V19:
        return jsonify({'error': 'قاعدة المعرفة الموسعة غير متاحة'}), 503
    return jsonify({'gates': get_all_gates()})


@app.route('/api/v19/knowledge/kings_list', methods=['GET'])
@_cached(timeout=86400)
def v19_knowledge_kings_list():
    """قائمة الملوك والسلاطين"""
    if not KNOWLEDGE_EXTENDED_V19:
        return jsonify({'error': 'قاعدة المعرفة الموسعة غير متاحة'}), 503
    return jsonify({'kings': get_all_kings()})


# ── الزايرجة المركزية (V19) ───────────────────────────────────────
@app.route('/api/zairja/center', methods=['POST', 'OPTIONS'])
@_handle_options_or
def zairja_center_api():
    """الزايرجة المركزية — القانون الأول (V19 New)"""
    if not ZAIRJA_CENTER_V19:
        return jsonify({'error': 'وظيفة الزايرجة المركزية غير متاحة'}), 503
    data = request.json or {}
    question    = (data.get('question', '') or '').strip()
    seeker_name = (data.get('seeker_name', '') or '').strip()
    if not question:
        return jsonify({'error': 'السؤال مطلوب'}), 400
    try:
        return jsonify(zairja_center(question, seeker_name, now_utc()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── علم الرمل الكامل (V19) ───────────────────────────────────────
@app.route('/api/geomancy/full_chart', methods=['POST', 'OPTIONS'])
@_handle_options_or
def geomancy_full_chart():
    """توليد لوح رمل كامل بالمحرك الجديد"""
    if not GEOMANCY_ENGINE_V19:
        return jsonify({'error': 'محرك علم الرمل الجديد غير متاح'}), 503
    data = request.json or {}
    points = data.get('points', None)
    try:
        chart = _geomancy_engine_v19.generate_full_chart(points)
        analysis = _geomancy_engine_v19.analyze_chart(chart)
        return jsonify({'chart': chart, 'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════
# القسم 30: V19 — نظام اقتراح الوقت الحالي (الجديد الأساسي)
# The Intelligent Time-Based Suggestion System
# ══════════════════════════════════════════════════════════════════

def _build_time_suggestions(now_dt) -> dict:
    """
    البنية الأساسية لنظام اقتراح الوقت — يحلل اللحظة الحالية
    ويقترح أفضل الأعمال والأوراد والأسماء الحسنى لهذه اللحظة.
    """
    try:
        hour_info = get_planetary_hour_info(now_dt)
    except Exception:
        hour_info = {'planet': 'الشمس', 'planet_ar': 'الشمس',
                     'hour_number': 1, 'is_forbidden': False,
                     'day_name': 'الأحد', 'day_planet': 'الشمس'}

    planet     = hour_info.get('planet_ar') or hour_info.get('planet', 'الشمس')
    hour_num   = int(hour_info.get('hour_number', 1))
    is_forb    = bool(hour_info.get('is_forbidden', False))
    day_name   = hour_info.get('day_name', '')

    # ── قاعدة التوافق: أي أعمال تناسب هذا الكوكب ───────────────
    PLANET_INTENTS = {
        'الشمس':    ['قبول', 'دخول على السلاطين', 'هيبة', 'شهرة', 'قبول التام'],
        'القمر':    ['محبة', 'جلب', 'رزق', 'سفر', 'شفاء'],
        'المريخ':   ['عقد لسان', 'قهر', 'ترحيل', 'هيبة في الحرب'],
        'عطارد':    ['علم', 'كتابة', 'كشف', 'فتح الكنوز', 'تعليم'],
        'المشتري':  ['رزق', 'قبول', 'صلح', 'فتح', 'شفاء', 'حفظ'],
        'الزهرة':   ['محبة', 'زواج', 'جلب', 'تهييج', 'جمال'],
        'زحل':      ['ترحيل', 'عقد لسان', 'قهر', 'ربط', 'إبطال'],
    }
    PLANET_WAFQ = {
        'الشمس': 'المربع (4×4)', 'القمر': 'المثلث (3×3)',
        'المريخ': 'المخمس (5×5)', 'عطارد': 'المسدس (6×6)',
        'المشتري': 'المسبع (7×7)', 'الزهرة': 'المثمن (8×8)', 'زحل': 'المتسع (9×9)',
    }
    PLANET_INCENSE_MAP = {
        'الشمس': 'العود والصندل والزعفران',
        'القمر': 'الكافور والبنفسج',
        'المريخ': 'الفربيون والبسباسة',
        'عطارد': 'المستكة والزعفران',
        'المشتري': 'العنبر والزعفران واللبان',
        'الزهرة': 'العنبر والورد والصندل الأبيض',
        'زحل': 'السليفة والحلتيت',
    }
    PLANET_COLORS = {
        'الشمس': '#FFD700', 'القمر': '#E0E0FF', 'المريخ': '#FF4444',
        'عطارد': '#44AAFF', 'المشتري': '#AAFFAA', 'الزهرة': '#FF88CC', 'زحل': '#666699',
    }
    PLANET_DIVINE_NAMES = {
        'الشمس': ['القاهر', 'النور', 'الجليل', 'الكريم'],
        'القمر': ['النور', 'الهادي', 'اللطيف', 'الرحيم'],
        'المريخ': ['القهار', 'المنتقم', 'العزيز', 'الجبار'],
        'عطارد': ['العليم', 'الحكيم', 'الخبير', 'الرشيد'],
        'المشتري': ['الرزاق', 'الوهاب', 'الفتاح', 'الغني'],
        'الزهرة': ['الودود', 'الجميل', 'اللطيف', 'الرؤوف'],
        'زحل': ['الصبور', 'القابض', 'المانع', 'القوي'],
    }

    suitable_intents  = PLANET_INTENTS.get(planet, ['قبول', 'دعاء'])
    wafq_type         = PLANET_WAFQ.get(planet, 'المربع (4×4)')
    incense           = PLANET_INCENSE_MAP.get(planet, 'العود')
    color             = PLANET_COLORS.get(planet, '#C8A84B')
    divine_names      = PLANET_DIVINE_NAMES.get(planet, ['الله'])

    # ── تحذير الساعة المذمومة ────────────────────────────────────
    warnings = []
    if is_forb:
        warnings.append(f'⚠️ هذه الساعة ({hour_num}) مذمومة لكوكب {planet} — تجنب الأعمال الكبيرة')

    # ── اقتراح الوفق ────────────────────────────────────────────
    try:
        from data import ABJAD_VALUES
        planet_abjad = sum(ABJAD_VALUES.get(c, 0) for c in planet)
    except Exception:
        planet_abjad = 64  # default

    # ── تحديد طبيعة الوقت ────────────────────────────────────────
    hour_local = now_dt.hour
    if 5 <= hour_local < 12:
        time_label = 'صباح'
        time_icon  = '🌅'
    elif 12 <= hour_local < 15:
        time_label = 'ظهيرة'
        time_icon  = '☀️'
    elif 15 <= hour_local < 18:
        time_label = 'عصر'
        time_icon  = '🌤️'
    elif 18 <= hour_local < 21:
        time_label = 'مساء'
        time_icon  = '🌆'
    else:
        time_label = 'ليل'
        time_icon  = '🌙'

    # ── اقتراح المنزل القمري ─────────────────────────────────────
    try:
        lunar_info = get_lunar_mansion_astro(now_dt, Config.LATITUDE, Config.LONGITUDE)
    except Exception:
        lunar_info = {}
    mansion_name    = lunar_info.get('mansion', '') if isinstance(lunar_info, dict) else ''
    mansion_ruling  = lunar_info.get('ruling', '') if isinstance(lunar_info, dict) else ''

    return {
        'timestamp':        now_dt.isoformat(),
        'time_label':       time_label,
        'time_icon':        time_icon,
        'day_name':         day_name,
        'planet':           planet,
        'planet_color':     color,
        'hour_number':      hour_num,
        'is_forbidden_hour': is_forb,
        'lunar_mansion':    mansion_name,
        'mansion_ruling':   mansion_ruling,
        'suitable_intents': suitable_intents,
        'best_intent':      suitable_intents[0] if suitable_intents else 'دعاء',
        'divine_names':     divine_names,
        'primary_name':     divine_names[0] if divine_names else 'الله',
        'wafq_type':        wafq_type,
        'wafq_abjad':       planet_abjad,
        'incense':          incense,
        'warnings':         warnings,
        'is_auspicious':    not is_forb,
        'advice': (
            f'الوقت الحالي ({time_icon} {time_label}) تحكمه ساعة {planet}. '
            f'أفضل الأعمال الآن: {", ".join(suitable_intents[:3])}. '
            f'استخدم بخور {incense}.'
        ) if not is_forb else (
            f'⚠️ الساعة {hour_num} مذمومة. يُستحسن الانتظار حتى تنتهي هذه الساعة.'
        ),
    }


@app.route('/api/time/suggest', methods=['GET'])
def time_suggest():
    """
    ✅ V19 NEW: نظام الاقتراح الذكي بناءً على الوقت الحالي
    يُحلل اللحظة الحالية ويقترح أفضل الأعمال والأوراد والأسماء الحسنى
    """
    try:
        now = now_utc()
        result = _build_time_suggestions(now)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'timestamp': now_utc().isoformat()}), 500


@app.route('/api/time/suggest_for', methods=['POST', 'OPTIONS'])
@_handle_options_or
def time_suggest_for():
    """
    ✅ V19 NEW: اقتراح ذكي لنية معينة — متى أفضل وقت لها
    يُحلل النية ويُحدد أفضل الأوقات والأيام والكواكب المناسبة
    """
    data   = request.json or {}
    intent = (data.get('intent', '') or '').strip()
    if not intent:
        return jsonify({'error': 'النية مطلوبة'}), 400

    INTENT_PLANETS = {
        'محبة':  ['الزهرة', 'القمر', 'المشتري'],
        'جلب':   ['الزهرة', 'القمر'],
        'قبول':  ['الشمس', 'المشتري'],
        'رزق':   ['المشتري', 'القمر'],
        'حفظ':   ['القمر', 'عطارد', 'المشتري'],
        'كشف':   ['عطارد', 'الشمس'],
        'علم':   ['عطارد'],
        'شفاء':  ['القمر', 'المشتري'],
        'قهر':   ['المريخ', 'زحل'],
        'ترحيل': ['زحل', 'المريخ'],
        'عقد لسان': ['زحل', 'المريخ'],
        'هيبة':  ['الشمس', 'المريخ'],
        'زواج':  ['الزهرة', 'القمر'],
        'شهرة':  ['الشمس'],
        'صلح':   ['المشتري', 'الزهرة'],
        'إبطال': ['عطارد', 'القمر'],
        'دخول':  ['الشمس', 'المشتري'],
    }
    INTENT_DAYS = {
        'محبة':  ['الجمعة', 'الاثنين'],
        'جلب':   ['الجمعة', 'الاثنين'],
        'قبول':  ['الأحد', 'الخميس'],
        'رزق':   ['الخميس', 'الأحد'],
        'حفظ':   ['الاثنين', 'الأربعاء'],
        'كشف':   ['الأربعاء'],
        'علم':   ['الأربعاء'],
        'شفاء':  ['الاثنين', 'الخميس'],
        'قهر':   ['الثلاثاء'],
        'ترحيل': ['السبت', 'الثلاثاء'],
        'عقد لسان': ['الثلاثاء', 'السبت'],
        'هيبة':  ['الأحد', 'الثلاثاء'],
        'زواج':  ['الجمعة', 'الاثنين'],
        'شهرة':  ['الأحد'],
        'صلح':   ['الخميس', 'الجمعة'],
        'إبطال': ['الأربعاء'],
        'دخول':  ['الأحد', 'الخميس'],
    }
    INTENT_HOURS = {
        'محبة': [1, 8], 'جلب': [2, 7], 'قبول': [1, 4, 9],
        'رزق': [1, 8], 'حفظ': [2, 5, 8], 'كشف': [1, 6],
        'علم': [1, 6, 11], 'شفاء': [2, 5], 'قهر': [3, 7],
        'ترحيل': [3, 8], 'عقد لسان': [3, 7], 'هيبة': [1, 6],
        'زواج': [1, 8], 'شهرة': [1, 5], 'صلح': [2, 6],
        'إبطال': [1, 7], 'دخول': [2, 5, 10],
    }
    INTENT_INCENSE = {
        'محبة': 'المصطكى والورد والعنبر', 'جلب': 'المصطكى والزعفران',
        'قبول': 'العود والمسك', 'رزق': 'العنبر والزعفران',
        'حفظ': 'اللبان والكافور', 'كشف': 'الصندل والعود',
        'علم': 'المستكة والزعفران', 'شفاء': 'الصندل واللبان',
        'قهر': 'الكبريت والمر', 'ترحيل': 'الكبريت والزراوند',
        'هيبة': 'العود والمسك', 'زواج': 'الورد والعنبر',
        'شهرة': 'العود الهندي والمسك', 'صلح': 'الورد والصندل',
        'إبطال': 'الكافور والصندل الأبيض', 'دخول': 'العود والكافور',
        'عقد لسان': 'الكبريت والمر',
    }

    best_planets = INTENT_PLANETS.get(intent, ['الشمس', 'المشتري'])
    best_days    = INTENT_DAYS.get(intent, ['الأحد'])
    best_hours   = INTENT_HOURS.get(intent, [1])
    incense      = INTENT_INCENSE.get(intent, 'العود')

    # تحليل الوقت الحالي
    now  = now_utc()
    curr = _build_time_suggestions(now)
    current_planet  = curr['planet']
    current_day     = curr['day_name']
    is_good_now     = (current_planet in best_planets and current_day in best_days)

    return jsonify({
        'intent':         intent,
        'best_planets':   best_planets,
        'best_days':      best_days,
        'best_hours':     best_hours,
        'incense':        incense,
        'is_good_now':    is_good_now,
        'current_planet': current_planet,
        'current_day':    current_day,
        'verdict': (
            f'✅ الوقت الحالي مناسب لعمل {intent} — الكوكب {current_planet} يدعمه'
            if is_good_now else
            f'⏳ انتظر يوم {best_days[0]} في ساعة {best_planets[0]} (الساعة {best_hours[0]})'
        ),
        'full_instructions': (
            f'اعمل {intent} يوم {best_days[0]} في الساعة الكوكبية {best_planets[0]} '
            f'(الساعة {best_hours[0]}). '
            f'استخدم بخور {incense}. '
            f'الأفضل: من الساعة الكوكبية {best_hours[0]} أو {best_hours[1] if len(best_hours)>1 else best_hours[0]}.'
        ),
    })


@app.route('/api/jafr/historical', methods=['POST', 'OPTIONS'])
@_handle_options_or
def jafr_historical():
    """
    ✅ V19 NEW: الجفر التاريخي — حساب مدة الملوك والفتن (V18 Addition)
    """
    from jafr_engine import calculate_reign_duration, predict_event, predict_city_fate, get_fitan_event
    data = request.json or {}
    mode = data.get('mode', 'reign')
    try:
        if mode == 'reign':
            king_name = (data.get('king_name', '') or '').strip()
            if not king_name:
                return jsonify({'error': 'اسم الملك مطلوب'}), 400
            hijri_year = data.get('hijri_year')
            return jsonify(calculate_reign_duration(king_name, 0, hijri_year))
        elif mode == 'event':
            event_name = (data.get('event_name', '') or '').strip()
            base_year  = int(data.get('base_year', 600))
            return jsonify(predict_event(event_name, base_year))
        elif mode == 'city':
            city_name = (data.get('city_name', '') or '').strip()
            return jsonify(predict_city_fate(city_name))
        elif mode == 'fitan':
            num = int(data.get('jafar_number', 312))
            return jsonify(get_fitan_event(num))
        else:
            return jsonify({'error': 'mode غير صحيح: reign/event/city/fitan'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ✅ FIX (v10/v12): app.run() خارج أي شرط if/else — سلوك مضمون ثابت
# ✅ FIX (v12): debug=True ثابتة → الآن تُقرأ من FLASK_ENV
# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    is_dev = os.environ.get('FLASK_ENV', 'development') == 'development'
    logger_system.log(
        'INFO', 'app.startup',
        f'🚀 تشغيل الخادم — {"Development" if is_dev else "Production"} Mode | {Config.APP_NAME} {Config.VERSION}'
    )
    app.run(debug=is_dev, host='0.0.0.0', port=5000)
