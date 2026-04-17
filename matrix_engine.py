# -*- coding: utf-8 -*-
"""
matrix_engine.py — محرك المصفوفة والكيمياء الرمزية
═══════════════════════════════════════════════════════════════════
يبني مصفوفة 4×4 من التوقيع الثنائي ويُطبّق عليها
عمليات XOR / AND / flip لتوليد حالة النظام.
═══════════════════════════════════════════════════════════════════
"""

from typing import Dict, List

# ============================================================================
# بناء المصفوفة
# ============================================================================

def signature_to_grid(sig: List[int]) -> List[List[int]]:
    sig = (sig + [0]*16)[:16]
    return [sig[i:i+4] for i in range(0, 16, 4)]


def grid_to_signature(grid: List[List[int]]) -> List[int]:
    return [cell for row in grid for cell in row]

# ============================================================================
# الكيمياء الرمزية
# ============================================================================

def horizontal_interaction(grid: List[List[int]]) -> List[List[int]]:
    g = [row[:] for row in grid]
    for i in range(4):
        for j in range(3):
            g[i][j] = grid[i][j] ^ grid[i][j+1]
    return g


def vertical_interaction(grid: List[List[int]]) -> List[List[int]]:
    g = [row[:] for row in grid]
    for i in range(3):
        for j in range(4):
            g[i][j] = grid[i][j] ^ grid[i+1][j]
    return g


def diagonal_interaction(grid: List[List[int]]) -> List[List[int]]:
    g = [row[:] for row in grid]
    for i in range(3):
        g[i][i]   = grid[i][i]   ^ grid[i+1][i+1]
        g[i][3-i] = grid[i][3-i] ^ grid[i+1][2-i]
    return g


def compute_final_state(orig, horiz, vert, diag) -> List[List[int]]:
    final = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            final[i][j] = horiz[i][j] & vert[i][j] & diag[i][j]
    return final

# ============================================================================
# كشف الحالة
# ============================================================================

def detect_state(original: List[List[int]], final: List[List[int]]) -> Dict:
    changes = sum(
        original[i][j] != final[i][j]
        for i in range(4) for j in range(4)
    )
    stability = round(1 - changes / 16, 3)
    if stability > 0.7:
        state = "stable"
    elif stability < 0.3:
        state = "conflict"
    else:
        state = "repetition"
    return {
        "state":           state,
        "stability_score": stability,
        "changes_count":   changes,
        "changes_ratio":   round(changes / 16, 3),
    }

# ============================================================================
# الدالة الرئيسية
# ============================================================================

STATE_MESSAGES = {
    "stable":     "المصفوفة مستقرة — الطريق مفتوح. لا توجد مقاومة داخلية كبيرة.",
    "conflict":   "صراع طاقي مكتشف — مقاومة داخلية. يُنصح بحرف الميزان أو تغيير الوقت.",
    "repetition": "نمط متكرر — النظام يعيد نفسه. قد تحتاج لكسر الدورة بتغيير النية.",
}


def process_matrix(signature: List[int]) -> Dict:
    if len(signature) != 16:
        signature = (signature + [0]*16)[:16]

    original = signature_to_grid(signature)
    parents  = [cell for row in original[:2] for cell in row]
    children = [cell for row in original[2:] for cell in row]

    horiz  = horizontal_interaction(original)
    vert   = vertical_interaction(original)
    diag   = diagonal_interaction(original)
    final  = compute_final_state(original, horiz, vert, diag)

    state_info = detect_state(original, final)

    return {
        "original_grid":     original,
        "original_signature":signature,
        "parents":           parents,
        "children":          children,
        "final_grid":        final,
        "final_signature":   grid_to_signature(final),
        "state_info":        state_info,
        "summary":           STATE_MESSAGES.get(state_info["state"], ""),
    }


if __name__ == "__main__":
    import random
    sig = [random.randint(0,1) for _ in range(16)]
    r = process_matrix(sig)
    print(f"State: {r['state_info']['state']}  stability={r['state_info']['stability_score']}")
    print(f"Summary: {r['summary']}")
