import os
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password
from core.models import AppUser, Lead, LeadStatusHistory, OnlineLead, LeadVisitDecision, LeadVisitDecisionHistory, ExcelImport, ExcelImportRow, DataAuditLog


class Command(BaseCommand):
    help = 'Create database tables if missing and create first admin user.'

    def ensure_missing_columns(self, schema_editor, model, field_names):
        table = model._meta.db_table
        with connection.cursor() as cursor:
            existing_columns = {column.name for column in connection.introspection.get_table_description(cursor, table)}
        for field_name in field_names:
            field = model._meta.get_field(field_name)
            if field.column not in existing_columns:
                schema_editor.add_field(model, field)
                self.stdout.write(self.style.SUCCESS(f'Added column: {table}.{field.column}'))


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
            self.ensure_missing_columns(schema_editor, OnlineLead, ['tsh', 'school', 'grade', 'subject'])
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin12345')
        full_name = os.getenv('ADMIN_FULL_NAME', 'Administrator')
        phone = os.getenv('ADMIN_PHONE', '')
        if not AppUser.objects.filter(role='admin', is_active=True).exists():
            AppUser.objects.create(username=username, password_hash=make_password(password), full_name=full_name, phone=phone, role='admin', is_active=True)
            self.stdout.write(self.style.SUCCESS(f'Default admin yaratildi: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin allaqachon mavjud.'))
