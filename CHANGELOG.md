# شمس المعارف الكبرى — سجل التغييرات

---

## v19 — الإصدار التاسع عشر (الحالي)

### الدمج الشامل (v17 + v18)
- دمج كامل لكود v17 المختبر مع إضافات v18
- صفر خسائر في الخصائص أو الوظائف
- مراجعة كاملة لجميع الأكواد

### محركات جديدة مضافة
- `engines/alchemy_engine.py` — الكيمياء الروحانية الكاملة (معادن/مراحل/وصفات/إكسير)
- `engines/symia_engine.py` — السيميا والخنفطريات (11 مقالة كاملة)
- `engines/abjad_calculator.py` — حساب الجمل المستقل
- `engines/time_engine.py` — محرك التوقيت الفلكي المستقل
- `engines/zairja_engine.py` — Bridge module للزايرجة
- `engines/jafr_engine.py` — Bridge module للجفر
- `engines/geomancy_engine.py` — Bridge module + GeomancyEngine class
- `engines/wafq_generator.py` — Bridge module للأوفاق

### قاعدة المعرفة الموسعة
- 18 Python module جديد في `knowledge/`
- الحروف: 28 حرف بالاستخدامات التفصيلية والخلوات والمواد
- الأسماء الحسنى: 99 اسم مع الأوفاق والطقوس والملائكة
- الكواكب: بيانات موسعة مع البخور والساعات والطبائع
- البروج: 12 برج مع الأعضاء والبلدان والحيوانات
- المنازل القمرية: 28 منزل
- الأعراش والحجب والأمهات والأبواب والملوك

### ميزات جديدة في v19
- **نظام الاقتراح الذكي**: `GET /api/time/suggest` — يحلل اللحظة ويقترح الأعمال
- **فحص النية**: `POST /api/time/suggest_for` — أفضل وقت لأي نية
- **الجفر التاريخي**: `POST /api/jafr/historical` — ملوك/فتن/مدن
- **الزايرجة المركزية**: `POST /api/zairja/center`
- **لوح الرمل الكامل**: `POST /api/geomancy/full_chart`
- **5 APIs للكيمياء**: metal/stages/recipes/balance/elixir
- **5 APIs للسيميا**: articles/article/ritual/khunfutriyyat/barhatiya
- **قاعدة المعرفة**: 10+ APIs جديدة في `/api/v19/knowledge/`

### تحسينات الواجهة
- **القائمة العلوية**: Horizontal scrolling بالماوس والتتبع باللمس
- **نظام الوقت**: Panel محدث بالكامل مع اقتراح ذكي وفحص النية
- **v19 في كل مكان**: تحديث شامل لمعرف الإصدار

### البنية
- `Start.bat` احترافي (English only, no Arabic encoding issues)
- `requirements.txt` مدمج (Flask + FastAPI + Skyfield + Pillow)
- `README.md` شامل بالعربية

---

## v17 — الإصدار السابع عشر (قاعدة v19)

- Core Engine + Rule Engine + Knowledge Base من مخطوطة البوني
- 113 API endpoint
- Skyfield للحسابات الفلكية الدقيقة
- Thread-safe في كل العمليات
- Rate limiting و caching
- Soul Engine (الفراغ) — نظام التقدم الخفي

---

## v18 — الإضافات (مدمجة في v19)

- engines/ folder مع محركات جديدة
- knowledge/ folder مع قاعدة بيانات Python
- FastAPI secondary API
- نماذج OOP (Letter, DivineName)
- templates/ HTML جديدة
