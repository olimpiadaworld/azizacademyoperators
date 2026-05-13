import json
import mimetypes
from collections import defaultdict
from io import BytesIO
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from .models import AppUser, Lead, LeadStatusHistory, OnlineLead, LeadVisitDecision, LeadVisitDecisionHistory, ExcelImport, ExcelImportRow, DataAuditLog
from .auth import issue_tokens, verify_password, require_auth, decode_refresh
from .serializers import user_to_dict, serialize_leads, lead_to_dict, online_lead_to_dict, visit_decision_to_dict
from .utils import (
    STATUS_LABELS, STATUS_ORDER, NOTE_REQUIRED_STATUSES,
    clean_string, is_valid_status, empty_status_counts, normalize_excel_column,
    normalize_phone, parse_datetime_value, parse_date_range, day_range,
    apply_lead_search, excel_safe, format_dt, local_date_key,
)
from .telegram import send_telegram_message, line as tg_line, lead_info as tg_lead_info, user_name as tg_user_name, now_text as tg_now_text


def notify_telegram_after_commit(text):
    if not text:
        return
    transaction.on_commit(lambda: send_telegram_message(text))



BRANCH_CHOICES = [
    'Niyozbosh', 'Xalqabod', 'Gulbahor', 'Kasblar', 'Kids1', 'Kids2',
    'Do’stobod', 'Olmazor', 'Chinoz', 'Krasin', 'Pitiletka', 'Qo’rg’oncha',
    'Kids 3', 'Oqqo’rg’on', 'Alimkent'
]

BRANCH_ALIASES = {
    'dostobod': 'Do’stobod', 'do‘stobod': 'Do’stobod', "do'stobod": 'Do’stobod', 'do’stobod': 'Do’stobod',
    'qorgoncha': 'Qo’rg’oncha', "qo'rg'oncha": 'Qo’rg’oncha', 'qo’rg’oncha': 'Qo’rg’oncha', 'qo‘rg‘oncha': 'Qo’rg’oncha',
    'oqqorgon': 'Oqqo’rg’on', "oqqo'rg'on": 'Oqqo’rg’on', 'oqqo’rg’on': 'Oqqo’rg’on', 'oqqo‘rg‘on': 'Oqqo’rg’on',
    'xalqobod': 'Xalqabod', 'xalqabod': 'Xalqabod',
    'kids 1': 'Kids1', 'kids1': 'Kids1', 'kids 2': 'Kids2', 'kids2': 'Kids2', 'kids3': 'Kids 3', 'kids 3': 'Kids 3',
}


def normalize_branch_label(value):
    value = clean_string(value)
    if not value:
        return ''
    if '-' in value and value.split('-', 1)[0].strip().isdigit():
        value = value.split('-', 1)[1].strip()
    key = value.lower().replace('ʼ', "'").replace('’', "'").replace('‘', "'").strip()
    key = ' '.join(key.split())
    if key in BRANCH_ALIASES:
        return BRANCH_ALIASES[key]
    for branch in BRANCH_CHOICES:
        if branch.lower().replace('’', "'") == key:
            return branch
    return value


def normalize_branch_names(value):
    items = []
    if isinstance(value, (list, tuple)):
        raw_items = value
    else:
        raw_items = str(value or '').replace(';', ',').split(',')
    for raw in raw_items:
        branch = normalize_branch_label(raw)
        if branch and branch not in items:
            items.append(branch)
    return items


def branch_names_string(body):
    raw = body.get('branch_names')
    if raw is None:
        raw = body.get('branch_name') or body.get('branch') or body.get('filial')
    return ', '.join(normalize_branch_names(raw))


def user_branch_set(user):
    return set(normalize_branch_names(getattr(user, 'branch_name', '') or ''))


def users_branch_overlap(user_a, user_b):
    a = user_branch_set(user_a)
    b = user_branch_set(user_b)
    return bool(a and b and a.intersection(b))


def filial_can_see_lead(filial_user, lead):
    operator = getattr(lead, 'assigned_operator', None)
    return bool(operator and users_branch_overlap(filial_user, operator))

def status_text(value):
    return STATUS_LABELS.get(value, value or '')


def json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return {}


def ok(data, status=200):
    return JsonResponse(data, status=status, safe=not isinstance(data, list))


def health(request):
    return ok({'status': 'ok', 'message': 'Django backend ishlayapti'})


@require_auth('admin')
def telegram_test(request):
    result = send_telegram_message(
        '✅ <b>Telegram notification test</b>\n'
        + tg_line('Vaqt', tg_now_text())
        + tg_line('Admin', tg_user_name(request.app_user))
        + 'Aziz Academy Operators CRM dan test xabar.'
    )
    return ok({'sent': bool(result.get('ok')), 'result': result})


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    body = json_body(request)
    username = clean_string(body.get('username'))
    password = str(body.get('password') or '')
    user = AppUser.objects.filter(username=username, is_active=True).first()
    if not user or not verify_password(password, user.password_hash):
        return ok({'non_field_errors': ['Login yoki parol xato.'], 'detail': 'Login yoki parol xato.'}, status=400)
    tokens = issue_tokens(user)
    return ok({**tokens, 'user': user_to_dict(user)})


@csrf_exempt
@require_http_methods(['POST'])
def refresh_view(request):
    body = json_body(request)
    try:
        payload = decode_refresh(body.get('refresh'))
        user = AppUser.objects.get(id=payload.get('userId'), is_active=True)
        return ok({'access': issue_tokens(user)['access']})
    except Exception:
        return ok({'detail': 'Refresh token noto‘g‘ri yoki muddati tugagan.'}, status=401)


@require_auth()
def me_view(request):
    return ok(user_to_dict(request.app_user))


def list_users(role, boss_id=None):
    qs = AppUser.objects.select_related('boss').filter(role=role, is_active=True)
    if boss_id is not None:
        qs = qs.filter(boss_id=boss_id)
    return [user_to_dict(u) for u in qs.order_by('-id')]


def create_user(request, role, boss_id=None):
    body = json_body(request)
    username = clean_string(body.get('username'))
    password = str(body.get('password') or '')
    full_name = clean_string(body.get('full_name'))
    phone = '' if role in ('operator', 'filial_rahbari') else clean_string(body.get('phone'))
    branch_name = branch_names_string(body)
    if role in ('operator', 'filial_rahbari'):
        full_name = full_name or username
        if not username or not password:
            return ok({'detail': 'Login va parol kiritish shart.'}, status=400)
        if not branch_name:
            return ok({'branch_name': ['Kamida bitta filial tanlash shart.'], 'detail': 'Kamida bitta filial tanlash shart.'}, status=400)
    elif not username or not password or not full_name:
        return ok({'detail': 'Ism, login va parol kiritish shart.'}, status=400)
    if AppUser.objects.filter(username=username).exists():
        return ok({'username': ['Bu login allaqachon mavjud.']}, status=400)
    user = AppUser.objects.create(
        username=username,
        password_hash=make_password(password),
        full_name=full_name,
        phone=phone,
        role=role,
        boss_id=boss_id,
        branch_name=branch_name,
        is_active=bool(body.get('is_active', True)),
    )
    return ok(user_to_dict(user), status=201)


def update_user(request, user_id, role, boss_id=None):
    qs = AppUser.objects.filter(id=user_id, role=role)
    if boss_id is not None:
        qs = qs.filter(boss_id=boss_id)
    user = qs.first()
    if not user:
        return ok({'detail': 'Foydalanuvchi topilmadi.'}, status=404)
    old = user_to_dict(user)
    body = json_body(request)
    username = clean_string(body.get('username') or user.username)
    if username != user.username and AppUser.objects.filter(username=username).exclude(id=user.id).exists():
        return ok({'username': ['Bu login allaqachon mavjud.']}, status=400)
    user.username = username
    if 'full_name' in body:
        user.full_name = clean_string(body.get('full_name'))
    if 'phone' in body:
        user.phone = '' if role in ('operator', 'filial_rahbari') else clean_string(body.get('phone'))
    if 'branch_names' in body or 'branch_name' in body or 'branch' in body or 'filial' in body:
        normalized_branches = branch_names_string(body)
        if role in ('operator', 'filial_rahbari') and not normalized_branches:
            return ok({'branch_name': ['Kamida bitta filial tanlash shart.'], 'detail': 'Kamida bitta filial tanlash shart.'}, status=400)
        user.branch_name = normalized_branches
    if 'is_active' in body:
        user.is_active = bool(body.get('is_active'))
        if user.is_active:
            user.deactivated_at = None
        elif not user.deactivated_at:
            user.deactivated_at = timezone.now()
    if body.get('password'):
        user.password_hash = make_password(str(body.get('password')))
    user.updated_at = timezone.now()
    user.save()
    DataAuditLog.objects.create(actor=request.app_user, entity_type='app_user', entity_id=user.id, action='updated', old_data=old, new_data=user_to_dict(user))
    return ok(user_to_dict(user))


def delete_user(request, user_id, role, boss_id=None):
    qs = AppUser.objects.filter(id=user_id, role=role)
    if boss_id is not None:
        qs = qs.filter(boss_id=boss_id)
    user = qs.first()
    if not user:
        return ok({'detail': 'Foydalanuvchi topilmadi.'}, status=404)
    old = user_to_dict(user)
    user.is_active = False
    user.deactivated_at = user.deactivated_at or timezone.now()
    user.updated_at = timezone.now()
    user.save(update_fields=['is_active', 'deactivated_at', 'updated_at'])
    DataAuditLog.objects.create(actor=request.app_user, entity_type='app_user', entity_id=user.id, action='deactivated', old_data=old, new_data=user_to_dict(user))
    return HttpResponse(status=204)


@csrf_exempt
@require_auth('admin')
def admin_bosses(request, user_id=None):
    if request.method == 'GET':
        return ok(list_users('boss'))
    if request.method == 'POST':
        return create_user(request, 'boss')
    if request.method in ('PATCH', 'PUT'):
        return update_user(request, user_id, 'boss')
    if request.method == 'DELETE':
        return delete_user(request, user_id, 'boss')
    return ok({'detail': 'Method not allowed'}, status=405)


@csrf_exempt
@require_auth('admin')
def admin_filial_rahbarlari(request, user_id=None):
    if request.method == 'GET':
        return ok(list_users('filial_rahbari'))
    if request.method == 'POST':
        return create_user(request, 'filial_rahbari')
    if request.method in ('PATCH', 'PUT'):
        return update_user(request, user_id, 'filial_rahbari')
    if request.method == 'DELETE':
        return delete_user(request, user_id, 'filial_rahbari')
    return ok({'detail': 'Method not allowed'}, status=405)



@csrf_exempt
@require_auth('admin')
def admin_users(request, user_id=None):
    allowed_roles = ['boss', 'operator', 'filial_rahbari']
    if request.method == 'GET':
        qs = AppUser.objects.select_related('boss').filter(role__in=allowed_roles, is_active=True).order_by('role', '-id')
        return ok([user_to_dict(u) for u in qs])

    user = AppUser.objects.filter(id=user_id, role__in=allowed_roles).first()
    if not user:
        return ok({'detail': 'Foydalanuvchi topilmadi.'}, status=404)

    if request.method in ('PATCH', 'PUT'):
        return update_user(request, user_id, user.role)

    if request.method == 'DELETE':
        return delete_user(request, user_id, user.role)

    return ok({'detail': 'Method not allowed'}, status=405)

@csrf_exempt
@require_auth('boss')
def boss_operators(request, user_id=None):
    if request.method == 'GET':
        return ok(list_users('operator', request.app_user.id))
    if request.method == 'POST':
        return create_user(request, 'operator', request.app_user.id)
    if request.method in ('PATCH', 'PUT'):
        return update_user(request, user_id, 'operator', request.app_user.id)
    if request.method == 'DELETE':
        return delete_user(request, user_id, 'operator', request.app_user.id)
    return ok({'detail': 'Method not allowed'}, status=405)


def base_lead_qs():
    return Lead.objects.select_related('assigned_operator', 'boss', 'uploaded_by').all()


def get_one_lead(lead_id):
    lead = base_lead_qs().filter(id=lead_id).first()
    if not lead:
        return None
    online = OnlineLead.objects.select_related('assigned_operator').filter(created_lead_id=lead_id).order_by('-submitted_at').first()
    history = list(LeadStatusHistory.objects.select_related('changed_by').filter(lead_id=lead_id).order_by('-changed_at', '-id'))
    decisions = list(LeadVisitDecision.objects.select_related('lead', 'decided_by', 'payment_done_by').filter(lead_id=lead_id).order_by('-updated_at'))
    return lead_to_dict(lead, history, online, decisions)


@require_auth('operator')
def operator_leads(request):
    qs = base_lead_qs().filter(assigned_operator=request.app_user)
    status = clean_string(request.GET.get('current_status'))
    if status:
        qs = qs.filter(current_status=status)
    qs = apply_lead_search(qs, request.GET.get('search'))
    return ok(serialize_leads(qs.order_by('-updated_at', '-id'), include_visit_decisions=False))


@require_auth('boss', 'filial_rahbari')
def boss_leads(request):
    user = request.app_user
    qs = base_lead_qs()
    if user.role == 'filial_rahbari':
        # Filial rahbarlari barcha Sotuv leadlarni ko‘radi.
        # Agar biror rahbar “Keldi” bosgan bo‘lsa, lead hamma rahbarlardan yopiladi.
        # Agar rahbar “Kelmadi” bosgan bo‘lsa, lead faqat o‘sha rahbar panelidan yopiladi.
        arrived_lead_ids = LeadVisitDecision.objects.filter(decision='arrived').values('lead_id')
        own_not_arrived_ids = LeadVisitDecision.objects.filter(decided_by=user, decision='not_arrived').values('lead_id')
        qs = qs.filter(current_status='sale').exclude(id__in=arrived_lead_ids).exclude(id__in=own_not_arrived_ids)
        qs = apply_lead_search(qs, request.GET.get('search')).order_by('-updated_at', '-id')
        visible = [lead for lead in qs if filial_can_see_lead(user, lead)]
        return ok(serialize_leads(visible, include_visit_decisions=True))
    else:
        qs = qs.filter(boss=user)
        status = clean_string(request.GET.get('current_status'))
        if status:
            qs = qs.filter(current_status=status)
        if clean_string(request.GET.get('assigned_operator')):
            qs = qs.filter(assigned_operator_id=int(request.GET.get('assigned_operator')))
    qs = apply_lead_search(qs, request.GET.get('search'))
    return ok(serialize_leads(qs.order_by('-updated_at', '-id'), include_visit_decisions=True))


@require_auth('admin')
def admin_leads(request):
    qs = base_lead_qs()
    if request.GET.get('current_status'):
        qs = qs.filter(current_status=request.GET.get('current_status'))
    if request.GET.get('assigned_operator'):
        qs = qs.filter(assigned_operator_id=int(request.GET.get('assigned_operator')))
    if request.GET.get('boss'):
        qs = qs.filter(boss_id=int(request.GET.get('boss')))
    qs = apply_lead_search(qs, request.GET.get('search'))
    return ok(serialize_leads(qs.order_by('-updated_at', '-id'), include_visit_decisions=True))


@csrf_exempt
@require_auth('operator')
def change_status(request, lead_id):
    body = json_body(request)
    next_status = clean_string(body.get('current_status'))
    note = clean_string(body.get('note'))
    if not is_valid_status(next_status):
        return ok({'current_status': ['Status noto‘g‘ri.']}, status=400)
    if next_status in NOTE_REQUIRED_STATUSES and not note:
        return ok({'note': ['Bu status uchun izoh kiritish kerak.']}, status=400)
    lead = Lead.objects.filter(id=lead_id, assigned_operator=request.app_user).first()
    if not lead:
        return ok({'detail': 'Bu lead sizga tegishli emas.'}, status=403)
    old_status = lead.current_status
    with transaction.atomic():
        lead.current_status = next_status
        lead.updated_at = timezone.now()
        lead.save(update_fields=['current_status', 'updated_at'])
        LeadStatusHistory.objects.create(lead=lead, old_status=old_status, new_status=next_status, changed_by=request.app_user, note=note)
        DataAuditLog.objects.create(actor=request.app_user, entity_type='lead', entity_id=lead.id, action='status_changed', old_data={'current_status': old_status}, new_data={'current_status': next_status, 'note': note})
        if next_status in ('sale', 'advice') and old_status != next_status:
            title = 'Yangi SOTUV lead' if next_status == 'sale' else 'Yangi MASLAHAT lead'
            emoji = '💰' if next_status == 'sale' else '💬'
            msg = (
                f'{emoji} <b>{title}</b>\n'
                + tg_line('Vaqt', tg_now_text())
                + tg_line('Operator', tg_user_name(request.app_user))
                + tg_line('Oldingi status', status_text(old_status))
                + tg_line('Yangi status', status_text(next_status))
                + tg_line('Izoh', note)
                + '\n' + tg_lead_info(lead)
            )
            notify_telegram_after_commit(msg)
    return ok(get_one_lead(lead.id))


@require_auth('operator')
def reminders(request):
    qs = base_lead_qs().filter(assigned_operator=request.app_user, reminder_at__isnull=False, reminder_last_notified_at__isnull=True).order_by('reminder_at')
    return ok(serialize_leads(qs, include_visit_decisions=False))


@csrf_exempt
@require_auth('operator')
def set_reminder(request, lead_id):
    body = json_body(request)
    lead = Lead.objects.filter(id=lead_id, assigned_operator=request.app_user).first()
    if not lead:
        return ok({'detail': 'Bu lead sizga tegishli emas.'}, status=403)
    old = {'reminder_at': lead.reminder_at.isoformat() if lead.reminder_at else None, 'reminder_note': lead.reminder_note, 'reminder_last_notified_at': lead.reminder_last_notified_at.isoformat() if lead.reminder_last_notified_at else None}
    if 'reminder_at' in body:
        if body.get('reminder_at'):
            lead.reminder_at = parse_datetime_value(body.get('reminder_at'))
            lead.reminder_last_notified_at = None
        else:
            lead.reminder_at = None
            lead.reminder_note = ''
            lead.reminder_last_notified_at = None
    if 'reminder_note' in body:
        lead.reminder_note = clean_string(body.get('reminder_note'))
    if body.get('mark_as_notified') and lead.reminder_at:
        lead.reminder_last_notified_at = timezone.now()
    lead.updated_at = timezone.now()
    lead.save()
    new = {'reminder_at': lead.reminder_at.isoformat() if lead.reminder_at else None, 'reminder_note': lead.reminder_note, 'reminder_last_notified_at': lead.reminder_last_notified_at.isoformat() if lead.reminder_last_notified_at else None}
    DataAuditLog.objects.create(actor=request.app_user, entity_type='lead', entity_id=lead.id, action='reminder_updated', old_data=old, new_data=new)
    return ok(get_one_lead(lead.id))


@csrf_exempt
@require_http_methods(['POST'])
def public_online_leads(request):
    body = json_body(request)
    tsh = clean_string(body.get('tsh') or body.get('t_sh'))
    school = clean_string(body.get('school') or body.get('maktab'))
    grade = clean_string(body.get('grade') or body.get('sinf'))
    full_name = clean_string(body.get('full_name') or body.get('fio'))
    subject = clean_string(body.get('subject') or body.get('interest_subject') or body.get('fan'))
    phone1 = clean_string(body.get('phone1') or body.get('tel1'))
    phone2 = clean_string(body.get('phone2') or body.get('tel2'))
    phone3 = clean_string(body.get('phone3') or body.get('tel3'))
    age = int(body.get('age') or 0)
    region = clean_string(body.get('region'))

    boss = AppUser.objects.filter(role='boss', is_active=True).order_by('id').first()
    item = OnlineLead.objects.create(
        full_name=full_name, tsh=tsh, school=school, grade=grade, subject=subject,
        age=age, phone1=phone1, phone2=phone2, phone3=phone3,
        interest_subject=subject, region=region, assigned_boss=boss, source_payload=body
    )
    msg = (
        '🆕 <b>Yangi online lead keldi</b>\n'
        + tg_line('Vaqt', tg_now_text())
        + tg_line('T/SH', tsh)
        + tg_line('Maktab', school)
        + tg_line('Sinf', grade)
        + tg_line('F.I.O', full_name)
        + tg_line('Fan', subject)
        + tg_line('Tel 1', phone1)
        + tg_line('Tel 2', phone2)
        + tg_line('Tel 3', phone3)
        + tg_line('Boss', tg_user_name(boss))
    )
    notify_telegram_after_commit(msg)
    return ok(online_lead_to_dict(item), status=201)


@require_auth('boss')
def boss_online_leads(request):
    qs = OnlineLead.objects.select_related('assigned_operator').filter(assigned_operator__isnull=True, assigned_boss=request.app_user)
    search = clean_string(request.GET.get('search'))
    if search:
        qs = qs.filter(Q(full_name__icontains=search) | Q(phone1__icontains=search) | Q(phone2__icontains=search) | Q(phone3__icontains=search) | Q(tsh__icontains=search) | Q(school__icontains=search) | Q(grade__icontains=search) | Q(subject__icontains=search) | Q(interest_subject__icontains=search))
    return ok([online_lead_to_dict(x) for x in qs.order_by('-submitted_at')])


@require_auth('operator')
def operator_online_leads(request):
    qs = OnlineLead.objects.select_related('assigned_operator').filter(assigned_operator=request.app_user).order_by('-assigned_at', '-submitted_at')
    return ok([online_lead_to_dict(x) for x in qs])


@csrf_exempt
@require_auth('boss')
def assign_online_lead(request, online_id):
    body = json_body(request)
    operator_id = int(body.get('operator_id') or 0)
    operator = AppUser.objects.filter(id=operator_id, role='operator', boss=request.app_user, is_active=True).first()
    if not operator:
        return ok({'detail': 'Tanlangan operator topilmadi.'}, status=403)
    online = OnlineLead.objects.filter(id=online_id, assigned_operator__isnull=True, assigned_boss=request.app_user).first()
    if not online:
        return ok({'detail': 'Lead topilmadi yoki allaqachon biriktirilgan.'}, status=404)
    with transaction.atomic():
        lead = Lead.objects.create(
            full_name=online.full_name, tsh=getattr(online, 'tsh', '') or '',
            phone1=online.phone1, phone2=online.phone2, phone3=online.phone3,
            subject=(getattr(online, 'subject', '') or online.interest_subject or ''),
            school=getattr(online, 'school', '') or '', grade=(getattr(online, 'grade', '') or (f'{online.age} yosh' if online.age else '')),
            branch_name=online.region or '',
            assigned_operator=operator, boss=request.app_user, uploaded_by=request.app_user, current_status='new'
        )
        online.assigned_operator = operator
        online.created_lead = lead
        online.assigned_at = timezone.now()
        online.save()
        DataAuditLog.objects.create(actor=request.app_user, entity_type='online_lead', entity_id=online.id, action='assigned', new_data={'operator_id': operator_id, 'lead_id': lead.id})
        msg = (
            '👤 <b>Online lead operatorga biriktirildi</b>\n'
            + tg_line('Vaqt', tg_now_text())
            + tg_line('Boss', tg_user_name(request.app_user))
            + tg_line('Operator', tg_user_name(operator))
            + '\n' + tg_lead_info(lead)
        )
        notify_telegram_after_commit(msg)
    return ok(online_lead_to_dict(online))


@csrf_exempt
@require_auth('boss')
def bulk_assign_online_leads(request):
    body = json_body(request)
    operator_id = int(body.get('operator_id') or 0)
    operator = AppUser.objects.filter(id=operator_id, role='operator', boss=request.app_user, is_active=True).first()
    if not operator:
        return ok({'detail': 'Tanlangan operator topilmadi.'}, status=403)
    items = list(OnlineLead.objects.filter(assigned_operator__isnull=True, assigned_boss=request.app_user).order_by('submitted_at'))
    count = 0
    with transaction.atomic():
        for online in items:
            lead = Lead.objects.create(full_name=online.full_name, tsh=getattr(online, 'tsh', '') or '', phone1=online.phone1, phone2=online.phone2, phone3=online.phone3, subject=(getattr(online, 'subject', '') or online.interest_subject or ''), school=getattr(online, 'school', '') or '', grade=(getattr(online, 'grade', '') or (f'{online.age} yosh' if online.age else '')), branch_name=online.region or '', assigned_operator=operator, boss=request.app_user, uploaded_by=request.app_user, current_status='new')
            online.assigned_operator = operator
            online.created_lead = lead
            online.assigned_at = timezone.now()
            online.save()
            count += 1
    return ok({'assigned': count})


@csrf_exempt
@require_auth('filial_rahbari')
def visit_decision(request, lead_id):
    body = json_body(request)
    decision = clean_string(body.get('decision'))
    if decision not in ('arrived', 'not_arrived'):
        return ok({'decision': ['Qaror noto‘g‘ri.']}, status=400)
    lead = Lead.objects.select_related('assigned_operator', 'boss').filter(id=lead_id, current_status='sale').first()
    if not lead:
        return ok({'detail': 'Lead topilmadi.'}, status=404)
    if not filial_can_see_lead(request.app_user, lead):
        return ok({'detail': 'Bu lead sizga biriktirilgan filialga tegishli emas.'}, status=403)

    with transaction.atomic():
        existing_arrived = LeadVisitDecision.objects.select_for_update().filter(lead=lead, decision='arrived').first()
        if existing_arrived and existing_arrived.decided_by_id != request.app_user.id:
            return ok({'detail': 'Bu lead bo‘yicha boshqa filial rahbari “Keldi” bosgan. Lead barcha filial rahbarlardan yopildi.'}, status=409)

        item, created = LeadVisitDecision.objects.select_for_update().get_or_create(
            lead=lead,
            decided_by=request.app_user,
            defaults={'decision': decision},
        )
        old_decision = '' if created else item.decision

        if old_decision == 'arrived' and decision != 'arrived':
            return ok({'detail': '“Keldi” belgilangan leadni “Kelmadi”ga qaytarib bo‘lmaydi.'}, status=400)

        if not created and item.decision != decision:
            item.decision = decision
            item.updated_at = timezone.now()
            item.save(update_fields=['decision', 'updated_at'])

        if created or old_decision != decision:
            LeadVisitDecisionHistory.objects.create(lead=lead, decided_by=request.app_user, old_decision=old_decision, new_decision=decision)
            DataAuditLog.objects.create(actor=request.app_user, entity_type='lead_visit_decision', entity_id=item.id, action='upserted', old_data={'decision': old_decision}, new_data={'decision': decision})
            decision_label = 'Keldi' if decision == 'arrived' else 'Kelmadi'
            emoji = '✅' if decision == 'arrived' else '❌'
            msg = (
                f'{emoji} <b>Filial rahbari {decision_label} bosdi</b>\n'
                + tg_line('Vaqt', tg_now_text())
                + tg_line('Filial rahbari', tg_user_name(request.app_user))
                + tg_line('Filial', request.app_user.branch_name)
                + tg_line('Qaror', decision_label)
                + tg_line('Operator', tg_user_name(lead.assigned_operator))
                + '\n' + tg_lead_info(lead)
            )
            notify_telegram_after_commit(msg)
    return ok(visit_decision_to_dict(item))


@csrf_exempt
@require_auth('filial_rahbari')
def mark_visit_payment(request, lead_id):
    lead = Lead.objects.select_related('assigned_operator', 'boss').filter(id=lead_id, current_status='sale').first()
    if not lead:
        return ok({'detail': 'Lead topilmadi.'}, status=404)
    if not filial_can_see_lead(request.app_user, lead):
        return ok({'detail': 'Bu lead sizga biriktirilgan filialga tegishli emas.'}, status=403)
    with transaction.atomic():
        item = LeadVisitDecision.objects.select_for_update().filter(lead=lead, decided_by=request.app_user).first()
        if not item:
            return ok({'detail': 'Avval Keldi yoki Kelmadi belgilang.'}, status=400)
        old_payment = bool(item.payment_done)
        if not item.payment_done:
            item.payment_done = True
            item.payment_done_at = timezone.now()
            item.payment_done_by = request.app_user
            item.updated_at = timezone.now()
            item.save(update_fields=['payment_done', 'payment_done_at', 'payment_done_by', 'updated_at'])
            DataAuditLog.objects.create(actor=request.app_user, entity_type='lead_visit_payment', entity_id=item.id, action='payment_done', old_data={'payment_done': old_payment}, new_data={'payment_done': True})
            msg = ('💳 <b>To‘lov qilindi</b>\n' + tg_line('Vaqt', tg_now_text()) + tg_line('Filial rahbari', tg_user_name(request.app_user)) + tg_line('Filial', request.app_user.branch_name) + tg_line('Operator', tg_user_name(lead.assigned_operator)) + '\n' + tg_lead_info(lead))
            notify_telegram_after_commit(msg)
    return ok(visit_decision_to_dict(item))


@require_auth('boss', 'filial_rahbari')
def lead_visit_decisions(request):
    user = request.app_user
    if user.role == 'filial_rahbari':
        qs = LeadVisitDecision.objects.select_related('lead', 'lead__assigned_operator', 'lead__boss', 'decided_by', 'payment_done_by').filter(decided_by=user).order_by('-updated_at')
    else:
        operator_ids = list(AppUser.objects.filter(role='operator', boss=user).values_list('id', flat=True))
        qs = LeadVisitDecision.objects.select_related('lead', 'lead__assigned_operator', 'lead__boss', 'decided_by', 'payment_done_by').filter(lead__assigned_operator_id__in=operator_ids).order_by('-updated_at')
    return ok([visit_decision_to_dict(x) for x in qs])


@require_auth('operator')
def operator_visit_decisions(request):
    user = request.app_user
    qs = LeadVisitDecision.objects.select_related(
        'lead', 'lead__assigned_operator', 'lead__boss', 'decided_by', 'payment_done_by'
    ).filter(lead__assigned_operator=user).order_by('-updated_at')
    # Operator faqat o‘ziga biriktirilgan filiallar rahbarlari bosgan Keldi/Kelmadi natijalarini ko‘radi.
    visible = [item for item in qs if item.decided_by and users_branch_overlap(user, item.decided_by)]
    decision = clean_string(request.GET.get('decision'))
    payment = clean_string(request.GET.get('payment'))
    if decision in ('arrived', 'not_arrived'):
        visible = [item for item in visible if item.decision == decision]
    if payment == 'done':
        visible = [item for item in visible if bool(getattr(item, 'payment_done', False))]
    elif payment == 'not_done':
        visible = [item for item in visible if not bool(getattr(item, 'payment_done', False))]
    return ok([visit_decision_to_dict(x) for x in visible])


def autosize(ws):
    for col in ws.columns:
        max_len = 10
        letter = col[0].column_letter
        for cell in col:
            max_len = max(max_len, len(str(cell.value or '')))
        ws.column_dimensions[letter].width = min(max_len + 2, 45)


def excel_response(wb, filename):
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    resp = HttpResponse(bio.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f"attachment; filename={filename}"
    return resp


@require_auth('boss')
def import_template(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Leadlar'
    ws.append(['№', 'T/SH', 'Maktab', 'Sinf', 'F.I.O', 'Fan', 'Ball', 'tel1', 'tel2', 'tel3', 'Filial'])
    ws.append([1, 'T001', '25-maktab', '8-sinf', 'Aliyev Ali', 'English', '85', '+998901234567', '', '', 'Niyozbosh'])
    autosize(ws)
    return excel_response(wb, 'lead_import_shablon.xlsx')


def read_excel_rows(file_obj):
    wb = load_workbook(file_obj, data_only=True)
    ws = wb.worksheets[0]
    headers = []
    for cell in ws[1]:
        headers.append(normalize_excel_column(cell.value))
    rows = []
    for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        item = {}
        has = False
        for key, value in zip(headers, row):
            if not key:
                continue
            text = '' if value is None else str(value).strip()
            item[key] = text
            if text:
                has = True
        if has:
            rows.append((index, item))
    return headers, rows


@csrf_exempt
@require_auth('boss')
def import_leads(request):
    operator_value = clean_string(request.POST.get('operator_id'))
    file = request.FILES.get('file')
    if not file:
        return ok({'detail': 'Excel fayl tanlang.'}, status=400)
    if not file.name.lower().endswith('.xlsx'):
        return ok({'detail': 'Faqat .xlsx Excel fayl yuklash mumkin.'}, status=400)
    headers, rows = read_excel_rows(file)
    required = ['T/SH', 'Maktab', 'Sinf', 'F.I.O', 'Fan', 'Ball', 'tel1', 'tel2', 'tel3']
    missing = [c for c in required if c not in headers]
    if missing:
        return ok({'detail': 'Excel formati noto‘g‘ri.', 'missing_columns': missing, 'received_columns': headers}, status=400)
    operators = []
    operator_mode = 'single'
    assigned_operator = None
    if operator_value == 'all':
        operators = list(AppUser.objects.filter(role='operator', boss=request.app_user, is_active=True).order_by('id'))
        operator_mode = 'all'
        if not operators:
            return ok({'detail': 'Operatorlar topilmadi.'}, status=400)
    else:
        assigned_operator = AppUser.objects.filter(id=int(operator_value or 0), role='operator', boss=request.app_user, is_active=True).first()
        if not assigned_operator:
            return ok({'detail': 'Operator topilmadi.'}, status=400)
    import_record = ExcelImport.objects.create(uploaded_by=request.app_user, assigned_operator=assigned_operator, filename=file.name, total_rows=len(rows))
    success = duplicate = failed = 0
    op_index = 0
    for source_row_number, raw in rows:
        normalized = {
            'tsh': clean_string(raw.get('T/SH')),
            'school': clean_string(raw.get('Maktab')),
            'grade': clean_string(raw.get('Sinf')),
            'full_name': clean_string(raw.get('F.I.O')),
            'subject': clean_string(raw.get('Fan')),
            'ball': clean_string(raw.get('Ball')),
            'phone1': normalize_phone(raw.get('tel1')),
            'phone2': normalize_phone(raw.get('tel2')),
            'phone3': normalize_phone(raw.get('tel3')),
            'branch_name': clean_string(raw.get('Filial')),
        }
        try:
            # F.I.O yoki telefon raqam majburiy emas.
            # Excel qatorida kamida bitta ma'lumot bo'lsa, lead saqlanadi.
            operator = operators[op_index % len(operators)] if operator_mode == 'all' else assigned_operator
            if operator_mode == 'all':
                op_index += 1

            duplicate_query = Q()
            phones = [normalized.get('phone1'), normalized.get('phone2'), normalized.get('phone3')]
            for phone in [p for p in phones if p]:
                duplicate_query |= Q(phone1=phone) | Q(phone2=phone) | Q(phone3=phone)
            if normalized.get('full_name'):
                duplicate_query |= Q(full_name__iexact=normalized['full_name'])

            dup = None
            if duplicate_query:
                dup = Lead.objects.filter(boss=request.app_user).filter(duplicate_query).order_by('id').first()

            lead = Lead.objects.create(**normalized, assigned_operator=operator, boss=request.app_user, uploaded_by=request.app_user, current_status='new', source_row_number=source_row_number, is_duplicate=bool(dup), duplicate_of_lead=dup)
            ExcelImportRow.objects.create(import_record=import_record, source_row_number=source_row_number, raw_data=raw, normalized_data=normalized, status='duplicate' if dup else 'saved', lead=lead, duplicate_of_lead=dup)
            success += 1
            if dup:
                duplicate += 1
        except Exception as e:
            failed += 1
            ExcelImportRow.objects.create(import_record=import_record, source_row_number=source_row_number, raw_data=raw, normalized_data=normalized, status='failed', error_message=str(e))
    import_record.success_rows = success
    import_record.duplicate_rows = duplicate
    import_record.failed_rows = failed
    import_record.save()
    if operator_mode == 'all':
        operator_text = f'Barcha operatorlar ({len(operators)} ta)'
    else:
        operator_text = tg_user_name(assigned_operator)
    msg = (
        '📥 <b>Excel import qilindi</b>\n'
        + tg_line('Vaqt', tg_now_text())
        + tg_line('Boss', tg_user_name(request.app_user))
        + tg_line('Fayl', file.name)
        + tg_line('Operator', operator_text)
        + tg_line('Jami qator', len(rows))
        + tg_line('Saqlangan', success)
        + tg_line('Dublikat', duplicate)
        + tg_line('Xato', failed)
    )
    notify_telegram_after_commit(msg)
    return ok({'total_rows': len(rows), 'success_rows': success, 'duplicate_rows': duplicate, 'failed_rows': failed, 'operator_mode': operator_mode})


@require_auth('admin')
def admin_statistics(request):
    data = {
        'bosses': AppUser.objects.filter(role='boss', is_active=True).count(),
        'filial_rahbarlari': AppUser.objects.filter(role='filial_rahbari', is_active=True).count(),
        'operators': AppUser.objects.filter(role='operator', is_active=True).count(),
        'new': Lead.objects.filter(current_status='new').count(),
    }
    for st in STATUS_ORDER:
        data[st] = Lead.objects.filter(current_status=st).count()
    return ok(data)


@require_auth('boss')
def boss_statistics(request):
    ops = AppUser.objects.filter(role='operator', boss=request.app_user, is_active=True).order_by('full_name', 'username')
    today, start, end = day_range()
    rows = []
    for op in ops:
        total = Lead.objects.filter(assigned_operator=op).count()
        sale = Lead.objects.filter(assigned_operator=op, current_status='sale').count()
        hist_today = LeadStatusHistory.objects.filter(changed_by=op, changed_at__range=(start, end))
        touched_today = hist_today.values('lead_id').distinct().count()
        actions_today = hist_today.count()
        advice = Lead.objects.filter(assigned_operator=op, current_status='advice').count()
        other = Lead.objects.filter(assigned_operator=op, current_status='other').count()
        rows.append({
            'operator_id': op.id,
            'operator_name': op.full_name or op.username,
            'total': total,
            'sale': sale,
            'actions_today': actions_today,
            'touched_today': touched_today,
            'advice': advice,
            'other': other,
            'conversion': round((sale / total * 100) if total else 0, 1),
        })
    return ok(rows)


@require_auth('operator')
def operator_daily_results(request):
    user = request.app_user
    today, start, end = day_range()
    data = {st: Lead.objects.filter(assigned_operator=user, current_status=st).count() for st in STATUS_ORDER}
    hist_today = LeadStatusHistory.objects.filter(changed_by=user, changed_at__range=(start, end))
    data.update({
        'daily_sale': hist_today.filter(new_status='sale').count(),
        'daily_otkaz': hist_today.filter(new_status='otkaz').count(),
        'touched_today': hist_today.values('lead_id').distinct().count(),
        'actions_today': hist_today.count(),
    })
    return ok(data)


@require_auth('operator')
def operator_daily_history(request):
    days = int(request.GET.get('days') or 31)
    end = timezone.now()
    start = end - timedelta(days=days)
    hist = LeadStatusHistory.objects.filter(changed_by=request.app_user, changed_at__gte=start).order_by('-changed_at')
    by_day = defaultdict(lambda: {'date': '', 'sale': 0, 'otkaz': 0, 'wrong_number': 0, 'open_number': 0, 'advice': 0, 'other': 0, 'actions_total': 0})
    seen = set()
    for h in hist:
        key = local_date_key(h.changed_at)
        row = by_day[key]
        row['date'] = key
        row['actions_total'] += 1
        if h.new_status in row:
            row[h.new_status] += 1
    return ok({'results': [by_day[k] for k in sorted(by_day.keys(), reverse=True)]})


def _users_for_admin_report(params):
    qs = AppUser.objects.select_related('boss').filter(role='operator')
    if clean_string(params.get('boss_id')):
        qs = qs.filter(boss_id=int(params.get('boss_id')))
    if clean_string(params.get('operator_id')):
        qs = qs.filter(id=int(params.get('operator_id')))
    return list(qs.order_by('boss__full_name', 'full_name', 'username'))


def build_admin_report(params):
    date_info = parse_date_range(params)
    operators = _users_for_admin_report(params)
    op_ids = [op.id for op in operators]
    if not op_ids:
        return {'range': {'start_date': date_info['start_date'], 'end_date': date_info['end_date']}, 'selected_operator': {'id': None, 'name': ''}, 'summary': {'assigned_leads': 0, **empty_status_counts(), 'actions_total': 0, 'online_assigned': 0}, 'operators': [], 'operator_rows': [], 'daily': []}
    assigned_qs = Lead.objects.filter(assigned_operator_id__in=op_ids, created_at__range=(date_info['start_dt'], date_info['end_dt']))
    hist = list(LeadStatusHistory.objects.select_related('changed_by').filter(changed_by_id__in=op_ids, changed_at__range=(date_info['start_dt'], date_info['end_dt'])))
    online = OnlineLead.objects.filter(assigned_operator_id__in=op_ids, assigned_at__range=(date_info['start_dt'], date_info['end_dt']))
    summary = {'assigned_leads': assigned_qs.count(), **empty_status_counts(), 'actions_total': len(hist), 'online_assigned': online.count()}
    for h in hist:
        if h.new_status in summary:
            summary[h.new_status] += 1
    rows = []
    for op in operators:
        r = {'boss_id': op.boss_id, 'boss_name': op.boss.full_name if op.boss else '', 'operator_id': op.id, 'id': op.id, 'name': op.full_name or op.username, 'operator_name': op.full_name or op.username, 'assigned_leads': assigned_qs.filter(assigned_operator=op).count(), **empty_status_counts(), 'actions_total': 0, 'online_assigned': online.filter(assigned_operator=op).count()}
        for h in hist:
            if h.changed_by_id == op.id:
                r['actions_total'] += 1
                if h.new_status in r:
                    r[h.new_status] += 1
        rows.append(r)
    daily_map = defaultdict(lambda: {'date': '', 'assigned_leads': 0, 'sale': 0, 'otkaz': 0, 'wrong_number': 0, 'open_number': 0, 'advice': 0, 'other': 0, 'actions_total': 0, 'online_assigned': 0})
    for lead in assigned_qs:
        key = local_date_key(lead.created_at); daily_map[key]['date'] = key; daily_map[key]['assigned_leads'] += 1
    for h in hist:
        key = local_date_key(h.changed_at); daily_map[key]['date'] = key; daily_map[key]['actions_total'] += 1
        if h.new_status in daily_map[key]: daily_map[key][h.new_status] += 1
    for item in online:
        key = local_date_key(item.assigned_at); daily_map[key]['date'] = key; daily_map[key]['online_assigned'] += 1
    selected = operators[0] if len(operators) == 1 else None
    return {'range': {'start_date': date_info['start_date'], 'end_date': date_info['end_date']}, 'selected_operator': {'id': selected.id if selected else None, 'name': (selected.full_name or selected.username) if selected else ''}, 'summary': summary, 'operators': [{'id': r['operator_id'], 'name': r['operator_name'], 'boss_name': r['boss_name']} for r in rows], 'operator_rows': rows, 'daily': [daily_map[k] for k in sorted(daily_map.keys(), reverse=True)]}


@require_auth('admin')
def admin_operator_report(request):
    return ok(build_admin_report(request.GET))


def build_boss_full_report(user, params):
    query_params = dict(params.items()) if hasattr(params, 'items') else dict(params)
    operator_id = clean_string(query_params.get('operator_id'))
    date_info = parse_date_range(query_params)
    ops = list(AppUser.objects.filter(role='operator', boss=user, is_active=True).order_by('full_name', 'username'))
    if operator_id:
        ops = [op for op in ops if op.id == int(operator_id)]
    op_ids = [op.id for op in ops]
    assigned_qs = Lead.objects.filter(assigned_operator_id__in=op_ids, created_at__range=(date_info['start_dt'], date_info['end_dt'])) if op_ids else Lead.objects.none()
    hist = list(LeadStatusHistory.objects.filter(changed_by_id__in=op_ids, changed_at__range=(date_info['start_dt'], date_info['end_dt']))) if op_ids else []
    online_submitted = OnlineLead.objects.filter(assigned_boss=user, submitted_at__range=(date_info['start_dt'], date_info['end_dt']))
    online_assigned = OnlineLead.objects.filter(assigned_operator_id__in=op_ids, assigned_at__range=(date_info['start_dt'], date_info['end_dt'])) if op_ids else OnlineLead.objects.none()
    decisions = list(LeadVisitDecision.objects.select_related('decided_by', 'payment_done_by', 'lead', 'lead__assigned_operator', 'lead__boss').filter(lead__assigned_operator_id__in=op_ids, updated_at__range=(date_info['start_dt'], date_info['end_dt']))) if op_ids else []
    summary = {'assigned_leads': assigned_qs.count(), **empty_status_counts(), 'actions_total': len(hist), 'online_submitted': online_submitted.count(), 'online_assigned': online_assigned.count(), 'arrived': sum(1 for d in decisions if d.decision == 'arrived'), 'not_arrived': sum(1 for d in decisions if d.decision == 'not_arrived'), 'payment_done': sum(1 for d in decisions if getattr(d, 'payment_done', False)), 'payment_not_done': sum(1 for d in decisions if not getattr(d, 'payment_done', False))}
    for h in hist:
        if h.new_status in summary: summary[h.new_status] += 1
    op_rows = []
    for op in ops:
        r = {'operator_id': op.id, 'operator_name': op.full_name or op.username, 'assigned_leads': assigned_qs.filter(assigned_operator=op).count(), 'online_assigned': online_assigned.filter(assigned_operator=op).count(), **empty_status_counts(), 'actions_total': 0}
        for h in hist:
            if h.changed_by_id == op.id:
                r['actions_total'] += 1
                if h.new_status in r: r[h.new_status] += 1
        op_rows.append(r)
    filial_map = {}
    for d in decisions:
        key = d.decided_by_id or 0
        filial_map.setdefault(key, {'filial_rahbari_id': d.decided_by_id, 'filial_rahbari_name': d.decided_by.full_name if d.decided_by else '-', 'arrived': 0, 'not_arrived': 0, 'payment_done': 0, 'payment_not_done': 0, 'total': 0})
        filial_map[key]['total'] += 1
        filial_map[key]['arrived' if d.decision == 'arrived' else 'not_arrived'] += 1
        filial_map[key]['payment_done' if getattr(d, 'payment_done', False) else 'payment_not_done'] += 1
    daily_map = defaultdict(lambda: {'date': '', 'assigned_leads': 0, 'sale': 0, 'otkaz': 0, 'wrong_number': 0, 'open_number': 0, 'advice': 0, 'other': 0, 'online_submitted': 0, 'online_assigned': 0, 'arrived': 0, 'not_arrived': 0, 'payment_done': 0, 'payment_not_done': 0})
    for lead in assigned_qs:
        key = local_date_key(lead.created_at); daily_map[key]['date'] = key; daily_map[key]['assigned_leads'] += 1
    for h in hist:
        key = local_date_key(h.changed_at); daily_map[key]['date'] = key
        if h.new_status in daily_map[key]: daily_map[key][h.new_status] += 1
    for o in online_submitted:
        key = local_date_key(o.submitted_at); daily_map[key]['date'] = key; daily_map[key]['online_submitted'] += 1
    for o in online_assigned:
        key = local_date_key(o.assigned_at); daily_map[key]['date'] = key; daily_map[key]['online_assigned'] += 1
    for d in decisions:
        key = local_date_key(d.updated_at); daily_map[key]['date'] = key; daily_map[key]['arrived' if d.decision == 'arrived' else 'not_arrived'] += 1; daily_map[key]['payment_done' if getattr(d, 'payment_done', False) else 'payment_not_done'] += 1
    selected = ops[0] if len(ops) == 1 else None
    decision_rows = [visit_decision_to_dict(d) for d in sorted(decisions, key=lambda x: x.updated_at, reverse=True)]
    return {'range': {'start_date': date_info['start_date'], 'end_date': date_info['end_date']}, 'selected_operator': {'id': selected.id if selected else None, 'name': (selected.full_name or selected.username) if selected else ''}, 'summary': summary, 'operators': op_rows, 'filial_rahbarlari': list(filial_map.values()), 'daily': [daily_map[k] for k in sorted(daily_map.keys(), reverse=True)], 'visit_decisions': decision_rows, 'not_arrived_leads': [row for row in decision_rows if row.get('decision') == 'not_arrived'], 'arrived_leads': [row for row in decision_rows if row.get('decision') == 'arrived'], 'payment_done_leads': [row for row in decision_rows if row.get('payment_done')], 'payment_not_done_leads': [row for row in decision_rows if not row.get('payment_done')]}


@require_auth('boss')
def boss_full_report(request):
    return ok(build_boss_full_report(request.app_user, request.GET))


def add_header_style(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1F4E78')
        cell.alignment = Alignment(horizontal='center')
    ws.freeze_panes = 'A2'
    autosize(ws)


@require_auth('boss')
def boss_daily_report_excel(request):
    today, start, end = day_range()
    ops = AppUser.objects.filter(role='operator', boss=request.app_user)
    hist = LeadStatusHistory.objects.select_related('lead', 'changed_by').filter(changed_by__in=ops, changed_at__range=(start, end)).order_by('-changed_at')
    wb = Workbook(); ws = wb.active; ws.title = 'Leadlar'
    ws.append(['Vaqt', 'Operator', 'T/SH', 'Maktab', 'Sinf', 'F.I.O', 'Fan', 'Ball', 'tel1', 'tel2', 'tel3', 'Oldingi holat', 'Yangi holat', 'Izoh'])
    for h in hist:
        l = h.lead
        ws.append([format_dt(h.changed_at), h.changed_by.full_name if h.changed_by else '', l.tsh, l.school, l.grade, l.full_name, l.subject, l.ball, l.phone1, l.phone2, l.phone3, STATUS_LABELS.get(h.old_status, h.old_status), STATUS_LABELS.get(h.new_status, h.new_status), h.note])
    add_header_style(ws)
    return excel_response(wb, 'kunlik_hisobot.xlsx')


@require_auth('boss')
def boss_full_report_excel(request):
    report = build_boss_full_report(request.app_user, request.GET)
    wb = Workbook(); ws = wb.active; ws.title = 'Natijalar'
    ws.append(['Ko‘rsatkich', 'Soni'])
    for key, val in report['summary'].items(): ws.append([key, val])
    ws.append([]); ws.append(['Operator', 'Biriktirildi', 'Online', 'Sotuv', 'Atkaz', 'Xato nomer', "O'chiq nomer", 'Maslahat', 'Boshqa', 'Jami action'])
    for r in report['operators']:
        ws.append([r['operator_name'], r['assigned_leads'], r['online_assigned'], r['sale'], r['otkaz'], r['wrong_number'], r['open_number'], r['advice'], r['other'], r['actions_total']])
    add_header_style(ws)
    ws2 = wb.create_sheet('Filial Rahbarlari')
    ws2.append(['Filial rahbari', 'Jami', 'Keldi', 'Kelmadi', 'To‘lov qildi', 'To‘lov qilmadi'])
    for r in report.get('filial_rahbarlari', []):
        ws2.append([r.get('filial_rahbari_name', ''), r.get('total', 0), r.get('arrived', 0), r.get('not_arrived', 0), r.get('payment_done', 0), r.get('payment_not_done', 0)])
    add_header_style(ws2)
    def append_decision_sheet(sheet_name, rows):
        sheet = wb.create_sheet(sheet_name)
        sheet.append(['Vaqt', 'Filial rahbari', 'Qaror', 'To‘lov', 'To‘lov qilgan', 'To‘lov vaqti', 'F.I.O', 'tel1', 'tel2', 'tel3', 'T/SH', 'Maktab', 'Sinf', 'Fan', 'Ball', 'Operator'])
        for item in rows:
            sheet.append([format_dt(item.get('updated_at')), item.get('filial_rahbari_name', ''), 'Keldi' if item.get('decision') == 'arrived' else 'Kelmadi', 'To‘lov qilindi' if item.get('payment_done') else 'To‘lov qilinmadi', item.get('payment_done_by_name') or '', format_dt(item.get('payment_done_at')), excel_safe(item.get('lead_name') or item.get('full_name') or ''), item.get('lead_phone') or item.get('phone1') or '', item.get('lead_phone2') or item.get('phone2') or '', item.get('lead_phone3') or item.get('phone3') or '', item.get('tsh') or '', item.get('display_school') or item.get('school') or '', item.get('grade') or '', item.get('subject') or '', item.get('ball') or '', item.get('operator_name') or ''])
        add_header_style(sheet)
    append_decision_sheet('Kelmadi Leadlar', report.get('not_arrived_leads', []))
    append_decision_sheet('Keldi Leadlar', report.get('arrived_leads', []))
    append_decision_sheet('To‘lov Qilinganlar', report.get('payment_done_leads', []))
    return excel_response(wb, 'umumiy_hisobot.xlsx')


@require_auth('admin')
def admin_visit_decisions(request):
    qs = LeadVisitDecision.objects.select_related('lead', 'lead__assigned_operator', 'lead__boss', 'decided_by', 'payment_done_by').order_by('-updated_at')
    return ok([visit_decision_to_dict(x) for x in qs[:1000]])


@require_auth('admin')
def admin_all_reports_excel(request):
    wb = Workbook()
    ws = wb.active; ws.title = 'Barcha Leadlar'
    ws.append(['F.I.O', 'T/SH', 'Maktab', 'Sinf', 'Fan', 'Ball', 'tel1', 'tel2', 'tel3', 'Status', 'Operator', 'Yangilangan'])
    for l in Lead.objects.select_related('assigned_operator', 'boss').order_by('-id'):
        ws.append([excel_safe(l.full_name), l.tsh, l.school, l.grade, l.subject, l.ball, l.phone1, l.phone2, l.phone3, STATUS_LABELS.get(l.current_status, l.current_status), l.assigned_operator.full_name if l.assigned_operator else '', format_dt(l.updated_at)])
    add_header_style(ws)
    ws2 = wb.create_sheet('Status Tarixi')
    ws2.append(['Vaqt', 'Lead ID', 'F.I.O', 'Operator', 'Oldingi status', 'Yangi status', 'Izoh'])
    for h in LeadStatusHistory.objects.select_related('lead', 'changed_by').order_by('-changed_at'):
        ws2.append([format_dt(h.changed_at), h.lead_id, h.lead.full_name if h.lead else '', h.changed_by.full_name if h.changed_by else '', STATUS_LABELS.get(h.old_status, h.old_status), STATUS_LABELS.get(h.new_status, h.new_status), excel_safe(h.note)])
    add_header_style(ws2)
    ws3 = wb.create_sheet('Online Leadlar')
    ws3.append(['ID', 'F.I.O', 'Yosh', 'tel1', 'tel2', 'tel3', 'Fan', 'Hudud', 'Boss', 'Operator', 'Yuborilgan', 'Biriktirilgan'])
    for o in OnlineLead.objects.select_related('assigned_boss', 'assigned_operator').order_by('-submitted_at'):
        ws3.append([o.id, o.full_name, o.age, o.phone1, o.phone2, o.phone3, o.interest_subject, o.region, o.assigned_boss.full_name if o.assigned_boss else '', o.assigned_operator.full_name if o.assigned_operator else '', format_dt(o.submitted_at), format_dt(o.assigned_at)])
    add_header_style(ws3)
    ws4 = wb.create_sheet('Keldi Kelmadi Tolov')
    ws4.append(['Vaqt', 'Lead', 'Telefon', 'Filial rahbari', 'Qaror', 'To‘lov', 'To‘lov qilgan', 'To‘lov vaqti'])
    for d in LeadVisitDecision.objects.select_related('lead', 'decided_by', 'payment_done_by').order_by('-updated_at'):
        ws4.append([format_dt(d.updated_at), d.lead.full_name if d.lead else '', d.lead.phone1 if d.lead else '', d.decided_by.full_name if d.decided_by else '', 'Keldi' if d.decision == 'arrived' else 'Kelmadi', 'To‘lov qilindi' if d.payment_done else 'To‘lov qilinmadi', d.payment_done_by.full_name if d.payment_done_by else '', format_dt(d.payment_done_at)])
    add_header_style(ws4)
    ws5 = wb.create_sheet('Excel Import Qatorlari')
    ws5.append(['Import ID', 'Qator', 'Status', 'Lead ID', 'Xato', 'Raw data'])
    for r in ExcelImportRow.objects.order_by('-id')[:5000]:
        ws5.append([r.import_record_id, r.source_row_number, r.status, r.lead_id or '', r.error_message, json.dumps(r.raw_data, ensure_ascii=False)])
    add_header_style(ws5)
    ws6 = wb.create_sheet('Foydalanuvchilar')
    ws6.append(['ID', 'Login', 'Ism', 'Rol', 'Telefon', 'Boss', 'Filial', 'Aktiv'])
    for u in AppUser.objects.select_related('boss').order_by('role', 'full_name'):
        ws6.append([u.id, u.username, u.full_name, u.role, u.phone, u.boss.full_name if u.boss else '', u.branch_name, 'Ha' if u.is_active else 'Yo‘q'])
    add_header_style(ws6)
    return excel_response(wb, 'barcha_hisobotlar.xlsx')
