# -*- coding: utf-8 -*-
"""
symbolic_engine.py — محرك الترميز الرمزي
═══════════════════════════════════════════════════════════════════
يحوّل النص إلى توقيع ثنائي 16-bit + seed + weight.
يُستخدم كثاني خطوة في Intent-Driven Pipeline.
═══════════════════════════════════════════════════════════════════
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

ABJAD_VALUES = {
    'ا':1,'أ':1,'إ':1,'آ':1,'ب':2,'ج':3,'د':4,'ه':5,'ة':5,
    'و':6,'ز':7,'ح':8,'ط':9,'ي':10,'ى':10,'ك':20,'ل':30,
    'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,'ق':100,
    'ر':200,'ش':300,'ت':400,'ث':500,'خ':600,'ذ':700,
    'ض':800,'ظ':900,'غ':1000,
}

# ============================================================================
# دوال مساعدة
# ============================================================================

def calculate_abjad(text: str) -> int:
    return sum(ABJAD_VALUES.get(ch, 0) for ch in (text or ''))


def get_text_hash(text: str) -> int:
    if not text:
        return 0
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 1_000_000_000


def get_timing() -> Tuple[int, int, int, int]:
    now = datetime.now()
    return now.hour, now.minute, now.second, now.microsecond // 1000


def combine_to_seed(abjad: int, hash_val: int, length: int,
                    hour: int, minute: int, second: int, ms: int) -> int:
    seed = (
        (abjad   * 1_000_003) ^
        (hash_val* 1_000_033) ^
        (length  * 10_007)    ^
        (hour    * 1_009)     ^
        (minute  * 101)       ^
        (second  * 31)        ^
        (ms      * 7)
    )
    return abs(seed) % 1_000_000_000


def seed_to_signature(seed: int, bits: int = 16) -> List[int]:
    sig = [(seed >> i) & 1 for i in range(bits)]
    while len(sig) < bits:
        sig.append(0)
    return sig[:bits]


def calculate_weight(abjad: int, length: int, seed: int) -> float:
    raw = (abjad % 1000) + (length * 10) + (seed % 1000)
    return round((raw % 1000) / 1000.0, 4)

# ============================================================================
# الدوال الرئيسية
# ============================================================================

def encode_text(text: str, include_timing: bool = True,
                custom_timing: Optional[Tuple[int,int,int,int]] = None) -> Dict:
    text = text or ''
    abjad_val = calculate_abjad(text)
    hash_val  = get_text_hash(text)
    length    = len(text)

    if include_timing:
        hour, minute, second, ms = custom_timing if custom_timing else get_timing()
    else:
        hour = minute = second = ms = 0

    seed      = combine_to_seed(abjad_val, hash_val, length, hour, minute, second, ms)
    signature = seed_to_signature(seed)
    weight    = calculate_weight(abjad_val, length, seed)

    return {
        "abjad":            abjad_val,
        "hash":             hash_val,
        "length":           length,
        "timing":           {"hour": hour, "minute": minute, "second": second, "ms": ms},
        "seed":             seed,
        "signature":        signature,
        "signature_binary": ''.join(str(b) for b in signature),
        "weight":           weight,
    }


def encode_user_data(name: str, mother: str, intent_text: str = '',
                     include_timing: bool = True) -> Dict:
    combined = f"{name} {mother} {intent_text}".strip()
    return encode_text(combined, include_timing=include_timing)


if __name__ == "__main__":
    r = encode_user_data("محمد", "فاطمة", "أريد محبة")
    print(f"seed={r['seed']}  weight={r['weight']}")
    print(f"sig={r['signature_binary']}")
