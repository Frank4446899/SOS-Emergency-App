
# SOS Emergency (Kivy + Buildozer)
هذا مشروع جاهز لبناء تطبيق أندرويد (APK) لمسار الطريقة B.

## المتطلبات
- Linux / WSL
- Python 3.10+
- Kivy
- Buildozer

## الأوامر
```bash
pip install kivy buildozer Cython
cd sos_kivy_buildozer
buildozer -v android debug
```
الملف الناتج في مجلد `bin/`.

## ملاحظات
- النسخة الحالية تلتقط **صورة ثابتة** بدل الفيديو لتسهيل البناء على Kivy. (نقدر نضيف تسجيل فيديو لاحقًا عبر MediaRecorder وSurfaceView بـ pyjnius)
- التسجيل الصوتي يعمل على أندرويد فقط (MediaRecorder).
- الإعدادات تُحفظ في `config.json` داخل نفس المسار.
- إرسال Gmail يحتاج **App Password**.
- تيليجرام يحتاج **Bot Token + Chat ID**.
