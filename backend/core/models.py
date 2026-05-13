from django.db import models
from django.utils import timezone


class AppUser(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('boss', 'Boss'),
        ('operator', 'Operator'),
        ('filial_rahbari', 'Filial rahbari'),
    )
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.TextField()
    full_name = models.CharField(max_length=255, default='', blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='operator')
    phone = models.CharField(max_length=30, default='', blank=True)
    boss = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='boss_id', related_name='operators')
    branch_name = models.CharField(max_length=255, default='', blank=True)
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'app_users'

    def __str__(self):
        return self.full_name or self.username


class Lead(models.Model):
    full_name = models.CharField(max_length=255, default='', blank=True)
    tsh = models.CharField(max_length=100, default='', blank=True)
    subject = models.CharField(max_length=255, default='', blank=True)
    ball = models.CharField(max_length=50, default='', blank=True)
    phone1 = models.CharField(max_length=50, default='', blank=True)
    phone2 = models.CharField(max_length=50, default='', blank=True)
    phone3 = models.CharField(max_length=50, default='', blank=True)
    school = models.CharField(max_length=255, default='', blank=True)
    grade = models.CharField(max_length=100, default='', blank=True)
    branch_name = models.CharField(max_length=255, default='', blank=True)
    assigned_operator = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='assigned_operator_id', related_name='assigned_leads')
    boss = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='boss_id', related_name='boss_leads')
    uploaded_by = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='uploaded_by_id', related_name='uploaded_leads')
    current_status = models.CharField(max_length=30, default='new')
    reminder_at = models.DateTimeField(null=True, blank=True)
    reminder_note = models.CharField(max_length=255, default='', blank=True)
    reminder_last_notified_at = models.DateTimeField(null=True, blank=True)
    source_row_number = models.IntegerField(default=0)
    is_duplicate = models.BooleanField(default=False)
    duplicate_of_lead = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='duplicate_of_lead_id')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'leads'
        indexes = [models.Index(fields=['assigned_operator']), models.Index(fields=['boss']), models.Index(fields=['current_status']), models.Index(fields=['created_at']), models.Index(fields=['branch_name'])]


class LeadStatusHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, db_column='lead_id', related_name='history_rows')
    old_status = models.CharField(max_length=30, default='new')
    new_status = models.CharField(max_length=30, default='new')
    changed_by = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='changed_by_id')
    note = models.CharField(max_length=500, default='', blank=True)
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'lead_status_history'
        indexes = [models.Index(fields=['lead']), models.Index(fields=['changed_by']), models.Index(fields=['changed_at'])]


class OnlineLead(models.Model):
    full_name = models.CharField(max_length=255, default='', blank=True)
    tsh = models.CharField(max_length=100, default='', blank=True)
    school = models.CharField(max_length=255, default='', blank=True)
    grade = models.CharField(max_length=100, default='', blank=True)
    subject = models.CharField(max_length=255, default='', blank=True)
    age = models.IntegerField(default=0)
    phone1 = models.CharField(max_length=50, default='', blank=True)
    phone2 = models.CharField(max_length=50, default='', blank=True)
    phone3 = models.CharField(max_length=50, default='', blank=True)
    interest_subject = models.CharField(max_length=255, default='', blank=True)
    region = models.CharField(max_length=50, default='', blank=True)
    assigned_boss = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='assigned_boss_id', related_name='online_boss_leads')
    assigned_operator = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='assigned_operator_id', related_name='online_operator_leads')
    created_lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, db_column='created_lead_id')
    source_payload = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    assigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'online_leads'
        indexes = [models.Index(fields=['assigned_boss']), models.Index(fields=['assigned_operator'])]


class LeadVisitDecision(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, db_column='lead_id', related_name='visit_decisions')
    decided_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, db_column='decided_by_id')
    decision = models.CharField(max_length=20)
    payment_done = models.BooleanField(default=False)
    payment_done_at = models.DateTimeField(null=True, blank=True)
    payment_done_by = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='payment_done_by_id', related_name='payment_confirmed_decisions')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'lead_visit_decisions'
        unique_together = ('lead', 'decided_by')


class LeadVisitDecisionHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, db_column='lead_id')
    decided_by = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='decided_by_id')
    old_decision = models.CharField(max_length=20, default='', blank=True)
    new_decision = models.CharField(max_length=20, default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'lead_visit_decision_history'


class ExcelImport(models.Model):
    uploaded_by = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='uploaded_by_id', related_name='excel_uploads')
    assigned_operator = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='assigned_operator_id')
    filename = models.CharField(max_length=255, default='', blank=True)
    total_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    duplicate_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'excel_imports'


class ExcelImportRow(models.Model):
    import_record = models.ForeignKey(ExcelImport, on_delete=models.CASCADE, db_column='import_id', related_name='rows')
    source_row_number = models.IntegerField(default=0)
    raw_data = models.JSONField(default=dict, blank=True)
    normalized_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=30, default='saved')
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, db_column='lead_id')
    duplicate_of_lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, db_column='duplicate_of_lead_id', related_name='duplicate_import_rows')
    error_message = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'excel_import_rows'


class DataAuditLog(models.Model):
    actor = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL, db_column='actor_id')
    entity_type = models.CharField(max_length=50, default='', blank=True)
    entity_id = models.IntegerField(default=0)
    action = models.CharField(max_length=50, default='', blank=True)
    old_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'data_audit_logs'
        indexes = [models.Index(fields=['entity_type', 'entity_id']), models.Index(fields=['actor'])]
