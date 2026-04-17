# -*- coding: utf-8 -*-
"""
wafq_generator.py — شمس المعارف v19
═══════════════════════════════════════════════════════════════════
محرك توليد الأوفاق الديناميكي الكامل المدمج
يدعم: 3×3، 4×4، 5×5، 6×6، 7×7، 8×8، 9×9، 10×10
      خالي الوسط للأبواب الظلمانية
      التحقق من صحة المربع السحري
      تحويل الصورة مباشرة إلى Base64
      توليد الوفق من الأبجد والأسماء الحسنى (V18 Addition)
⚠️ لا تُعدَّل الخوارزميات دون مرجع من المخطوطة.
═══════════════════════════════════════════════════════════════════
"""

import base64
import math
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class WafqGenerator:
    def __init__(self, img_size: int = 500):
        self.img_size     = img_size
        self.bg_color     = (10, 5, 15)
        self.line_color   = (255, 170, 68)
        self.text_color   = (0, 242, 255)
        self.accent_color = (255, 255, 255)
        self.glow_color   = (255, 215, 0)

        if PIL_AVAILABLE:
            for font_path in ["Amiri-Bold.ttf", "DejaVuSans.ttf", "arial.ttf", "arialbd.ttf"]:
                try:
                    self.font_large  = ImageFont.truetype(font_path, 32)
                    self.font_medium = ImageFont.truetype(font_path, 20)
                    self.font_small  = ImageFont.truetype(font_path, 14)
                    break
                except Exception:
                    pass
            else:
                self.font_large  = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small  = ImageFont.load_default()

    # ================================================================
    # 1. الخوارزميات — توليد المصفوفات
    # ================================================================
    def _siamese_square(self, size: int, miftah: int = 1, remainder: int = 0) -> List[List[int]]:
        """⚠️ محمية — السيرة (Siamese) للأحجام الفردية."""
        square = [[0] * size for _ in range(size)]
        r, c = 0, size // 2
        for num in range(1, size * size + 1):
            square[r][c] = num
            nr, nc = (r - 1) % size, (c + 1) % size
            if square[nr][nc] != 0:
                r = (r + 1) % size
            else:
                r, c = nr, nc
        for i in range(size):
            for j in range(size):
                square[i][j] += (miftah - 1)
        if remainder > 0:
            whole_per_cell = remainder // (size * size)
            if whole_per_cell > 0:
                for i in range(size):
                    for j in range(size):
                        square[i][j] += whole_per_cell
        return square

    def _even_4x4(self, miftah: int = 1) -> List[List[int]]:
        """⚠️ محمية — وفق 4×4 القاعدة الكلاسيكية."""
        base = [[16,2,3,13],[5,11,10,8],[9,7,6,12],[4,14,15,1]]
        return [[v + (miftah - 1) for v in row] for row in base]

    def _even_6x6(self, miftah: int = 1) -> List[List[int]]:
        """⚠️ محمية — وفق 6×6 طريقة الأرباع."""
        size = 6
        q = self._siamese_square(3, miftah, 0)
        square = [[0] * size for _ in range(size)]
        for i in range(3):
            for j in range(3):
                square[i][j]     = q[i][j]
                square[i][j+3]   = q[i][j] + 9
                square[i+3][j]   = q[i][j] + 18
                square[i+3][j+3] = q[i][j] + 27
        for i in range(3):
            for j in range(2):
                square[i][j], square[i+3][j] = square[i+3][j], square[i][j]
        return square

    def _even_8x8(self, miftah: int = 1) -> List[List[int]]:
        """⚠️ محمية — وفق 8×8 طريقة توسيع 4×4."""
        q = self._even_4x4(miftah)
        size = 8
        square = [[0] * size for _ in range(size)]
        for i in range(4):
            for j in range(4):
                square[i][j]     = q[i][j]
                square[i][j+4]   = q[i][j] + 16
                square[i+4][j]   = q[i][j] + 32
                square[i+4][j+4] = q[i][j] + 48
        return square

    def _even_10x10(self, miftah: int = 1) -> List[List[int]]:
        """⚠️ محمية — وفق 10×10 (V18 Addition)."""
        base = [
            [1,100,99,2,3,98,97,4,5,96],   [95,6,7,94,93,8,9,92,91,10],
            [11,90,89,12,13,88,87,14,15,86],[85,16,17,84,83,18,19,82,81,20],
            [21,80,79,22,23,78,77,24,25,76],[75,26,27,74,73,28,29,72,71,30],
            [31,70,69,32,33,68,67,34,35,66],[65,36,37,64,63,38,39,62,61,40],
            [41,60,59,42,43,58,57,44,45,56],[55,46,47,54,53,48,49,52,51,50]
        ]
        diff = miftah - base[4][4]
        return [[v + diff for v in row] for row in base]

    def _is_magic_square(self, matrix: List[List[int]]) -> bool:
        """⚠️ إضافة DeepSeek #4 — التحقق من صحة المربع السحري."""
        n = len(matrix)
        if n == 0: return False
        target = sum(matrix[0])
        for row in matrix:
            if sum(row) != target: return False
        for j in range(n):
            if sum(matrix[i][j] for i in range(n)) != target: return False
        if sum(matrix[i][i] for i in range(n)) != target: return False
        if sum(matrix[i][n-1-i] for i in range(n)) != target: return False
        return True

    def compute_miftah_and_remainder(self, total_value: int, wafq_type: str) -> Tuple[int, int]:
        """حساب المفتاح والباقي بحسب حجم الوفق."""
        size_map = {
            'المثلث': 3, 'المربع': 4, 'المخمس': 5,
            'المسدس': 6, 'المسبع': 7, 'المثمن': 8, 'المتسع': 9, 'المعشر': 10
        }
        size = size_map.get(wafq_type, 3)
        cells = size * size
        miftah = total_value // cells
        remainder = total_value % cells
        return max(1, miftah), remainder

    def generate_wafq(
        self,
        wafq_type: str,
        total_value: int,
        top_text: str = '',
        corners: Optional[List[str]] = None,
        hollow_center: bool = False,
    ) -> Optional[str]:
        """توليد الوفق وإرجاعه كـ Base64 PNG."""
        if not PIL_AVAILABLE:
            return None
        size_map = {
            'المثلث': 3, 'المربع': 4, 'المخمس': 5,
            'المسدس': 6, 'المسبع': 7, 'المثمن': 8, 'المتسع': 9, 'المعشر': 10
        }
        size = size_map.get(wafq_type, 3)
        miftah, remainder = self.compute_miftah_and_remainder(total_value, wafq_type)

        if size % 2 == 1:
            matrix = self._siamese_square(size, miftah, remainder)
        elif size == 4:  matrix = self._even_4x4(miftah)
        elif size == 6:  matrix = self._even_6x6(miftah)
        elif size == 8:  matrix = self._even_8x8(miftah)
        elif size == 10: matrix = self._even_10x10(miftah)
        else:            matrix = self._siamese_square(size, miftah, remainder)

        if hollow_center and size >= 3:
            cx = cy = size // 2
            matrix[cx][cy] = 0

        S = self.img_size
        margin = 60
        grid_size = S - 2 * margin
        cell = grid_size / size
        W, H = S, S + 80

        img  = Image.new('RGB', (W, H), self.bg_color)
        draw = ImageDraw.Draw(img)

        # رسم الشبكة
        for i in range(size + 1):
            y = margin + i * cell
            draw.line([(margin, y), (margin + grid_size, y)], fill=self.line_color, width=2)
        for j in range(size + 1):
            x = margin + j * cell
            draw.line([(x, margin), (x, margin + grid_size)], fill=self.line_color, width=2)

        # كتابة الأرقام
        for i in range(size):
            for j in range(size):
                val = matrix[i][j]
                if val == 0: continue
                cx_cell = int(margin + j * cell + cell / 2)
                cy_cell = int(margin + i * cell + cell / 2)
                txt = str(val)
                try:
                    bbox = draw.textbbox((0, 0), txt, font=self.font_medium)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    draw.text((cx_cell - tw//2, cy_cell - th//2), txt,
                              fill=self.text_color, font=self.font_medium)
                except Exception:
                    draw.text((cx_cell - 10, cy_cell - 10), txt, fill=self.text_color)

        # النص العلوي
        if top_text:
            try:
                bbox = draw.textbbox((0, 0), top_text, font=self.font_large)
                tw = bbox[2] - bbox[0]
                draw.text(((W - tw) // 2, H - 70), top_text,
                          fill=self.glow_color, font=self.font_large)
            except Exception:
                draw.text((10, H - 70), top_text, fill=self.glow_color)

        # الزوايا
        if corners:
            positions = [(8, 8), (W-70, 8), (8, H-30), (W-70, H-30)]
            for i, (cx_c, cy_c) in enumerate(positions):
                if i < len(corners) and corners[i]:
                    try:
                        draw.text((cx_c, cy_c), str(corners[i]),
                                  fill=(200, 200, 255), font=self.font_small)
                    except Exception:
                        pass

        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"


# ================================================================
# الدوال المساعدة على مستوى الموديول (V17 + V18 merged)
# ================================================================
def generate_wafq(total_value: int, size: int = 3) -> list:
    """Wrapper يُعيد مصفوفة الوفق لقيمة إجمالية وحجم."""
    size_names = {3:"المثلث", 4:"المربع", 5:"المخمس",
                  6:"المسدس", 7:"المسبع", 8:"المثمن", 9:"المتسع", 10:"المعشر"}
    wafq_type = size_names.get(size, "المثلث")
    gen = WafqGenerator(100)
    miftah, remainder = gen.compute_miftah_and_remainder(total_value, wafq_type)
    if size % 2 == 1:
        return gen._siamese_square(size, miftah, remainder)
    elif size == 4:  return gen._even_4x4(miftah)
    elif size == 6:  return gen._even_6x6(miftah)
    elif size == 8:  return gen._even_8x8(miftah)
    elif size == 10: return gen._even_10x10(miftah)
    return []


def validate_wafq(matrix: list) -> dict:
    """التحقق من صحة الوفق — يتحقق من مجاميع الصفوف والأعمدة والقطر."""
    if not matrix or not matrix[0]:
        return {"valid": False, "target_sum": 0, "errors": ["مصفوفة فارغة"]}
    n = len(matrix)
    target = sum(matrix[0])
    errors = []
    for i, row in enumerate(matrix):
        if sum(row) != target:
            errors.append(f"الصف {i}: {sum(row)} ≠ {target}")
    for j in range(n):
        col = sum(matrix[i][j] for i in range(n))
        if col != target:
            errors.append(f"العمود {j}: {col} ≠ {target}")
    diag1 = sum(matrix[i][i] for i in range(n))
    if diag1 != target: errors.append(f"القطر الرئيسي: {diag1} ≠ {target}")
    diag2 = sum(matrix[i][n-1-i] for i in range(n))
    if diag2 != target: errors.append(f"القطر الثانوي: {diag2} ≠ {target}")
    return {"valid": len(errors) == 0, "target_sum": target, "errors": errors, "size": n}


def generate_wafq_for_name(divine_name: dict) -> Optional[List[List[int]]]:
    """توليد وفق من بيانات الاسم الحسنى (V18 Addition)."""
    size = divine_name.get('wafq_size', 4)
    key  = divine_name.get('wafq_key', divine_name.get('abjad', 1))
    return generate_wafq(key or 1, size)


def get_wafq_sum(size: int, key: int) -> int:
    """حساب مجموع صف الوفق (V18 Addition)."""
    total_cells = size * size
    total_sum   = total_cells * (total_cells + 1) // 2
    return total_sum // size


def generate_empty_center_wafq(size: int, key: int) -> Optional[List]:
    """توليد وفق بمركز فارغ للأبواب الظلمانية (V18 Addition)."""
    wafq = generate_wafq(key, size)
    if wafq and size >= 3:
        center = size // 2
        wafq[center][center] = None
    return wafq


def generate_wafq_from_abjad(abjad: int) -> Dict[str, Any]:
    """توليد وفق تلقائي من قيمة الأبجد (V18 Addition)."""
    size = 3 if abjad % 2 == 1 else 4
    key  = abjad % (size * size) or 1
    wafq = generate_wafq(key, size)
    return {'wafq': wafq, 'size': size, 'key': key, 'sum': get_wafq_sum(size, key)}
