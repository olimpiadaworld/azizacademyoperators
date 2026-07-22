import os
import re
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password
from core.models import AppUser, Lead, LeadStatusHistory, OnlineLead, LeadVisitDecision, LeadVisitDecisionHistory, ExcelImport, ExcelImportRow, DataAuditLog


class Command(BaseCommand):
    help = 'Create database tables if missing and create first admin user.'

    BRANCH_ALIASES = {
        'niyozbosh': 'Niyozbosh', 'niyazbosh': 'Niyozbosh', 'niyoz bosh': 'Niyozbosh', 'niyaz bosh': 'Niyozbosh',
        'kids1': 'Kids 1', 'kids 1': 'Kids 1', 'kids2': 'Kids 2', 'kids 2': 'Kids 2',
        'kids3': 'Kids 3', 'kids 3': 'Kids 3', 'gulbahor': 'Gulbahor', 'kasblar': 'Kasblar',
        'xalqobod': 'Xalqobod', 'xalqabod': 'Xalqobod', 'chinoz': 'Chinoz',
        'olmazor': 'Olmozor', 'olmozor': 'Olmozor', 'paxtazor': 'Paxtazor', 'mevazor': 'Mevazor',
        'dostobod': 'Dostobod', "do'stobod": 'Dostobod', 'do‘stobod': 'Dostobod',
        'qorgonchi': "Qorg'onchi", "qorg'onchi": "Qorg'onchi", 'qorgoncha': "Qorg'onchi", "qo'rg'oncha": "Qorg'onchi",
        'oqqorgon': "Oqqo'rg'on", "oqqo'rg'on": "Oqqo'rg'on",
        'qoshyogoch': "Qo'shyog'och", "qo'shyog'och": "Qo'shyog'och",
    }

    def normalize_branch(self, value):
        text = str(value or '').strip()
        if not text:
            return ''
        if '-' in text and text.split('-', 1)[0].strip().isdigit():
            text = text.split('-', 1)[1].strip()
        key = text.lower().replace('ʼ', "'").replace('’', "'").replace('‘', "'")
        key = ' '.join(key.split())
        return self.BRANCH_ALIASES.get(key, '')

    def branch_from_sale_note(self, note):
        text = str(note or '').strip()
        if not text:
            return ''
        for match in re.finditer(r'(?:^|[|;\n])\s*filial\s*:\s*([^|;\n]+)', text, flags=re.IGNORECASE):
            branch = self.normalize_branch(match.group(1))
            if branch:
                return branch
        return ''

    def backfill_sale_lead_branches(self):
        """Eski sotuvlarda filialni status tarixidan lead.branch_name ga tiklaydi.

        Menenjer akkaunti sotuvdan keyin yaratilgan bo‘lsa ham ayni filialdagi
        oldingi sotuvlar uning paneliga tushishi uchun bu backfill deployda ishlaydi.
        """
        sale_lead_ids = list(Lead.objects.filter(current_status='sale').values_list('id', flat=True))
        if not sale_lead_ids:
            return

        branch_by_lead = {}
        history_rows = LeadStatusHistory.objects.filter(
            lead_id__in=sale_lead_ids,
            new_status='sale',
        ).only('lead_id', 'note', 'changed_at', 'id').order_by('-changed_at', '-id')
        for row in history_rows:
            if row.lead_id in branch_by_lead:
                continue
            branch = self.branch_from_sale_note(row.note)
            if branch:
                branch_by_lead[row.lead_id] = branch

        # Ayrim juda eski yozuvlarda filial faqat audit JSON ichida qolgan bo‘lishi mumkin.
        missing_ids = [lead_id for lead_id in sale_lead_ids if lead_id not in branch_by_lead]
        if missing_ids:
            audit_rows = DataAuditLog.objects.filter(
                entity_type='lead',
                entity_id__in=missing_ids,
                action='status_changed',
            ).only('entity_id', 'new_data', 'created_at', 'id').order_by('-created_at', '-id')
            for row in audit_rows:
                if row.entity_id in branch_by_lead:
                    continue
                data = row.new_data if isinstance(row.new_data, dict) else {}
                if data.get('current_status') != 'sale':
                    continue
                branch = self.normalize_branch(data.get('selected_branch') or data.get('branch_name') or data.get('filial'))
                if branch:
                    branch_by_lead[row.entity_id] = branch

        if not branch_by_lead:
            return
        changed = []
        for lead in Lead.objects.filter(id__in=branch_by_lead.keys()):
            branch = branch_by_lead.get(lead.id, '')
            if branch and lead.branch_name != branch:
                lead.branch_name = branch
                changed.append(lead)
        if changed:
            Lead.objects.bulk_update(changed, ['branch_name'])
            self.stdout.write(self.style.SUCCESS(f'{len(changed)} ta eski sotuv leadining filiali tiklandi.'))

    def ensure_missing_columns(self, schema_editor, model, field_names=None):
        table = model._meta.db_table
        if table not in connection.introspection.table_names():
            return
        with connection.cursor() as cursor:
            existing_columns = {column.name for column in connection.introspection.get_table_description(cursor, table)}
        if field_names is None:
            fields = [field for field in model._meta.local_fields if not field.auto_created]
        else:
            fields = [model._meta.get_field(field_name) for field_name in field_names]
        for field in fields:
            if field.column not in existing_columns:
                schema_editor.add_field(model, field)
                self.stdout.write(self.style.SUCCESS(f'Added column: {table}.{field.column}'))

    def rename_existing_managers(self):
        """Eski menenjer ismlarini filial nomi asosida yangilaydi."""
        managers = list(AppUser.objects.filter(role='filial_rahbari'))
        changed = []
        for manager in managers:
            # Boss yoki admin tahrirlagan ism-familiyani deploy paytida qayta
            # filial nomiga almashtirmaymiz. Faqat nomi bo‘sh yoki login bilan
            # bir xil bo‘lgan eski akkauntlar avtomatik to‘ldiriladi.
            current_name = str(manager.full_name or '').strip()
            if current_name and current_name != manager.username:
                continue
            branches = [item.strip() for item in str(manager.branch_name or '').split(',') if item.strip()]
            names = []
            for branch in branches:
                display_name = 'Olmazor' if branch == 'Olmozor' else branch
                name = f'{display_name} Menenjeri'
                if name not in names:
                    names.append(name)
            new_name = ', '.join(names) or manager.username
            if manager.full_name != new_name:
                manager.full_name = new_name
                changed.append(manager)
        if changed:
            AppUser.objects.bulk_update(changed, ['full_name'])
            self.stdout.write(self.style.SUCCESS(f'{len(changed)} ta eski menenjer nomi yangilandi.'))

    def remove_branch_unique_constraints(self, schema_editor):
        # Eski bazada branch_name unique bo'lib qolgan bo'lsa olib tashlaydi.
        # Operator va menenjerlarda bitta filialga bir nechta odam biriktirish mumkin.
        table = AppUser._meta.db_table
        if table not in connection.introspection.table_names():
            return
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, table)

        table_name = schema_editor.quote_name(table)
        for name, info in constraints.items():
            columns = info.get('columns') or []
            if not info.get('unique') or 'branch_name' not in columns:
                continue
            # username unique qolishi kerak, faqat filial bo'yicha eski cheklovni olib tashlaymiz.
            if columns == ['username']:
                continue
            quoted_name = schema_editor.quote_name(name)
            try:
                if connection.vendor == 'postgresql' and not info.get('index'):
                    schema_editor.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {quoted_name}')
                else:
                    schema_editor.execute(f'DROP INDEX IF EXISTS {quoted_name}')
                self.stdout.write(self.style.SUCCESS(f'Removed old branch unique constraint/index: {name}'))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Could not remove branch unique constraint/index {name}: {exc}'))


    def handle(self, *args, **options):
        models = [AppUser, Lead, LeadStatusHistory, OnlineLead, LeadVisitDecision, LeadVisitDecisionHistory, ExcelImport, ExcelImportRow, DataAuditLog]
        existing = set(connection.introspection.table_names())
        with connection.schema_editor() as schema_editor:
            for model in models:
                if model._meta.db_table not in existing:
                    schema_editor.create_model(model)
                    self.stdout.write(self.style.SUCCESS(f'Created table: {model._meta.db_table}'))

            # Productionda jadval allaqachon bor bo'lsa, yangi qo'shilgan ustunlarni
            # xavfsiz tarzda qo'shib ketadi. Mavjud ma'lumotlar o'chmaydi.
            for model in models:
                self.ensure_missing_columns(schema_editor, model)
            self.remove_branch_unique_constraints(schema_editor)
        self.rename_existing_managers()
        self.backfill_sale_lead_branches()
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin12345')
        full_name = os.getenv('ADMIN_FULL_NAME', 'Administrator')
        phone = os.getenv('ADMIN_PHONE', '')
        if not AppUser.objects.filter(role='admin', is_active=True).exists():
            AppUser.objects.create(username=username, password_hash=make_password(password), full_name=full_name, phone=phone, role='admin', is_active=True)
            self.stdout.write(self.style.SUCCESS(f'Default admin yaratildi: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin allaqachon mavjud.'))
