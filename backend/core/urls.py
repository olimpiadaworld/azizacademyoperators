from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('health', views.health),
    path('auth/login/', views.login_view),
    path('auth/refresh/', views.refresh_view),
    path('auth/me/', views.me_view),

    path('admin/bosses/', views.admin_bosses),
    path('admin/bosses/<int:user_id>/', views.admin_bosses),
    path('admin/filial-rahbarlari/', views.admin_filial_rahbarlari),
    path('admin/filial-rahbarlari/<int:user_id>/', views.admin_filial_rahbarlari),
    path('admin/users/', views.admin_users),
    path('admin/users/<int:user_id>/', views.admin_users),
    path('admin/leads/', views.admin_leads),
    path('admin/statistics/', views.admin_statistics),
    path('admin/lead-visit-decisions/', views.admin_visit_decisions),
    path('admin/operator-report/', views.admin_operator_report),
    path('admin/reports/all-excel/', views.admin_all_reports_excel),
    path('admin/telegram/test/', views.telegram_test),

    path('boss/operators/', views.boss_operators),
    path('boss/operators/<int:user_id>/', views.boss_operators),
    path('boss/leads/', views.boss_leads),
    path('boss/leads/import/template/', views.import_template),
    path('boss/leads/import/', views.import_leads),
    path('boss/leads/<int:lead_id>/visit-decision/', views.visit_decision),
    path('boss/leads/<int:lead_id>/payment-done/', views.mark_visit_payment),
    path('boss/lead-visit-decisions/', views.lead_visit_decisions),
    path('boss/online-leads/', views.boss_online_leads),
    path('boss/online-leads/<int:online_id>/assign/', views.assign_online_lead),
    path('boss/online-leads/bulk-assign/', views.bulk_assign_online_leads),
    path('boss/statistics/', views.boss_statistics),
    path('boss/statistics/full-report/', views.boss_full_report),
    path('boss/statistics/daily-report/', views.boss_daily_report_excel),
    path('boss/statistics/full-report-excel/', views.boss_full_report_excel),

    path('operator/leads/', views.operator_leads),
    path('operator/leads/<int:lead_id>/change-status/', views.change_status),
    path('operator/leads/<int:lead_id>/reminder/', views.set_reminder),
    path('operator/reminders/', views.reminders),
    path('operator/online-leads/', views.operator_online_leads),
    path('operator/daily-results/', views.operator_daily_results),
    path('operator/daily-history/', views.operator_daily_history),

    path('public/online-leads/', views.public_online_leads),
]
