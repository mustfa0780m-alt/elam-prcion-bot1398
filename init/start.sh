#!/usr/bin/env bash
# حقوق النشر (C) 2019-2021 المؤلفون
#
# مرخص بموجب رخصة Raphielscape Public License، النسخة 1.d ("الرخصة")
# لا يمكنك استخدام هذا الملف إلا وفقًا للشروط الواردة في الرخصة.
#

# تشغيل خادم Redis في الخلفية
echo "جاري تشغيل خادم Redis في الخلفية..."
redis-server --daemonize yes

# تشغيل Userbot
echo "جاري تشغيل Userbot..."
python3 -m userbot
