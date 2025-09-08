# -*- coding: utf-8 -*-
import os, json, random, time, hashlib, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timedelta, timezone

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

HISTORY_PATH = Path("history.json")
HISTORY_DAYS = 14
MAX_TRIES = 20

OPENERS = [
    "🔧 یک نکتهٔ سریع:",
    "🏗️ امروز یاد بگیریم:",
    "🧱 ریزدانش کاربردی:",
    "📏 مهندسی در ۲۰ ثانیه:",
    "🪜 یک قدم حرفه‌ای‌تر:",
]

AUDIENCES = [
    ("owners", "👥 مالکین"),
    ("structural", "👷‍♂️ مهندس سازه"),
    ("architect", "🧑‍🎨 مهندس معمار"),
    ("geotech", "⛏️ مهندس ژئوتکنیک"),
    ("developer", "🏢 انبوه‌ساز"),
]
AUDMAP = dict(AUDIENCES)

VOCAB = {
    "owners": {
        "themes": ["قرارداد","زمان‌بندی","کیفیت بتن","صورت‌جلسه","کنترل هزینه","تحویل موقت"],
        "facts": [
            "ابهام در دامنهٔ کار منبع اختلاف جدی است",
            "بدون آزمایش مقاومت، کیفیت بتن قابل استناد نیست",
            "تعهدات پیمانکار باید به Milestone گره بخورد",
            "تحویل موقت بدون چک‌لیست ریسک بالایی دارد",
            "تغییرات کوچک بدون مستند، هزینه‌های بزرگ می‌سازد",
        ],
        "actions": [
            "دامنهٔ کار و خسارت تأخیر را شفاف و مکتوب کن",
            "از هر بچ بتن نمونهٔ فشاری بگیر و ضمیمه کن",
            "زمان‌بندی را با نقاط تحویل عددی کن",
            "چک‌لیست تحویل و مهلت رفع نواقص را درج کن",
            "هر تغییر را با RFI/VO ثبت و تصویب کن",
        ],
        "checks": [
            "خط‌مشی پرداخت‌ها و تضمین‌ها مشخص باشد",
            "رِنج پذیرش مقاومت 7/28 روز درج شود",
            "شاخص‌های عملکردی پیمانکار قابل اندازه‌گیری باشند",
            "ضمانت‌نامه‌ها و بیمه‌نامه‌ها به‌روز باشند",
        ],
        "hashtags": ["قرارداد","مدیریت_پروژه","مالکیت","تحویل","کیفیت","صورتجلسه"],
    },
    "structural": {
        "themes": ["برش پانچ","نامنظمی پیچشی","اتصالات","دیافراگم","دیوار برشی","دریفت"],
        "facts": [
            "اطراف ستون بحرانی‌ترین ناحیهٔ برش در دال تخت است",
            "فاصلهٔ مرکز جرم و سختی باعث پیچش ناخواسته می‌شود",
            "جزئیات اتصال بر رفتار لرزه‌ای غالب است",
            "دیافراگم صلب مسیر بار را یکپارچه می‌کند",
        ],
        "actions": [
            "Stud Rail و ضخامت مؤثر را کنترل کن",
            "چیدمان دیوار برشی را برای تعادل پیچشی بهینه کن",
            "وصله‌ها را از نواحی بحرانی دور نگه دار",
            "مسیرهای باربر را پیوسته طراحی کن",
        ],
        "checks": [
            "ترکیب بار سرویس/نهایی را بازبینی کن",
            "حدود دریفت طبقات در کنترل باشد",
            "شکست ترد اتصال با وصله نامناسب رخ ندهد",
        ],
        "hashtags": ["سازه","تحلیل","برش_پانچ","دیافراگم","دیوار_برشی","اتصالات"],
    },
    "architect": {
        "themes": ["نما","آب‌بندی","پارتیشن","هماهنگی نقشه","جزئیات اجرایی","نورگیری"],
        "facts": [
            "نفوذ آب دشمن اصلی مصالح و اتصالات نماست",
            "بازشوهای ناخواسته مسیرهای باربر را تضعیف می‌کند",
            "جزئیات اجرا کیفیت نهایی را تعیین می‌کند",
        ],
        "actions": [
            "درز انبساط، آب‌چکان و فلاشینگ را دقیق طراحی کن",
            "پارتیشن‌ها را با قاب خمشی/مهاربندی هماهنگ کن",
            "کاور مصالح و jointها را استاندارد کن",
        ],
        "checks": [
            "تخلیهٔ آب باران قابل اتکا باشد",
            "کلیرنس‌های لرزشی و جان‌پناه رعایت شود",
            "تداخل معماری با مسیر باربر رخ ندهد",
        ],
        "hashtags": ["معماری","نما","آب_بندی","هماهنگی_نقشه","جزئیات"],
    },
    "geotech": {
        "themes": ["SPT","CPT","نیلینگ","پایداری گود","تراکم","آب زیرزمینی"],
        "facts": [
            "N خام SPT قابل مقایسه نیست و باید تصحیح شود",
            "آب حفره‌ای می‌تواند پایداری شیب را واژگون کند",
            "تراکم نسبی شن و ماسه کلید رفتار نشست است",
        ],
        "actions": [
            "N60 را با تصحیح انرژی/طول راد/قطر گمانه مبنا بگیر",
            "زهکشی سطحی پشت دیوارهٔ گود را اجرا کن",
            "دانسیته درجا و منحنی تراکم را انطباق بده",
        ],
        "checks": [
            "Pull-out تست مهاری را دوره‌ای انجام بده",
            "پروفیل آب زیرزمینی را به‌روز نگه دار",
            "ایمنی شیب با ضریب کافی کنترل شود",
        ],
        "hashtags": ["ژئوتکنیک","SPT","CPT","نیلینگ","پایدارسازی_گود","تراکم"],
    },
    "developer": {
        "themes": ["تدارکات","زمان‌بندی","کیفیت","تغییرات","ریسک","ایمنی"],
        "facts": [
            "تاخیر حمل باعث افت اسلامپ و دوباره‌کاری می‌شود",
            "تغییرات بدون مستند، برآورد را بی‌اعتبار می‌کند",
            "ریسک‌های HSE باید قبل از اجرا حذف/کاهش یابد",
        ],
        "actions": [
            "تأمین سیمان/سنگدانه و ناوگان حمل را همزمان قفل کن",
            "هر تغییر را با RFI/VO و اثر مالی ثبت کن",
            "برنامهٔ بازرسی و تست را الزامی کن",
        ],
        "checks": [
            "دمای بتن تازه و زمان تا تخلیه محدود باشد",
            "کِیش‌فلو با تغییرات همگام‌سازی شود",
            "شاخص‌های HSE و PPE کنترل گردد",
        ],
        "hashtags": ["انبوه_ساز","تدارکات","زمانبندی","کیفیت","RFI","HSE"],
    },
}

TEMPLATES = [
    "{opener}\n{aud}\n\n{title}\n{fact}. {action}.\n\n{hashtags}",
    "{opener}\n{aud}\n\n{title}\n{action}. {check}.\n\n{hashtags}",
    "{opener}\n{aud}\n\n{title}\n{fact}. {check}.\n\n{hashtags}",
]

def load_history():
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_history(hist):
    HISTORY_PATH.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

def cutoff_ts(days):
    return int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

def in_recent(hist, fp: str, days: int) -> bool:
    t0 = cutoff_ts(days)
    return any(h.get("fp")==fp and h.get("ts",0)>=t0 for h in hist)

def make_fp(txt: str) -> str:
    return hashlib.sha1(txt.strip().encode("utf-8")).hexdigest()

def rotrand(now_ts: int, modulo: int) -> int:
    slot = now_ts // (30*60)  # نیم‌ساعته
    return slot % modulo

def pick_audience(now_ts: int):
    idx = rotrand(now_ts, len(AUDIENCES))
    return AUDIENCES[idx]

def make_hashtags(pool, k=5):
    pool = [p.strip().replace(" ", "_").replace("#", "") for p in pool if p.strip()]
    random.shuffle(pool)
    uniq, seen = [], set()
    for t in pool:
        if t not in seen:
            uniq.append("#"+t); seen.add(t)
        if len(uniq) >= k: break
    return " ".join(uniq)

def generate_tip(now_ts: int, hist: list) -> tuple[str,str,str]:
    key, label = pick_audience(now_ts)
    bag = VOCAB[key]
    opener = random.choice(OPENERS)

    for _ in range(20):
        theme  = random.choice(bag["themes"])
        fact   = random.choice(bag["facts"])
        action = random.choice(bag["actions"])
        check  = random.choice(bag["checks"])
        tpl    = random.choice(TEMPLATES)
        title = random.choice([
            f"{theme} زیر ذره‌بین",
            f"{theme}: یک تصمیم بهتر",
            f"{theme}؛ خطای رایج و راه‌حل",
            f"{theme}: تیپ سریع اجرایی",
        ])
        hashtags = make_hashtags([theme] + bag["hashtags"], k=5)
        fp = make_fp(f"{key}|{title}|{fact}|{action}|{check}")
        if not in_recent(hist, fp, HISTORY_DAYS):
            text = tpl.format(
                opener=opener, aud=label, title=title,
                fact=fact, action=action, check=check, hashtags=hashtags
            ).strip()
            return key, text, fp

    # fallback
    theme = bag["themes"][0]
    text = TEMPLATES[0].format(
        opener=opener, aud=label, title=f"{theme}: یادآوری کوتاه",
        fact=bag["facts"][0], action=bag["actions"][0],
        hashtags=make_hashtags([theme] + bag["hashtags"], k=5), check=bag["checks"][0]
    ).strip()
    fp = make_fp(f"{key}|{theme}|fallback")
    return key, text, fp

def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("BOT_TOKEN یا CHAT_ID ست نشده است.")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

if __name__ == "__main__":
    now = int(time.time())
    history = load_history()
    aud_key, tip_text, tip_fp = generate_tip(now, history)
    send_telegram(tip_text)
    history.append({"ts": int(datetime.now(timezone.utc).timestamp()), "aud": aud_key, "fp": tip_fp})
    t0 = cutoff_ts(HISTORY_DAYS)
    history = [h for h in history if h.get("ts",0) >= t0]
    save_history(history)
    print("SENT:", tip_text[:140].replace("\n"," ") + ("..." if len(tip_text)>140 else ""))
