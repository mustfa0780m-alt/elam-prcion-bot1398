# حقوق النشر (C) 2020-2021 المؤلفون
#
# مرخص بموجب رخصة Raphielscape Public License، النسخة 1.d ("الرخصة")
# لا يمكنك استخدام هذا الملف إلا وفقًا للشروط الواردة في الرخصة.
#
# هذا السكربت لا يقوم بتشغيل Paperplane، بل يقوم بإنشاء جلسة مستخدم Telegram.
#

from telethon import TelegramClient

print(
    """يرجى الذهاب إلى my.telegram.org، تسجيل الدخول باستخدام حسابك على Telegram،
ثم الانتقال إلى أدوات تطوير التطبيقات (API Development Tools) وإنشاء تطبيق جديد،
مع إدخال البيانات المطلوبة.
احصل على 'App api_id' و 'App api_hash'.
API_KEY هو api_id و API_HASH هو api_hash. قم بتسجيلهما أدناه عند الطلب."""
)

# استلام بيانات API من المستخدم
API_KEY = input("أدخل API_KEY: ")
API_HASH = input("أدخل API_HASH: ")

# إنشاء جلسة مستخدم وحفظها في ملف
with TelegramClient("userbot", API_KEY, API_HASH) as client:
    print("تم إنشاء ملف الجلسة 'userbot.session' بنجاح! سيتم الإغلاق الآن.")
