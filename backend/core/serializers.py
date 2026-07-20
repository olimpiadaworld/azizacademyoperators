from collections import defaultdict
from .models import LeadStatusHistory, OnlineLead, LeadVisitDecision


def parse_branch_names(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        raw = []
        for item in value:
            raw.extend(parse_branch_names(item))
        return list(dict.fromkeys(raw))
    parts = []
    for item in str(value).replace(';', ',').split(','):
        item = item.strip()
        if not item:
            continue
        if '-' in item and item.split('-', 1)[0].strip().isdigit():
            item = item.split('-', 1)[1].strip()
        parts.append(item)
    return list(dict.fromkeys(parts))


def user_to_dict(user):
    if not user:
        return None
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name or '',
        'phone': user.phone or '',
        'role': user.role,
        'boss': user.boss_id,
        'boss_name': getattr(user.boss, 'full_name', '') if getattr(user, 'boss_id', None) else '',
        'branch_name': user.branch_name or '',
        'branch_names': parse_branch_names(user.branch_name),
        'is_active': user.is_active,
        'deactivated_at': user.deactivated_at.isoformat() if user.deactivated_at else None,
    }


def history_to_dict(item):
    return {
        'id': item.id,
        'old_status': item.old_status,
        'new_status': item.new_status,
        'note': item.note or '',
        'changed_by_name': item.changed_by.full_name if item.changed_by_id and item.changed_by else '',
        'changed_at': item.changed_at,
    }


def get_lead_operator_note(lead, history=None):
    history = history or []
    if history:
        sale_history = next((h for h in history if h.new_status == 'sale' and (h.note or '').strip()), None)
        latest_with_note = next((h for h in history if (h.note or '').strip()), None)
        selected = sale_history or latest_with_note
    else:
        selected = None
        if lead:
            selected = LeadStatusHistory.objects.select_related('changed_by').filter(lead=lead, new_status='sale').exclude(note='').order_by('-changed_at', '-id').first()
            if not selected:
                selected = LeadStatusHistory.objects.select_related('changed_by').filter(lead=lead).exclude(note='').order_by('-changed_at', '-id').first()
    if not selected:
        return {'operator_note': '', 'operator_note_at': None, 'operator_note_by_name': ''}
    return {
        'operator_note': selected.note or '',
        'operator_note_at': selected.changed_at,
        'operator_note_by_name': ((selected.changed_by.full_name or selected.changed_by.username) if selected.changed_by_id and selected.changed_by else ''),
    }


def visit_decision_to_dict(item):
    lead = item.lead if item.lead_id and item.lead else None
    note_info = get_lead_operator_note(lead)
    return {
        'id': item.id,
        'lead': item.lead_id,
        'lead_id': item.lead_id,
        'lead_name': lead.full_name if lead else '',
        'full_name': lead.full_name if lead else '',
        'tsh': lead.tsh if lead else '',
        'subject': lead.subject if lead else '',
        'ball': lead.ball if lead else '',
        'school': lead.school if lead else '',
        'display_school': lead.school if lead else '',
        'grade': lead.grade if lead else '',
        'branch_name': lead.branch_name if lead else '',
        'lead_phone': lead.phone1 if lead else '',
        'lead_phone2': lead.phone2 if lead else '',
        'lead_phone3': lead.phone3 if lead else '',
        'phone1': lead.phone1 if lead else '',
        'phone2': lead.phone2 if lead else '',
        'phone3': lead.phone3 if lead else '',
        'operator_name': ((lead.assigned_operator.full_name or lead.assigned_operator.username) if lead and lead.assigned_operator_id and lead.assigned_operator else ''),
        'boss_name': ((lead.boss.full_name or lead.boss.username) if lead and lead.boss_id and lead.boss else ''),
        'decision': item.decision,
        'payment_done': bool(getattr(item, 'payment_done', False)),
        'payment_done_at': getattr(item, 'payment_done_at', None),
        'payment_done_by': getattr(item, 'payment_done_by_id', None),
        'payment_done_by_name': ((item.payment_done_by.full_name or item.payment_done_by.username) if getattr(item, 'payment_done_by_id', None) and getattr(item, 'payment_done_by', None) else ''),
        'left_without_payment': bool(getattr(item, 'left_without_payment', False)),
        'left_without_payment_at': getattr(item, 'left_without_payment_at', None),
        'left_without_payment_by_name': ((item.left_without_payment_by.full_name or item.left_without_payment_by.username) if getattr(item, 'left_without_payment_by_id', None) and getattr(item, 'left_without_payment_by', None) else ''),
        'decided_by': item.decided_by_id,
        'filial_rahbari_id': item.decided_by_id,
        'filial_rahbari_name': ((item.decided_by.full_name or item.decided_by.username) if item.decided_by_id and item.decided_by else ''),
        'filial_rahbari_branch': item.decided_by.branch_name if item.decided_by_id and item.decided_by else '',
        'operator_branch': lead.assigned_operator.branch_name if lead and lead.assigned_operator_id and lead.assigned_operator else '',
        'operator_note': note_info.get('operator_note', ''),
        'operator_note_at': note_info.get('operator_note_at'),
        'operator_note_by_name': note_info.get('operator_note_by_name', ''),
        'created_at': item.created_at,
        'updated_at': item.updated_at,
    }


def online_lead_to_dict(item):
    subject = getattr(item, 'subject', '') or item.interest_subject or ''
    return {
        'id': item.id,
        'full_name': item.full_name or '',
        'tsh': getattr(item, 'tsh', '') or '',
        'school': getattr(item, 'school', '') or '',
        'display_school': getattr(item, 'school', '') or '',
        'grade': getattr(item, 'grade', '') or '',
        'subject': subject,
        'age': item.age,
        'phone1': item.phone1 or '',
        'phone2': item.phone2 or '',
        'phone3': item.phone3 or '',
        'interest_subject': subject,
        'region': item.region or '',
        'assigned_boss': item.assigned_boss_id,
        'assigned_operator': item.assigned_operator_id,
        'operator_name': item.assigned_operator.full_name if item.assigned_operator_id and item.assigned_operator else '',
        'submitted_at': item.submitted_at,
        'assigned_at': item.assigned_at,
    }


def lead_to_dict(lead, history=None, online=None, decisions=None):
    history = history or []
    decisions = decisions or []
    note_info = get_lead_operator_note(lead, history)
    return {
        'id': lead.id,
        'full_name': lead.full_name or '',
        'tsh': lead.tsh or '',
        'subject': lead.subject or '',
        'ball': lead.ball or '',
        'phone1': lead.phone1 or '',
        'phone2': lead.phone2 or '',
        'phone3': lead.phone3 or '',
        'school': lead.school or '',
        'grade': lead.grade or '',
        'age': online.age if online else '',
        'branch_name': lead.branch_name or '',
        'display_school': '' if online else (lead.school or ''),
        'current_status': lead.current_status or 'new',
        'operator_name': ((lead.assigned_operator.full_name or lead.assigned_operator.username) if lead.assigned_operator_id and lead.assigned_operator else ''),
        'boss_name': ((lead.boss.full_name or lead.boss.username) if lead.boss_id and lead.boss else ''),
        'assigned_operator': lead.assigned_operator_id,
        'boss': lead.boss_id,
        'operator_note': note_info.get('operator_note', ''),
        'operator_note_at': note_info.get('operator_note_at'),
        'operator_note_by_name': note_info.get('operator_note_by_name', ''),
        'created_at': lead.created_at,
        'updated_at': lead.updated_at,
        'history': [history_to_dict(h) for h in history],
        'is_online': bool(online),
        'online_region': online.region if online else '',
        'online_interest_subject': online.interest_subject if online else '',
        'visit_decisions': [visit_decision_to_dict(d) for d in decisions],
        'reminder_at': lead.reminder_at,
        'reminder_note': lead.reminder_note or '',
        'reminder_last_notified_at': lead.reminder_last_notified_at,
        'is_duplicate': bool(lead.is_duplicate),
        'duplicate_of_lead': lead.duplicate_of_lead_id,
        'is_manual_entry': bool(lead.is_manual_entry),
    }


def serialize_leads(leads, include_visit_decisions=True):
    leads = list(leads)
    ids = [l.id for l in leads]
    hist_map = defaultdict(list)
    online_map = {}
    decision_map = defaultdict(list)
    if ids:
        for h in LeadStatusHistory.objects.select_related('changed_by').filter(lead_id__in=ids).order_by('-changed_at', '-id'):
            hist_map[h.lead_id].append(h)
        for o in OnlineLead.objects.select_related('assigned_operator').filter(created_lead_id__in=ids).order_by('-submitted_at'):
            online_map.setdefault(o.created_lead_id, o)
        if include_visit_decisions:
            for d in LeadVisitDecision.objects.select_related('lead', 'decided_by').filter(lead_id__in=ids).order_by('-updated_at'):
                decision_map[d.lead_id].append(d)
    return [lead_to_dict(l, hist_map.get(l.id, []), online_map.get(l.id), decision_map.get(l.id, [])) for l in leads]
