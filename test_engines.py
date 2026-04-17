#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_engines.py — اختبار متكامل لجميع محركات شمس المعارف
"""

def test_all():
    print("=" * 60)
    print("اختبار محركات شمس المعارف الكبرى v11.0")
    print("=" * 60)

    from intent_engine     import analyze_intent
    from symbolic_engine   import encode_user_data
    from matrix_engine     import process_matrix
    from king_engine       import get_king_for_intent
    from path_engine       import resolve_path
    from astro_gatekeeper  import astro_gatekeeper
    from elemental_balance import analyze_user_balance

    data = {"name": "محمد", "mother": "فاطمة", "intent": "أريد أن يحبني الناس"}

    # 1. Intent
    ir = analyze_intent(data["intent"])
    print(f"\n1. Intent Engine:      {ir['intent_type']} (شدة={ir['intensity']} وضوح={ir['clarity']})")

    # 2. Symbolic
    sym = encode_user_data(data["name"], data["mother"], data["intent"])
    print(f"2. Symbolic Engine:    seed={sym['seed']}  weight={sym['weight']}")

    # 3. Matrix
    mx = process_matrix(sym['signature'])
    si = mx['state_info']
    print(f"3. Matrix Engine:      state={si['state']}  stability={si['stability_score']}")

    # 4. Path
    pr = resolve_path(ir, si['state'])
    print(f"4. Path System:        {pr['path']['name']} ({pr['path']['name_en']})")

    # 5. Gatekeeper
    gk = astro_gatekeeper(ir['intent_type'], pr['path']['name_en'].lower())
    print(f"5. Astro Gatekeeper:   {'✅ Granted' if gk['granted'] else '❌ Rejected'} | {gk['reason'][:60]}")

    # 6. Elemental
    eb = analyze_user_balance(data["name"], data["mother"])
    print(f"6. Elemental Balance:  dom={eb['combined_dominant']} conflict={eb['conflict_detected']} mediator={eb['mediator_letter']}")

    # 7. King
    king = get_king_for_intent(ir['intent_type'], sym['weight'], si['state'])
    print(f"7. King Engine:        {king['king_name']} | {king['upper_king']} | {king['planet']}")

    print("\n✅ جميع المحركات تعمل.")

if __name__ == "__main__":
    test_all()
