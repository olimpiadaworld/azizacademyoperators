from datetime import datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db.models import Q

STATUS_LABELS = {
    'new': 'Biriktirilgan lead',
    'sale': 'Sotuv',
    'otkaz': 'Atkaz',
    'open_number': "O'chiq Nomer",
    'wrong_number': 'Xato nomer',
    'advice': 'Maslahat',
    'other': "O'qiydi",
    'not_answered': "Ko'tarmadi",
}
STATUS_ORDER = ['new', 'sale', 'otkaz', 'open_number', 'wrong_number', 'advice', 'other', 'not_answered']
NOTE_REQUIRED_STATUSES = ['sale', 'otkaz', 'advice', 'other']


def clean_string(value):
    if value is None:
        return ''
    return str(value).strip()


def is_valid_status(value):
    return value in STATUS_ORDER


def empty_status_counts(include_new=False):
    data = {k: 0 for k in STATUS_ORDER if include_new or k != 'new'}
    return data


def local_date_key(value=None):
    value = value or timezone.now()
    if isinstance(value, str):
        value = parse_datetime_value(value) or timezone.now()
    return timezone.localtime(value).date().isoformat()


def parse_date(value):
    value = clean_string(value)
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        return None


def parse_datetime_value(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value if timezone.is_aware(value) else timezone.make_aware(value)
    try:
        text = str(value).replace('Z', '+00:00')
        dt = datetime.fromisoformat(text)
        return dt if timezone.is_aware(dt) else timezone.make_aware(dt)
    except Exception:
        return None


def day_range(date_value=None):
    d = parse_date(date_value) if date_value else timezone.localdate()
    start = timezone.make_aware(datetime.combine(d, time.min))
    end = timezone.make_aware(datetime.combine(d, time.max))
    return d.isoformat(), start, end


def parse_date_range(params):
    today = timezone.localdate()
    exact = clean_string(params.get('date'))
    month_value = clean_string(params.get('month'))
    if exact and parse_date(exact):
        start = end = parse_date(exact)
    elif month_value and len(month_value) == 7:
        try:
            year, month = [int(x) for x in month_value.split('-')]
            start = datetime(year, month, 1).date()
            end = (datetime(year + (month == 12), 1 if month == 12 else month + 1, 1).date() - timedelta(days=1))
        except Exception:
            start = today.replace(day=1); end = today
    else:
        raw_start = parse_date(params.get('start_date'))
        raw_end = parse_date(params.get('end_date'))
        end = raw_end or today
        start = raw_start or end.replace(day=1)
    if start > end:
        start, end = end, start
    start_dt = timezone.make_aware(datetime.combine(start, time.min))
    end_dt = timezone.make_aware(datetime.combine(end, time.max))
    return {
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
        'start_dt': start_dt,
        'end_dt': end_dt,
    }


def normalize_phone(value):
    raw = clean_string(value)
    if not raw:
        return ''

    # Excel ba'zan telefon raqamni son qilib beradi: 998901234567.0 yoki 9.98901234567E+11.
    # Shunday holatda oxiriga ortiqcha 0 qo‘shilib ketmasligi uchun oldin tozalab olamiz.
    cleaned_raw = raw.replace(' ', '')
    try:
        if cleaned_raw.lower().endswith('.0'):
            cleaned_raw = cleaned_raw[:-2]
        if 'e' in cleaned_raw.lower():
            number = Decimal(cleaned_raw)
            if number == number.to_integral_value():
                cleaned_raw = format(number.quantize(Decimal(1)), 'f')
    except (InvalidOperation, ValueError):
        cleaned_raw = raw

    digits = ''.join(ch for ch in cleaned_raw if ch.isdigit())
    if not digits:
        return ''
    if digits.startswith('998') and len(digits) >= 12:
        return '+' + digits[:12]
    if len(digits) == 9:
        return '+998' + digits
    if raw.startswith('+'):
        return '+' + digits
    return digits


def normalize_excel_column(value):
    text = ' '.join(clean_string(value).split())
    mapping = {
        '№': '№', '#': '№', 'no': '№', 'n': '№',
        't/sh': 'T/SH', 'tsh': 'T/SH', 't sh': 'T/SH', 't.sh': 'T/SH', 't-sh': 'T/SH', 't_sh': 'T/SH',
        'maktab': 'Maktab', 'school': 'Maktab',
        'sinf': 'Sinf', 'sinfi': 'Sinf', 'class': 'Sinf', 'grade': 'Sinf',
        'f.i.o': 'F.I.O', 'fio': 'F.I.O', 'f i o': 'F.I.O', 'f/i/o': 'F.I.O', 'f.i.sh': 'F.I.O', 'fish': 'F.I.O', 'ism': 'F.I.O', 'ismi': 'F.I.O',
        'fan': 'Fan', 'subject': 'Fan',
        'ball': 'Ball', 'bal': 'Ball', 'score': 'Ball',
        'filial': 'Filial', 'filiali': 'Filial', 'branch': 'Filial', 'hudud': 'Filial', 'region': 'Filial', "o'quv markaz": 'Filial', 'o‘quv markaz': 'Filial', 'markaz': 'Filial',
        'tel1': 'tel1', 'tel 1': 'tel1', 'telefon1': 'tel1', 'telefon 1': 'tel1', 'phone1': 'tel1', 'phone 1': 'tel1', 'nomer1': 'tel1', 'nomer 1': 'tel1',
        'tel2': 'tel2', 'tel 2': 'tel2', 'telefon2': 'tel2', 'telefon 2': 'tel2', 'phone2': 'tel2', 'phone 2': 'tel2', 'nomer2': 'tel2', 'nomer 2': 'tel2',
        'tel3': 'tel3', 'tel 3': 'tel3', 'telefon3': 'tel3', 'telefon 3': 'tel3', 'phone3': 'tel3', 'phone 3': 'tel3', 'nomer3': 'tel3', 'nomer 3': 'tel3',
    }
    return mapping.get(text.lower(), text)


def apply_lead_search(qs, search):
    s = clean_string(search)
    if not s:
        return qs
    return qs.filter(Q(full_name__icontains=s) | Q(tsh__icontains=s) | Q(subject__icontains=s) | Q(ball__icontains=s) | Q(phone1__icontains=s) | Q(phone2__icontains=s) | Q(phone3__icontains=s) | Q(school__icontains=s) | Q(grade__icontains=s) | Q(branch_name__icontains=s))


def excel_safe(value):
    if value is None:
        return ''
    if isinstance(value, datetime):
        return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')
    text = str(value)
    if text.startswith(('=', '+', '-', '@')):
        return "'" + text
    return text


def format_dt(value):
    if not value:
        return ''
    if isinstance(value, str):
        return value
    return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')
