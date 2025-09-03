# وحدة البوت لإدارة الأحداث.
# أحد المكونات الأساسية للبوت.

import sys
from asyncio import create_subprocess_shell as asyncsubshell
from asyncio import subprocess as asyncsub
from os import remove
from time import gmtime, strftime
from traceback import format_exc

from telethon import events

from userbot import bot, BOTLOG, BOTLOG_CHATID, LOGS
from userbot.modules.dbhelper import get_exclude


def register(**args):
    """تسجيل حدث جديد للبوت."""
    pattern = args.get("pattern")  # نمط الرسالة (Regex)
    disable_edited = args.get("disable_edited", False)  # تجاهل الرسائل المحررة
    ignore_unsafe = args.get("ignore_unsafe", False)  # تجاهل الأنماط غير الآمنة
    unsafe_pattern = r"^[^/!#@\$A-Za-z'\"]"  # نمط غير آمن افتراضي
    group_only = args.get("group_only", False)  # العمل على المجموعات فقط
    disable_errors = args.get("disable_errors", False)  # عدم إرسال سجل الأخطاء
    insecure = args.get("insecure", False)  # تجاهل الأمان للبوتات
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern  # جعل النمط غير حساس لحالة الحروف

    if "disable_edited" in args:
        del args["disable_edited"]

    if "ignore_unsafe" in args:
        del args["ignore_unsafe"]

    if "group_only" in args:
        del args["group_only"]

    if "disable_errors" in args:
        del args["disable_errors"]

    if "insecure" in args:
        del args["insecure"]

    if pattern and not ignore_unsafe:
        args["pattern"] = args["pattern"].replace(r"^.", unsafe_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            # تجاهل الرسائل المحررة في القنوات
            if check.edit_date and check.is_channel and not check.is_group:
                return
            # التأكد من أن الحدث في مجموعة إذا كان مطلوبًا
            if group_only and not check.is_group:
                await check.respond("`هل أنت متأكد أن هذه مجموعة؟`")
                return
            # تجاهل الرسائل الصادرة عبر البوتات
            if check.via_bot_id and not insecure and check.out:
                return
            # تجاهل الرسائل المنسقة (عريض، مائل، إلخ)
            if (check.message.text or "").startswith(("`", "*", "_", "~")):
                return

            try:
                await func(check)  # تنفيذ الدالة الأساسية
            except events.StopPropagation:
                raise events.StopPropagation  # السماح باستمرار StopPropagation
            except KeyboardInterrupt:
                pass  # تجاهل المقاطعة اليدوية
            except BaseException as e:
                await log_error(error=e, event=check, disable_errors=disable_errors)  # تسجيل الأخطاء
            else:
                pass

        if not disable_edited:
            bot.add_event_handler(wrapper, events.MessageEdited(**args))  # تسجيل الرسائل المحررة
        bot.add_event_handler(wrapper, events.NewMessage(**args))  # تسجيل الرسائل الجديدة
        return wrapper

    return decorator


def grp_exclude(force_exclude=False):
    """التحقق إذا كانت المجموعة مستثناة من متابعة البوت."""

    def decorator(func):
        async def wrapper(check):
            exclude = await get_exclude(check.chat_id)  # الحصول على بيانات الاستثناء
            if exclude is not None:
                LOGS.info(func)
                if force_exclude:
                    LOGS.info("مستثناة! force_exclude مفعل")
                    return

                if exclude["excl_type"] == 2:  # استثناء كامل
                    LOGS.info("مستثناة! النوع=2")
                    return

                if exclude["excl_type"] == 1 and check.out is False:  # استثناء للرسائل الواردة فقط
                    LOGS.info("مستثناة! النوع=1 والرسالة واردة")
                    return

                LOGS.info("ليست مستثناة!")
            await func(check)

        return wrapper

    return decorator


async def log_error(error, event, disable_errors=False):
    """تسجيل الأخطاء وإرسالها للقناة المناسبة."""
    LOGS.exception(error)  # تسجيل الخطأ في الكونسول

    if not disable_errors:
        date = strftime("%Y-%m-%d %H:%M:%S", gmtime())  # الحصول على الوقت بالتنسيق العالمي

        text = "**عذراً، واجهت خطأ!**\n"
        link = "[https://t.me/tgpaperplane](Userbot Support Chat)"
        text += "للتبليغ، قم بإعادة توجيه هذه الرسالة إلى " + link + ".\n"
        text += "لن نسجل أي شيء إلا تاريخ ووقت الخطأ.\n"

        ftext = "\nتنويه:\nهذا الملف مُرفع هنا فقط، تم تسجيل تاريخ ووقت الخطأ، نحترم خصوصيتك.\n"
        ftext += "--------بداية سجل أخطاء البوت--------"
        ftext += "\nالتاريخ: " + date
        if event:
            ftext += "\nمعرف المجموعة: " + str(event.chat_id)
            ftext += "\nمعرف المرسل: " + str(event.sender_id)
            ftext += "\n\nنص الرسالة التي أثارت الحدث:\n"
            ftext += str(event.text)
        ftext += "\n\nتفاصيل Traceback:\n"
        ftext += str(format_exc())
        ftext += "\n\nنص الخطأ:\n"
        ftext += str(sys.exc_info()[1])
        ftext += "\n--------نهاية سجل الأخطاء--------"

        command = 'git log --pretty=format:"%an: %s" -5'
        ftext += "\n\nآخر 5 تغييرات في Git:\n"

        process = await asyncsubshell(
            command, stdout=asyncsub.PIPE, stderr=asyncsub.PIPE
        )
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())
        ftext += result

        with open("error.log", "w+") as output_file:
            output_file.write(ftext)

        if BOTLOG:
            await bot.send_file(BOTLOG_CHATID, "error.log", caption=text)
        elif event:
            await bot.send_file(event.chat_id, "error.log", caption=text)

        remove("error.log")  # حذف الملف بعد الإرسال
