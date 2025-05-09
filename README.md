# وكيل استراتيجية المحتوى (Content Strategist Agent)

هذا التطبيق عبارة عن وكيل ذكي متخصص في استراتيجية المحتوى، يقوم بإنشاء خطة محتوى شاملة لمدة 30 يومًا بناءً على النيتش (المجال) الذي تقوم بإدخاله.

## المميزات

- إنشاء جدول نشر لمدة 30 يومًا (Post Calendar)، بمعدل منشور يومي
- لكل يوم يتم إنشاء:
  - موضوع مناسب للجمهور المستهدف
  - عنوان جذاب للمنشور
  - وصف SEO احترافي (Meta Description) لا يتجاوز 160 حرفًا
  - 5 هاشتاغات مناسبة وشائعة لزيادة الوصول
- المواضيع مترابطة ومتسلسلة لبناء اهتمام تدريجي
- تنوع في المحتوى (نصائح، معلومات، أسئلة، اقتباسات، إلخ)

## كيفية الاستخدام

### استخدام النسخة النصية (Terminal)

1. قم بتشغيل الملف `app.py`:
   ```
   python app.py
   ```

2. أدخل اسم المشروع أو النيتش (المجال) عندما يُطلب منك ذلك

3. سيقوم التطبيق بإنشاء خطة محتوى لمدة 30 يومًا وتصديرها إلى ملف JSON

### استخدام واجهة الويب

1. قم بتشغيل الملف `web_app.py`:
   ```
   python web_app.py
   ```

2. افتح المتصفح على الرابط: `http://localhost:5000`

3. أدخل اسم المشروع أو النيتش في النموذج واضغط على زر "إنشاء خطة المحتوى"

4. سيتم عرض خطة المحتوى في المتصفح مع إمكانية تصديرها إلى ملف JSON

## المخرجات

يقوم التطبيق بإنشاء ملف JSON يحتوي على خطة المحتوى لمدة 30 يومًا، حيث يتضمن كل يوم المعلومات التالية:

- رقم اليوم والتاريخ
- الموضوع ونوع المحتوى
- العنوان الجذاب
- وصف SEO
- الهاشتاغات المقترحة

## المتطلبات

- Python 3.6 أو أحدث
- للواجهة الويب: Flask

## التثبيت

```
pip install flask
```

## الترخيص

هذا المشروع متاح تحت رخصة MIT.