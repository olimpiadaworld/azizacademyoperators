import os
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password
from core.models import AppUser, Lead, LeadStatusHistory, OnlineLead, LeadVisitDecision, LeadVisitDecisionHistory, ExcelImport, ExcelImportRow, DataAuditLog


class Command(BaseCommand):
    help = 'Create database tables if missing and create first admin user.'

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
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin12345')
        full_name = os.getenv('ADMIN_FULL_NAME', 'Administrator')
        phone = os.getenv('ADMIN_PHONE', '')
        if not AppUser.objects.filter(role='admin', is_active=True).exists():
            AppUser.objects.create(username=username, password_hash=make_password(password), full_name=full_name, phone=phone, role='admin', is_active=True)
            self.stdout.write(self.style.SUCCESS(f'Default admin yaratildi: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin allaqachon mavjud.'))
