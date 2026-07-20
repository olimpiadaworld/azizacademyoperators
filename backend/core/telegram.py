import json
import os
import html
import urllib.parse
import urllib.request
from django.utils import timezone


def _env_list(name):
    raw = os.getenv(name, '') or ''
    return [x.strip() for x in raw.replace(';', ',').split(',') if x.strip()]


def telegram_enabled():
    return bool(os.getenv('TELEGRAM_BOT_TOKEN') and (_env_list('TELEGRAM_CHAT_IDS') or os.getenv('TELEGRAM_CHAT_ID')))


def get_chat_ids():
    ids = []
    main = (os.getenv('TELEGRAM_CHAT_ID') or '').strip()
    if main:
        ids.append(main)
    ids.extend(_env_list('TELEGRAM_CHAT_IDS'))
    # preserve order and remove duplicates
    seen = set()
    result = []
    for chat_id in ids:
        if chat_id not in seen:
            result.append(chat_id)
            seen.add(chat_id)
    return result


def esc(value):
    return html.escape(str(value or '').strip())


def send_telegram_message(text):
    """Send a Telegram message without breaking the main API if Telegram fails."""
    token = (os.getenv('TELEGRAM_BOT_TOKEN') or '').strip()
    chat_ids = get_chat_ids()
    if not token or not chat_ids or not text:
        return {'ok': False, 'skipped': True, 'detail': 'Telegram env to‘ldirilmagan.'}

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    results = []
    for chat_id in chat_ids:
        payload = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text[:3900],
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
                try:
                    results.append(json.loads(body))
                except Exception:
                    results.append({'ok': True, 'raw': body[:200]})
        except Exception as exc:
            results.append({'ok': False, 'chat_id': chat_id, 'error': str(exc)})
    return {'ok': any(r.get('ok') for r in results if isinstance(r, dict)), 'results': results}


def line(label, value):
    if value is None or value == '':
        return ''
    return f'<b>{esc(label)}:</b> {esc(value)}\n'


def lead_info(lead):
    if not lead:
        return ''
    text = ''
    text += line('F.I.O', getattr(lead, 'full_name', ''))
    text += line('Tel 1', getattr(lead, 'phone1', ''))
    text += line('Tel 2', getattr(lead, 'phone2', ''))
    text += line('Tel 3', getattr(lead, 'phone3', ''))
    text += line('T/SH', getattr(lead, 'tsh', ''))
    text += line('Maktab', getattr(lead, 'school', ''))
    text += line('Sinf', getattr(lead, 'grade', ''))
    text += line('Fan', getattr(lead, 'subject', ''))
    text += line('Ball', getattr(lead, 'ball', ''))
    return text


def user_name(user):
    if not user:
        return ''
    return getattr(user, 'full_name', '') or getattr(user, 'username', '') or ''


def now_text():
    return timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
