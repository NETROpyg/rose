from telethon import TelegramClient, events, Button
import requests
import tempfile
from collections import defaultdict

API_ID = 23988357
API_HASH = '25bee10ac433f3dc16a2c0d78bb579de'

client = TelegramClient('my_session', API_ID, API_HASH).start()

FAST_API_URL = "http://sii3.moayman.top/api/gpt.php"
DEEP_API_URL = "https://sii3.moayman.top/api/black.php"
IMG_API_URL = "http://sii3.moayman.top/api/img.php?halagpt-7-i="
VOICE_API_URL = "http://sii3.moayman.top/DARK/voice.php"

ADMIN_ID = 7373751354

user_states = defaultdict(lambda: {
    'mode': 'fast',
    'fast_model': 'searchgpt',
    'deep_model': 'blackbox'
})

allowed_chats = set()
allowed_users = set()  # المستخدمين اللي مفعلين البوت بالخاص

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.is_channel and not event.is_group:
        return

    if event.is_private:
        user_states[event.sender_id] = {
            'mode': 'fast', 'fast_model': 'searchgpt', 'deep_model': 'blackbox'
        }
        msg = "**أهلين وسهلين في بوت netro_gz**\n\n"
        msg += "ابعتلي شو بدك أو جرّب الأوامر هدول:\n"
        msg += "`/img` — لعمل صورة من كلامك\n"
        msg += "`/text` — بحوّل الكلام لصوت\n"
        msg += "`.تكلم` — لتفعيل البوت في الخاص\n"
        msg += "`.اخرس` — لإسكاته"
        buttons = [[Button.url("netro_gz", "https://t.me/python_gaza")]]
        await event.respond(msg, buttons=buttons)

@client.on(events.NewMessage(pattern=r'^\.احكي$'))
async def enable_group(event):
    if event.is_channel and not event.is_group:
        return

    if event.is_group:
        perms = await event.client.get_permissions(event.chat_id, event.sender_id)
        if perms.is_admin:
            allowed_chats.add(event.chat_id)
            await event.reply("✅ تمام! فعلت البوت هون بالمجموعة.")
        else:
            await event.reply("❌ بس المشرفين بقدرو يفعلوه.")

@client.on(events.NewMessage(pattern=r'^\.اطفي$'))
async def disable_group(event):
    if event.is_channel and not event.is_group:
        return

    if event.is_group:
        perms = await event.client.get_permissions(event.chat_id, event.sender_id)
        if perms.is_admin:
            allowed_chats.discard(event.chat_id)
            await event.reply("⛔️ طفيت البوت من المجموعة.")
        else:
            await event.reply("❌ بس المشرفين بقدرو يطفوه.")

@client.on(events.NewMessage(pattern=r'^\.تكلم$'))
async def enable_private(event):
    if event.is_private:
        allowed_users.add(event.sender_id)
        await event.reply("✅ تمام! فعلت البوت بالخاص.")

@client.on(events.NewMessage(pattern=r'^\.اخرس$'))
async def disable_private(event):
    if event.is_private:
        allowed_users.discard(event.sender_id)
        await event.reply("⛔️ أوك، سكّت البوت بالخاص.")

@client.on(events.NewMessage(pattern=r'^/img (.+)'))
async def handle_image(event):
    if event.is_channel and not event.is_group:
        return

    prompt = event.pattern_match.group(1).strip()
    await event.reply("🎨 بستنى شوي، عم بجهزلك الصورة ...")
    try:
        response = requests.get(f"{IMG_API_URL}{prompt}", timeout=60)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                f.write(response.content)
                f.flush()
                await event.reply(file=f.name, force_document=False)
        else:
            await event.reply("❌ ما قدرت أعمل الصورة، جرّب كمان مرة.")
    except Exception as e:
        await event.reply(f"⚠️ صار خطأ وقت توليد الصورة: {e}")

@client.on(events.NewMessage(pattern=r'^/text (.+)'))
async def handle_text_to_voice(event):
    if event.is_channel and not event.is_group:
        return

    text = event.pattern_match.group(1).strip()
    await event.reply("🔊 لحظة شوي، بحوّل الكلام لصوت MP3 ...")
    try:
        response = requests.get(f"{VOICE_API_URL}?text={text}", timeout=60)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(response.content)
                f.flush()
                await event.reply(file=f.name, voice_note=False)
        else:
            await event.reply("❌ ما قدرت أعمل الصوت، جرّب مرة تانية.")
    except Exception as e:
        await event.reply(f"⚠️ صار خطأ وقت تحويل النص لصوت: {e}")

@client.on(events.NewMessage)
async def handle_normal(event):
    if event.is_channel and not event.is_group:
        return

    user_id = event.sender_id

    if event.is_group and event.chat_id not in allowed_chats:
        return

    if event.is_private and user_id not in allowed_users:
        return

    if event.text.startswith('/') or event.text.startswith('.'):
        return

    state = user_states[user_id]
    mode = state['mode']
    model = state['fast_model'] if mode == 'fast' else state['deep_model']
    prompt = f"رد باللهجة الفلسطينية على: {event.text}"

    try:
        await event.respond("⏳ لحظة شوي، خليني أشوف شو بقدر أجاوبك ...")
        if mode == 'fast':
            res = requests.get(FAST_API_URL, params={model: prompt}, timeout=60).json()
            reply = res.get("reply", "❌ ما لقيت رد.")
        else:
            res = requests.post(DEEP_API_URL, data={model: prompt}, timeout=90).json()
            reply = res.get("response", "❌ ما لقيت رد.")
        await event.respond(reply)
    except Exception as e:
        await event.respond(f"⚠️ صار خطأ: {e}")

client.start()
print("🤖 البوت اشتغل... ")
client.run_until_disconnected()