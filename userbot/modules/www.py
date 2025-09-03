# وحدة أوامر الإنترنت للمستخدم (Userbot)
# مرخصة بموجب Raphielscape Public License 1.d

from datetime import datetime

import speedtest
from telethon import functions

from userbot import CMD_HELP
from userbot.events import register, grp_exclude


@register(outgoing=True, pattern=r"^.speed$")
@grp_exclude()
async def speedtst(spd):
    """أمر .speed: لاختبار سرعة الاتصال بالخادم."""
    await spd.edit("`جارٍ اختبار السرعة...⏳`")
    test = speedtest.Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await spd.edit(
        "`"
        f"بدأ الاختبار في: {result['timestamp']}\n\n"
        f"سرعة التحميل: {speed_convert(result['download'])}\n"
        f"سرعة الرفع: {speed_convert(result['upload'])}\n"
        f"الاستجابة (Ping): {result['ping']}ms\n"
        f"مزود الخدمة (ISP): {result['client']['isp']}"
        "`"
    )


def speed_convert(size):
    """تحويل البايتات إلى Kb/s أو Mb/s أو Gb/s"""
    power = 2**10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@register(outgoing=True, pattern=r"^.nearestdc$")
@grp_exclude()
async def neardc(event):
    """أمر .nearestdc: عرض أقرب مركز بيانات (Data Center) للبوت."""
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(
        f"البلد: `{result.country}`\n"
        f"أقرب مركز بيانات: `{result.nearest_dc}`\n"
        f"هذا المركز: `{result.this_dc}`"
    )


@register(outgoing=True, pattern=r"^.pingme$")
@grp_exclude()
async def pingme(pong):
    """أمر .pingme: اختبار زمن استجابة البوت."""
    start = datetime.now()
    await pong.edit("`Pong! 🏓`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit(f"`Pong! استغرقت {duration}ms`")


# =============================
# تحديث أوامر المساعدة
# =============================
CMD_HELP.update(
    {
        "www": [
            "WWW",
            " - `.speed`: اختبار سرعة الإنترنت وإظهار النتائج.\n"
            " - `.nearestdc`: عرض أقرب مركز بيانات للبوت.\n"
            " - `.pingme`: عرض زمن الاستجابة للبوت.\n",
        ]
    }
  )
