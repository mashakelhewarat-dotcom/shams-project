# -*- coding: utf-8 -*-
"""
talisman_engine.py
═══════════════════════════════════════════════════════════════════
محرك اختيار وتقديم الطلاسم + التوليد الديناميكي للأوفاق
النسخة النهائية — يربط الصور الحقيقية بالسياق الروحاني.
⚠️ المعدل ليتوافق مع مجلد static/images/
═══════════════════════════════════════════════════════════════════
"""

import os
from typing import Optional, Dict, List

from wafq_generator import WafqGenerator
from shams_data_extended import TALISMANS_DB, TWISTED_TALISMANS, PROPHETIC_SEALS

IMAGES_FOLDER   = "static"
TALISMANS_FOLDER = os.path.join(IMAGES_FOLDER, "talisman")
os.makedirs(TALISMANS_FOLDER, exist_ok=True)

# مولد الأوفاق الديناميكي
wafq_gen = WafqGenerator(img_size=500)

# ============================================================================
# الربط السياقي: حالة → مجموعة صور (معدل: جميع المسارات تبدأ بـ images/)
# ============================================================================
CONTEXT_IMAGE_MAP = {
    # خواتم سليمان وإدريس
    "seal":         ["images/seals/solomon_1.png","images/seals/solomon_2.png","images/seals/solomon_3.png","images/seals/solomon_4.png"],
    "idris":        ["images/seals/idris_seal_1.png","images/seals/idris_seal_2.png","images/seals/idris_seal_3.png","images/seals/idris_seal_4.png"],
    # عقدة الحكيم (للأبواب الظلمانية)
    "hakim":        ["images/talisman/hakim_knot_0.png","images/talisman/hakim_knot_2.png",
                     "images/talisman/hakim_knot_3.png","images/talisman/hakim_knot_4.png","images/talisman/hakim_knot_5.png"],
    # ميزان العدل (للأوفاق الكبيرة)
    "mizan":        ["images/mizan/mizan_al_3adl_16_3.png","images/mizan/mizan_al_3adl_16_4.png",
                     "images/mizan/mizan_al_3adl_16_12.png","images/mizan/mizan_al_3dl_16_5.jpeg"],
    # الأبراج
    "zodiac":       ["images/zodiac/zodiac_all.png","images/zodiac/zodiac_disc.png","images/zodiac/zodiac_all2.png"],
    "zodiac_aries": ["images/zodiac/zodiac_aries.png"],
    "zodiac_taurus":["images/zodiac/zodiac_taurus.png"],
    "zodiac_gemini":["images/zodiac/zodiac_gemini.png"],
    "zodiac_cancer":["images/zodiac/zodiac_cancer.png"],
    "zodiac_leo":   ["images/zodiac/zodiac_leo.png"],
    "zodiac_virgo": ["images/zodiac/zodiac_virgo.png"],
    "zodiac_libra": ["images/zodiac/zodiac_libra.png"],
    # منازل القمر
    "mansions":     ["images/mansions/mansion_thuraya.png","images/mansions/mansion_butayn.png",
                     "images/mansions/mansion_dabaran.png","images/mansions/mansion_haqaa.png"],
    # الرمل
    "geomancy":     ["images/geomancy/geo_jamaa.png","images/geomancy/geo_farah.png",
                     "images/geomancy/geo_ribh.png","images/geomancy/geo_saada.png"],
    # الوفق الفاتحة والمكتوب
    "wafq_written": ["images/talisman/wafq_fatiha.png","images/talisman/wafq_perfect_1.png",
                     "images/talisman/wafq_engraved_1.png","images/talisman/wafq_large_1.png"],
    # أيقونة عامة
    "cinematic":    ["images/cinematic/cinematic_1.png","images/cinematic/cinematic_2.png","images/cinematic/cinematic_3.png"],
    "astro":        ["images/astro/astro_float_1.png","images/astro/astro_float_2.png","images/astro/astro_mystic_1.png"],
}

ZODIAC_MAP = {
    'الحمل':'zodiac_aries','الثور':'zodiac_taurus','الجوزاء':'zodiac_gemini',
    'السرطان':'zodiac_cancer','الأسد':'zodiac_leo','السنبلة':'zodiac_virgo',
    'الميزان':'zodiac_libra','العقرب':'zodiac','القوس':'zodiac',
    'الجدي':'zodiac','الدلو':'zodiac','الحوت':'zodiac',
}

def _img_url(rel_path: str) -> Optional[str]:
    """إرجاع URL الصورة إذا كانت موجودة."""
    full = os.path.join(IMAGES_FOLDER, rel_path)
    if os.path.isfile(full):
        return f"/{IMAGES_FOLDER}/{rel_path}"
    return None

def get_context_images(context: str, max_count: int = 4) -> List[str]:
    """إرجاع قائمة صور ذات صلة بالسياق."""
    paths = CONTEXT_IMAGE_MAP.get(context, CONTEXT_IMAGE_MAP.get("cinematic", []))
    result = []
    for p in paths[:max_count]:
        url = _img_url(p)
        if url:
            result.append(url)
    return result

def get_talisman_url(key: str) -> Optional[str]:
    """إرجاع URL الطلسم الثابت."""
    filename = TALISMANS_DB.get(key)
    if filename:
        return _img_url(filename)
    return None

def get_talisman_from_recommendation(recommendation: Dict) -> Optional[str]:
    """
    استخراج أو توليد الطلسم من التوصية.
    الأولوية:
      1. صورة ثابتة إن وُجدت
      2. صورة ميزان العدل (للأوفاق الكبيرة ≥ 4x4)
      3. وفق ديناميكي Base64
    """
    # 1. محاولة صورة ثابتة
    key = recommendation.get("talisman", "") or recommendation.get("asma", "")

    # حالة الأبواب الظلمانية → عقدة الحكيم
    if recommendation.get("is_empty_center"):
        imgs = get_context_images("hakim")
        if imgs:
            return imgs[0]

    # حالة وجود برج → صورة البرج
    zodiac_name = recommendation.get("zodiac_name", "")
    if zodiac_name and zodiac_name in ZODIAC_MAP:
        imgs = get_context_images(ZODIAC_MAP[zodiac_name])
        if imgs:
            return imgs[0]

    # حالة ختم سليمان أو إدريس
    if "سليمان" in key or "solomon" in key.lower():
        imgs = get_context_images("seal")
        return imgs[0] if imgs else None
    if "إدريس" in key or "idris" in key.lower():
        imgs = get_context_images("idris")
        return imgs[0] if imgs else None

    # حالة ميزان العدل (وفق كبير)
    wtype = recommendation.get("wafq_type", "")
    if any(x in wtype for x in ["المربع","المخمس","4x4","5x5","المسدس","6x6"]):
        imgs = get_context_images("mizan")
        if imgs:
            return imgs[0]

    # 2. بحث في TALISMANS_DB
    if key:
        url = get_talisman_url(key)
        if url:
            return url

    # 3. توليد وفق ديناميكي
    wafq_type    = recommendation.get("wafq_type",   "المثلث")
    total_value  = recommendation.get("total_value",  0)
    if total_value == 0:
        total_value = recommendation.get("jummal", recommendation.get("code9", 114))

    is_empty = recommendation.get("is_empty_center", False)
    c_val    = recommendation.get("center_value",    0)
    top_text = recommendation.get("asma", recommendation.get("name", "وفق"))
    corners  = recommendation.get("angels", ["جبرائيل","ميكائيل","إسرافيل","عزرائيل"])

    try:
        return wafq_gen.generate_wafq(
            wafq_type=wafq_type,
            total_value=total_value,
            is_empty_center=is_empty,
            center_value=c_val,
            top_text=top_text,
            corners=corners,
        )
    except Exception as e:
        print(f"⚠️ خطأ في توليد الوفق: {e}")
        return None

def list_available_talismans() -> List[Dict]:
    """قائمة الطلاسم الثابتة المتوفرة."""
    available = []
    for key, filename in TALISMANS_DB.items():
        full_path = os.path.join(IMAGES_FOLDER, filename)
        if os.path.isfile(full_path):
            available.append({"key": key, "url": f"/{IMAGES_FOLDER}/{filename}"})
    return available

import math
from io import BytesIO
import base64

# ── طلاسم هندسية (مدموج من DeepSeek) ──
def generate_geometric_talisman(talisman_type: str, size: int = 500, color: str = "#ffaa44") -> str:
    """
    توليد طلسم هندسي (خاتم سليمان، نجمة سداسية، دائرة الأسماء، مربع التسعة).
    الأنواع: "solomon_seal", "hexagram", "circle_of_names", "square_of_nine"
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2
    radius = size // 2 - 20
    rgb_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    if talisman_type == "solomon_seal":
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append((x, y))
        draw.polygon([points[0], points[2], points[4]], outline=rgb_color, width=3, fill=None)
        draw.polygon([points[1], points[3], points[5]], outline=rgb_color, width=3, fill=None)
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=rgb_color, width=2)
        
    elif talisman_type == "hexagram":
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append((x, y))
        for i in range(6):
            draw.line([points[i], points[(i+2)%6]], fill=rgb_color, width=2)
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=rgb_color, width=2)
        
    elif talisman_type == "circle_of_names":
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=rgb_color, width=3)
        for r in range(radius-30, 30, -30):
            draw.ellipse([center-r, center-r, center+r, center+r], outline=rgb_color, width=1)
        star_size = 40
        star_pts = []
        for i in range(5):
            angle = math.radians(72 * i - 90)
            x = center + star_size * math.cos(angle)
            y = center + star_size * math.sin(angle)
            star_pts.append((x, y))
        draw.polygon(star_pts, outline=rgb_color, fill=None, width=2)
        
    elif talisman_type == "square_of_nine":
        cell = (size - 100) // 3
        offset = 50
        for i in range(4):
            x = offset + i * cell
            draw.line([(x, offset), (x, offset + 3*cell)], fill=rgb_color, width=2)
            draw.line([(offset, offset + i*cell), (offset + 3*cell, offset + i*cell)], fill=rgb_color, width=2)
        numbers = [4,9,2,3,5,7,8,1,6]
        for idx, num in enumerate(numbers):
            row = idx // 3
            col = idx % 3
            x = offset + col * cell + cell//2
            y = offset + row * cell + cell//2
            draw.text((x-10, y-10), str(num), fill=rgb_color)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


# ══════════════════════════════════════════════════════════════
# bird_script — أقلام الطيور (التشفير البصري من شمس المعارف)
# ══════════════════════════════════════════════════════════════
BIRD_MAP = {
    'ا':'◀','أ':'◀','إ':'◀','آ':'◀','ب':'▶','ج':'▲','د':'▼',
    'ه':'◆','ة':'◆','و':'◉','ز':'★','ح':'☆','ط':'◻','ي':'◼',
    'ى':'◼','ك':'⬤','ل':'♦','م':'♥','ن':'♣','س':'♠','ع':'●',
    'ف':'○','ص':'◐','ق':'◑','ر':'◒','ش':'◓','ت':'◔','ث':'◕',
    'خ':'☉','ض':'❋','ظ':'✦','غ':'✧','ذ':'✩',
}

def bird_script(text: str) -> str:
    """يحوّل النص العربي إلى رموز أقلام الطيور الهندسية من شمس المعارف"""
    return ''.join(BIRD_MAP.get(ch, ch) for ch in (text or ''))

def bird_script_grid(text: str) -> dict:
    """يرجع النص الأصلي والمحوَّل معاً مع الجدول"""
    encoded = bird_script(text)
    return {
        'original': text,
        'encoded':  encoded,
        'pairs':    [{'char': c, 'symbol': BIRD_MAP.get(c, c)} for c in text],
    }
