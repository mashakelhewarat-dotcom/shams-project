# -*- coding: utf-8 -*-
"""
license_manager.py — v11.0
═══════════════════════════════════════════════════════════════════
بروتوكولات السيادة والحماية الرباعية
المصدر: شمس المعارف الكبرى + مبادئ الأمن السيبراني

✦ يشمل:
  1. الخلوة الرقمية (Digital Khulwa — Environment Isolation)
  2. بروتوكول الصلاحيات (Hardware ID Locking)
  3. العزل الرقمي (Anti-debug / Anti-VM)
  4. مفتاح التدمير الذاتي (Israf Kill-Switch)
  5. العهد القديم (Root Authorization Protocol)
  6. خاتم الإغلاق (Session Sealing)

⚠️ هذا الملف يُشغَّل في بداية التطبيق — لا تُعدَّل منطقه.
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import hashlib
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============================================================================
# 1. الخلوة الرقمية — Environment Isolation Check
# المصدر: شمس المعارف، فصل الرياضات — "الخلوة بيت الحكمة"
# ============================================================================

def check_digital_khulwa(strict: bool = False) -> dict:
    """
    ✦ الخلوة الرقمية — فحص بيئة التشغيل
    ══════════════════════════════════════
    البوني: "الروحانية لا تنزل في مكان مشحون بصور الغفلة"
    برمجياً: فحص أدوات المراقبة والتصحيح قبل بدء الجلسة.

    المخرج:
      pure:     True إذا كانت البيئة نظيفة
      warnings: قائمة بالمشاكل المكتشفة
      log:      نص السجل
    """
    warnings = []
    checks   = {}

    # ── فحص الـ Debugger ──────────────────────────────────────
    try:
        if sys.gettrace() is not None:
            warnings.append("⚡ DEBUGGER_DETECTED: مصحح أوامر نشط — جلسة غير نظيفة")
            checks['debugger'] = False
        else:
            checks['debugger'] = True
    except Exception:
        checks['debugger'] = True

    # ── فحص بيئة الـ VM (اختياري) ─────────────────────────────
    vm_indicators = []
    try:
        cpu_info = platform.processor().lower()
        if any(x in cpu_info for x in ['vmware', 'virtualbox', 'qemu', 'hyperv']):
            vm_indicators.append(cpu_info)
    except Exception:
        pass

    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SOFTWARE\\VMware, Inc.\\VMware Tools'],
                capture_output=True, timeout=2
            )
            if result.returncode == 0:
                vm_indicators.append('vmware_registry')
    except Exception:
        pass

    if vm_indicators:
        checks['vm'] = False
        if strict:
            warnings.append(f"🔍 VM_ENVIRONMENT: بيئة افتراضية مشتبه بها — {', '.join(vm_indicators)}")
    else:
        checks['vm'] = True

    # ── فحص أدوات المراقبة (Windows) ──────────────────────────
    suspicious_procs = [
        'wireshark', 'fiddler', 'charles', 'burpsuite',
        'ida64', 'x64dbg', 'ollydbg', 'procmon', 'processhacker'
    ]
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                ['tasklist'], capture_output=True, text=True, timeout=3
            )
            running = result.stdout.lower()
            found = [p for p in suspicious_procs if p in running]
            if found:
                checks['monitoring'] = False
                if strict:
                    warnings.append(f"🔍 MONITORING_TOOLS: أدوات مراقبة مكتشفة — {', '.join(found)}")
            else:
                checks['monitoring'] = True
        else:
            checks['monitoring'] = True
    except Exception:
        checks['monitoring'] = True

    # ── تقييم البيئة ──────────────────────────────────────────
    is_pure = checks.get('debugger', True) and (
        not strict or (checks.get('vm', True) and checks.get('monitoring', True))
    )

    status_text = (
        "[Environment] Digital Khulwa: PURE — No interference detected."
        if is_pure else
        "[Environment] Digital Khulwa: CONTAMINATED — Suspicious environment."
    )

    return {
        'pure':      is_pure,
        'checks':    checks,
        'warnings':  warnings,
        'log':       status_text,
        'timestamp': datetime.now().isoformat(),
    }


# ============================================================================
# 2. بروتوكول الصلاحيات — Hardware ID Locking
# "العهد القديم" هو ما يدي الصلاحية للمشغل
# ============================================================================

def get_hardware_id() -> str:
    """
    استخراج معرّف الجهاز الفريد (Hardware Fingerprint).
    يجمع: MAC Address + CPU ID + OS Name → SHA256
    """
    components = []

    # MAC Address
    try:
        import uuid
        components.append(str(uuid.getnode()))
    except Exception:
        components.append('no_mac')

    # Platform info
    try:
        components.append(platform.node())
        components.append(platform.machine())
        components.append(platform.system())
        components.append(platform.version()[:30])
    except Exception:
        components.append('no_platform')

    # CPU info
    try:
        components.append(platform.processor()[:30])
    except Exception:
        components.append('no_cpu')

    fingerprint = '_'.join(components)
    return hashlib.sha256(fingerprint.encode('utf-8', errors='ignore')).hexdigest()[:32]


LICENSE_FILE = Path(__file__).parent / 'license.json'

def generate_license(hardware_id: str, owner_name: str = 'المرخص له') -> dict:
    """
    إنشاء ملف ترخيص مرتبط بالجهاز.
    يُستخدم مرة واحدة عند التثبيت الأول.
    """
    license_data = {
        'hardware_id':  hardware_id,
        'owner':        owner_name,
        'issued_at':    datetime.now().isoformat(),
        'version':      'v11.0',
        'product':      'SWALLOW THE SUN — شمس المعارف الكبرى',
        'checksum':     hashlib.md5(
            f"{hardware_id}{owner_name}SHAMS_MAARIF".encode()
        ).hexdigest(),
        'ahd_seal':     'بسم الله — العهد القديم محفوظ — خاتم سليمان',
    }
    with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(license_data, f, ensure_ascii=False, indent=2)
    return license_data


def verify_license() -> dict:
    """
    فحص الترخيص عند بدء التشغيل.
    يقارن hardware_id المخزّن مع الجهاز الحالي.
    """
    if not LICENSE_FILE.exists():
        return {
            'valid':   False,
            'reason':  'NO_LICENSE: لا يوجد ترخيص — يرجى التثبيت أولاً.',
            'action':  'GENERATE_LICENSE',
        }

    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            stored = json.load(f)
    except Exception:
        return {
            'valid':  False,
            'reason': 'CORRUPT_LICENSE: ملف الترخيص تالف أو معبوث به.',
            'action': 'ISRAF_PROTOCOL',
        }

    current_hw = get_hardware_id()
    stored_hw  = stored.get('hardware_id', '')

    # فحص الـ checksum
    expected_checksum = hashlib.md5(
        f"{stored_hw}{stored.get('owner','')}{'' if stored_hw else ''}SHAMS_MAARIF".encode()
    ).hexdigest()

    if stored_hw != current_hw:
        return {
            'valid':      False,
            'reason':     'HARDWARE_MISMATCH: هذا الترخيص مرتبط بجهاز مختلف.',
            'action':     'ACCESS_DENIED',
            'current_hw': current_hw,
            'stored_hw':  stored_hw,
        }

    if stored.get('checksum') != expected_checksum:
        return {
            'valid':  False,
            'reason': 'CHECKSUM_INVALID: تلاعب في ملف الترخيص — بروتوكول الإصراف.',
            'action': 'ISRAF_PROTOCOL',
        }

    return {
        'valid':     True,
        'owner':     stored.get('owner', ''),
        'version':   stored.get('version', ''),
        'issued_at': stored.get('issued_at', ''),
        'log':       f"[Auth] Solomonic Ahd Verified. Owner: {stored.get('owner','')}. Hardware: OK.",
    }


# ============================================================================
# 3. مفتاح التدمير الذاتي — Israf Kill-Switch
# "إذا أُفسد العمل، بيتم حرقه" — البوني
# ============================================================================

def israf_protocol(reason: str = 'TAMPERING_DETECTED') -> dict:
    """
    ✦ بروتوكول الإصراف — Anti-Tamper Response
    ═══════════════════════════════════════════
    إذا اكتُشف عبث بالملفات أو تلاعب بالترخيص:
    1. مسح session data
    2. تشويش license.json
    3. تسجيل حدث الاختراق
    4. رفض أي طلب جديد

    ⚠️ لا يمسح البيانات الأساسية — فقط الجلسة والترخيص.
    """
    log_entry = {
        'event':     'ISRAF_PROTOCOL_TRIGGERED',
        'reason':    reason,
        'timestamp': datetime.now().isoformat(),
        'hardware':  get_hardware_id(),
    }

    # تشويش ملف الترخيص (لا حذف — فقط invalidate)
    if LICENSE_FILE.exists():
        try:
            corrupt_data = {
                'status':    'INVALIDATED',
                'reason':    reason,
                'timestamp': datetime.now().isoformat(),
                'note':      'تم تفعيل بروتوكول الإصراف — يرجى إعادة التثبيت.',
            }
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(corrupt_data, f, ensure_ascii=False, indent=2)
            log_entry['license_action'] = 'INVALIDATED'
        except Exception as e:
            log_entry['license_error'] = str(e)

    # تسجيل الحدث
    log_file = Path(__file__).parent / 'israf_log.json'
    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-50:], f, ensure_ascii=False, indent=2)  # احتفظ بآخر 50 حدث
    except Exception:
        pass

    return {
        'triggered': True,
        'reason':    reason,
        'message':   (
            "🛑 ISRAF PROTOCOL ACTIVE — "
            "تم رصد محاولة تلاعب. بروتوكول الإصراف فعّال. "
            "يرجى التواصل مع المطور لإعادة التفعيل."
        ),
        'log':       log_entry,
    }


# ============================================================================
# 4. العهد القديم — Root Authorization Injector
# يُحقن في بداية كل عملية حساسة
# ============================================================================

def inject_ahd(operation_name: str, user_name: str = '',
               planet: str = '', intent: str = '') -> dict:
    """
    ✦ حقن العهد القديم في رأس العملية
    ════════════════════════════════════
    يولّد نص تفويض روحاني مخصص لكل عملية.
    يُضاف كـ 'ahd_header' في response الـ API.
    """
    from shams_data_extended import AHD_AL_QADIM, TAHATIL
    now     = datetime.now()
    weekday = (now.weekday() + 2) % 7
    tahatil = TAHATIL.get(weekday, TAHATIL[1])

    personalized = (
        f"{AHD_AL_QADIM['short_form']} — "
        f"العملية: {operation_name} | "
        f"المُشغِّل: {user_name or 'الحكيم'} | "
        f"الكوكب الحاكم: {tahatil['planet']} | "
        f"التهطيل: {tahatil['tahateel']} | "
        f"التوقيت: {now.strftime('%Y-%m-%d %H:%M')}"
    )

    return {
        'ahd_text':    AHD_AL_QADIM['full_text'],
        'ahd_short':   personalized,
        'ahd_seal':    AHD_AL_QADIM['seal'],
        'tahateel':    tahatil['tahateel'],
        'planet':      tahatil['planet'],
        'king_upper':  tahatil['king_upper'],
        'king_lower':  tahatil['king_lower'],
        'day_sigil':   tahatil['sigil'],
        'operation':   operation_name,
        'timestamp':   now.isoformat(),
    }


# ============================================================================
# 5. خاتم الإغلاق — Session Sealing
# يُضاف في نهاية كل عملية كـ Digital Signature
# ============================================================================

def apply_sealing_ring(result: dict, operation_name: str = '') -> dict:
    """
    ✦ تطبيق خاتم الإغلاق على نتيجة العملية
    ══════════════════════════════════════════
    يُضيف:
      - نص خاتم الإغلاق
      - توقيت فلكي
      - hash للتحقق من سلامة النتيجة
    """
    from shams_data_extended import KHATAM_AL_IGHLAQ
    now = datetime.now()

    # hash للتحقق (يستخدم جُمَّل بيانات مختارة)
    data_str = str(result.get('servant_name', '')) + str(result.get('jummal', 0))
    integrity_hash = hashlib.sha256(
        f"{data_str}{now.isoformat()[:16]}SHAMS_SEAL".encode()
    ).hexdigest()[:16]

    seal = {
        'text':           KHATAM_AL_IGHLAQ['text'],
        'code':           KHATAM_AL_IGHLAQ['code'],
        'operation':      operation_name,
        'sealed_at':      now.isoformat(),
        'integrity_hash': integrity_hash,
        'astro_time':     now.strftime('يوم %A الساعة %H:%M — %d/%m/%Y'),
    }

    result['_khatam'] = seal
    return result


# ============================================================================
# 6. Safety Log — رسائل تحذير البوني الدرامية
# "Warning: Atmospheric turbulence detected..."
# ============================================================================

SAFETY_MESSAGES = {
    'forbidden_hour': (
        "⚠️ TEMPORAL_CONFLICT — الساعة الحالية مذمومة في ميزان البوني. "
        "تردد الكوكب الحاكم متعارض مع طلبك. "
        "Re-aligning frequencies... يُنصح بالانتظار أو استخدام باب التحصين."
    ),
    'dark_gate': (
        "⚡ DARK_GATE_DETECTED — هذا الباب ظلماني. "
        "تأكد من الطهارة الكاملة قبل المتابعة. "
        "النظام في وضع Restricted Mode — التصريح محدود."
    ),
    'element_conflict': (
        "🔥💧 ELEMENTAL_COLLISION — تضاد عنصري مكتشف. "
        "إشارة الجمع بين {el1} و{el2} غير مستقرة. "
        "يُنصح بحقن حرف الميزان لضبط التردد."
    ),
    'vm_detected': (
        "🛡️ ENVIRONMENT_ANOMALY — بيئة افتراضية مشتبه بها. "
        "الخلوة الرقمية غير نظيفة. "
        "الروحانية لا تنزل في مكان مشحون بالغفلة — انتظر أو أوقف بيئة الـ VM."
    ),
    'debugger_active': (
        "🔍 SURVEILLANCE_DETECTED — مصحح أوامر نشط. "
        "هذا يعني أن الجلسة تحت المراقبة. "
        "Digital Khulwa Protocol: FAILED — الجلسة غير آمنة."
    ),
    'license_invalid': (
        "🚫 AHD_VIOLATION — الترخيص غير صالح أو مرتبط بجهاز آخر. "
        "العهد القديم غير مُفعَّل. الوصول مرفوض — Access Denied by Solomonic Protocol."
    ),
    'intent_unclear': (
        "⚠️ INTENT_NOISE — النية غير واضحة. "
        "الشك يُفسد العمل في نظام البوني. "
        "Signal Jitter detected — يُنصح بإعادة صياغة طلبك بوضوح."
    ),
    'session_timeout': (
        "⏰ SESSION_EXPIRED — الجلسة انتهت. "
        "لا تترك العمل مفتوحاً — الخدام يحتاجون إلى الصرف. "
        "قراءة الإصراف: 'انصرفوا مأجورين بارك الله فيكم'. "
        "Session auto-terminated to prevent Backfire."
    ),
}


def get_safety_message(msg_type: str, **kwargs) -> str:
    """استرجاع رسالة تحذير البوني الدرامية مع تخصيص."""
    msg = SAFETY_MESSAGES.get(msg_type, "⚠️ UNKNOWN_WARNING — خطأ غير محدد.")
    return msg.format(**kwargs)


# ============================================================================
# 7. التهاطيل + الطلاسم السبعة — Full Binding
# ربط كل طلسم بيومه وكوكبه والتهطيل الخاص به
# ============================================================================

def get_tahateel_for_today() -> dict:
    """استخراج التهطيل الكامل لليوم الحالي."""
    from shams_data_extended import TAHATIL
    now     = datetime.now()
    weekday = (now.weekday() + 2) % 7
    t       = TAHATIL.get(weekday, TAHATIL[1])
    return {
        **t,
        'weekday':  weekday,
        'datetime': now.isoformat(),
        'instruction': (
            f"في يوم {t['day_ar']} (كوكب {t['planet']}): "
            f"انطق التهطيل «{t['tahateel']}» مع إشعال بخور {t['incense']}. "
            f"الملك العلوي: {t['king_upper']} | الملك الأرضي: {t['king_lower']}. "
            f"اتجه نحو الكعبة واحمل أو ضع {t['metal']} أمامك."
        ),
    }


def get_tahateel_for_talisman(king_lower: str) -> Optional[dict]:
    """استخراج التهطيل الخاص بملك معين من اسمه الأرضي."""
    from shams_data_extended import TAHATIL
    for weekday, data in TAHATIL.items():
        if king_lower in data.get('king_lower', ''):
            return {**data, 'weekday': weekday}
    return None


# ============================================================================
# 8. التثبيت الأول — First Run Setup
# ============================================================================

def first_run_setup(owner_name: str = 'الحكيم') -> dict:
    """
    إعداد التطبيق للمرة الأولى:
    1. استخراج Hardware ID
    2. إنشاء ملف الترخيص
    3. فحص البيئة
    """
    hw_id   = get_hardware_id()
    license_data = generate_license(hw_id, owner_name)
    khulwa  = check_digital_khulwa(strict=False)

    return {
        'status':        'INITIALIZED',
        'hardware_id':   hw_id,
        'license':       license_data,
        'khulwa':        khulwa,
        'message':       (
            f"✅ تم تفعيل النظام لصاحبه: {owner_name}. "
            f"Hardware ID: {hw_id[:8]}... "
            f"البيئة: {'نظيفة' if khulwa['pure'] else 'تحتاج مراجعة'}."
        ),
    }


# ============================================================================
# Flask Middleware Helper — يُستخدم في app.py
# ============================================================================

def sovereignty_check(operation: str, strict_license: bool = False) -> dict:
    """
    دالة موحّدة للفحص قبل كل API حساس.
    تُستدعى في بداية /api/process و /api/mandal/summon وغيرها.
    """
    result = {
        'cleared':  True,
        'warnings': [],
        'logs':     [],
        'ahd':      None,
    }

    # 1. الخلوة الرقمية
    khulwa = check_digital_khulwa(strict=False)
    result['logs'].append(khulwa['log'])
    if not khulwa['pure']:
        result['warnings'].extend(khulwa['warnings'])
        if khulwa['checks'].get('debugger') is False:
            result['warnings'].append(get_safety_message('debugger_active'))

    # 2. الترخيص (اختياري حسب البيئة)
    if strict_license:
        lic = verify_license()
        result['logs'].append(lic.get('log', ''))
        if not lic['valid']:
            result['cleared'] = False
            result['warnings'].append(get_safety_message('license_invalid'))
            result['license_action'] = lic.get('action')

    # 3. حقن العهد القديم
    result['ahd'] = inject_ahd(operation)

    return result
