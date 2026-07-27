from unittest.mock import patch
import json

from django.test import Client, TestCase

from .auth import issue_tokens
from .models import AppUser, Lead, LeadStatusHistory, LeadVisitDecision


class ManagerCreatedAfterSaleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.operator = AppUser.objects.create(
            username='operator-old',
            password_hash='unused',
            full_name='Operator',
            role='operator',
            branch_name='Niyozbosh',
        )

    def auth_headers(self, user):
        token = issue_tokens(user)['access']
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_manager_created_after_sale_can_see_and_mark_old_sale(self):
        # Eski import filiali branch_name ichida qolgan, sotuv filiali esa tarixda.
        lead = Lead.objects.create(
            full_name='Test Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Eski import markazi',
        )
        LeadStatusHistory.objects.create(
            lead=lead,
            old_status='new',
            new_status='sale',
            changed_by=self.operator,
            note='Sotuv qilindi | Filial: Niyazbosh',
        )

        # Menenjer sotuvdan keyin yaratiladi.
        manager = AppUser.objects.create(
            username='manager-new',
            password_hash='unused',
            full_name='Niyozbosh Menenjeri',
            role='filial_rahbari',
            branch_name='Niyozbosh',
        )

        response = self.client.get('/api/boss/leads/', **self.auth_headers(manager))
        self.assertEqual(response.status_code, 200)
        self.assertIn(lead.id, [item['id'] for item in response.json()])

        response = self.client.post(
            f'/api/boss/leads/{lead.id}/visit-decision/',
            data=json.dumps({'decision': 'arrived'}),
            content_type='application/json',
            **self.auth_headers(manager),
        )
        self.assertEqual(response.status_code, 200)
        decision = LeadVisitDecision.objects.get(lead=lead)
        self.assertEqual(decision.decision, 'arrived')
        self.assertEqual(decision.decided_by_id, manager.id)

    def test_manager_created_after_sale_can_mark_not_arrived(self):
        lead = Lead.objects.create(
            full_name='Kelmadi Test Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Eski import markazi',
        )
        LeadStatusHistory.objects.create(
            lead=lead,
            old_status='new',
            new_status='sale',
            changed_by=self.operator,
            note='Sotuv qilindi | Filial: Niyozbosh',
        )
        manager = AppUser.objects.create(
            username='manager-not-arrived',
            password_hash='unused',
            full_name='Yangi Menenjer',
            role='filial_rahbari',
            branch_name='Niyozbosh',
        )

        response = self.client.post(
            f'/api/boss/leads/{lead.id}/visit-decision/',
            data=json.dumps({'decision': 'not_arrived'}),
            content_type='application/json',
            **self.auth_headers(manager),
        )
        self.assertEqual(response.status_code, 200)
        decision = LeadVisitDecision.objects.get(lead=lead, decided_by=manager)
        self.assertEqual(decision.decision, 'not_arrived')

    def test_new_manager_gets_own_not_arrived_row_without_reassigning_old_one(self):
        lead = Lead.objects.create(
            full_name='Old Manager Decision Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Niyozbosh',
        )
        old_manager = AppUser.objects.create(
            username='old-manager-kelmadi',
            password_hash='unused',
            full_name='Old Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
            is_active=False,
        )
        old_decision = LeadVisitDecision.objects.create(
            lead=lead,
            decided_by=old_manager,
            decision='not_arrived',
        )
        new_manager = AppUser.objects.create(
            username='new-manager-kelmadi',
            password_hash='unused',
            full_name='New Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
        )

        response = self.client.post(
            f'/api/boss/leads/{lead.id}/visit-decision/',
            data=json.dumps({'decision': 'not_arrived'}),
            content_type='application/json',
            **self.auth_headers(new_manager),
        )
        self.assertEqual(response.status_code, 200)
        old_decision.refresh_from_db()
        self.assertEqual(old_decision.decided_by_id, old_manager.id)
        self.assertTrue(LeadVisitDecision.objects.filter(
            lead=lead,
            decided_by=new_manager,
            decision='not_arrived',
        ).exists())

    def test_other_branch_manager_cannot_manage_sale(self):
        lead = Lead.objects.create(
            full_name='Other Branch Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Niyozbosh',
        )
        manager = AppUser.objects.create(
            username='manager-other',
            password_hash='unused',
            full_name='Gulbahor Menenjeri',
            role='filial_rahbari',
            branch_name='Gulbahor',
        )

        response = self.client.get('/api/boss/leads/', **self.auth_headers(manager))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(lead.id, [item['id'] for item in response.json()])

        response = self.client.post(
            f'/api/boss/leads/{lead.id}/visit-decision/',
            data=json.dumps({'decision': 'arrived'}),
            content_type='application/json',
            **self.auth_headers(manager),
        )
        self.assertEqual(response.status_code, 403)

    def test_new_manager_can_mark_arrived_after_old_manager_not_arrived(self):
        lead = Lead.objects.create(
            full_name='Transferred Decision Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Niyozbosh',
        )
        old_manager = AppUser.objects.create(
            username='manager-old',
            password_hash='unused',
            full_name='Old Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
            is_active=False,
        )
        old_decision = LeadVisitDecision.objects.create(
            lead=lead,
            decided_by=old_manager,
            decision='not_arrived',
        )
        new_manager = AppUser.objects.create(
            username='manager-replacement',
            password_hash='unused',
            full_name='New Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
        )

        response = self.client.post(
            f'/api/boss/leads/{lead.id}/visit-decision/',
            data=json.dumps({'decision': 'arrived'}),
            content_type='application/json',
            **self.auth_headers(new_manager),
        )
        self.assertEqual(response.status_code, 200)
        old_decision.refresh_from_db()
        self.assertEqual(old_decision.decision, 'not_arrived')
        self.assertEqual(old_decision.decided_by_id, old_manager.id)
        self.assertTrue(LeadVisitDecision.objects.filter(
            lead=lead,
            decided_by=new_manager,
            decision='arrived',
        ).exists())


class ManagerPaymentStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.operator = AppUser.objects.create(
            username='payment-operator',
            password_hash='unused',
            full_name='Payment Operator',
            role='operator',
            branch_name='Niyozbosh',
        )
        self.old_manager = AppUser.objects.create(
            username='payment-old-manager',
            password_hash='unused',
            full_name='Old Payment Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
            is_active=False,
        )
        self.new_manager = AppUser.objects.create(
            username='payment-new-manager',
            password_hash='unused',
            full_name='New Payment Manager',
            role='filial_rahbari',
            branch_name='Niyozbosh',
        )
        self.lead = Lead.objects.create(
            full_name='Payment Test Lead',
            assigned_operator=self.operator,
            current_status='sale',
            branch_name='Niyozbosh',
        )
        self.decision = LeadVisitDecision.objects.create(
            lead=self.lead,
            decided_by=self.old_manager,
            decision='arrived',
        )

    def auth_headers(self):
        token = issue_tokens(self.new_manager)['access']
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_new_manager_can_mark_old_arrived_lead_as_paid(self):
        response = self.client.post(
            f'/api/boss/leads/{self.lead.id}/payment-done/',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_done)
        self.assertFalse(self.decision.payment_not_done)
        self.assertEqual(self.decision.payment_done_by_id, self.new_manager.id)

    def test_new_manager_can_mark_old_arrived_lead_as_unpaid(self):
        response = self.client.post(
            f'/api/boss/leads/{self.lead.id}/payment-not-done/',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_not_done)
        self.assertFalse(self.decision.payment_done)
        self.assertEqual(self.decision.payment_not_done_by_id, self.new_manager.id)

    def test_unified_payment_endpoint_accepts_lead_id(self):
        response = self.client.post(
            f'/api/boss/leads/{self.lead.id}/payment-status/',
            data=json.dumps({'status': 'paid'}),
            content_type='application/json',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_done)
        self.assertEqual(response.json().get('payment_status'), 'paid')

    def test_unified_payment_endpoint_accepts_decision_id_as_fallback(self):
        response = self.client.post(
            f'/api/boss/leads/{self.decision.id}/payment-status/',
            data=json.dumps({'status': 'unpaid'}),
            content_type='application/json',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_not_done)
        self.assertEqual(self.decision.payment_not_done_by_id, self.new_manager.id)

    @patch('core.views.visit_decision_to_dict', side_effect=RuntimeError('serializer unavailable'))
    def test_serializer_failure_does_not_turn_saved_payment_into_500(self, _serializer):
        response = self.client.post(
            f'/api/boss/leads/{self.lead.id}/payment-status/',
            data=json.dumps({'status': 'paid'}),
            content_type='application/json',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_done)
        self.assertTrue(response.json().get('saved'))

    @patch('core.views.DataAuditLog.objects.create', side_effect=RuntimeError('audit unavailable'))
    def test_audit_failure_does_not_rollback_paid_status(self, _audit_create):
        response = self.client.post(
            f'/api/boss/leads/{self.lead.id}/payment-done/',
            **self.auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.decision.refresh_from_db()
        self.assertTrue(self.decision.payment_done)
        self.assertEqual(self.decision.payment_done_by_id, self.new_manager.id)


class OperatorPhoneUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.operator = AppUser.objects.create(
            username='phone-operator',
            password_hash='unused',
            full_name='Phone Operator',
            role='operator',
        )
        self.other_operator = AppUser.objects.create(
            username='other-phone-operator',
            password_hash='unused',
            full_name='Other Operator',
            role='operator',
        )
        self.lead = Lead.objects.create(
            full_name='Phone Test Lead',
            phone1='+998901112233',
            assigned_operator=self.operator,
            current_status='new',
        )

    def auth_headers(self, user):
        token = issue_tokens(user)['access']
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_operator_can_add_phone2_and_phone3_to_own_lead(self):
        response = self.client.patch(
            f'/api/operator/leads/{self.lead.id}/update-phones/',
            data=json.dumps({'phone2': '91 222 33 44'}),
            content_type='application/json',
            **self.auth_headers(self.operator),
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.phone2, '+998912223344')
        self.assertEqual(response.json()['phone2'], '+998912223344')

        response = self.client.patch(
            f'/api/operator/leads/{self.lead.id}/update-phones/',
            data=json.dumps({'phone3': '+998 93 555 66 77'}),
            content_type='application/json',
            **self.auth_headers(self.operator),
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.phone3, '+998935556677')

    def test_operator_cannot_update_another_operators_lead(self):
        response = self.client.patch(
            f'/api/operator/leads/{self.lead.id}/update-phones/',
            data=json.dumps({'phone2': '+998901234567'}),
            content_type='application/json',
            **self.auth_headers(self.other_operator),
        )
        self.assertEqual(response.status_code, 403)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.phone2, '')

    def test_duplicate_phone_inside_same_lead_is_rejected(self):
        response = self.client.patch(
            f'/api/operator/leads/{self.lead.id}/update-phones/',
            data=json.dumps({'phone2': self.lead.phone1}),
            content_type='application/json',
            **self.auth_headers(self.operator),
        )
        self.assertEqual(response.status_code, 400)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.phone2, '')


class OperatorVisitDecisionReclassifyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.boss = AppUser.objects.create(
            username='reclassify-boss', password_hash='unused', full_name='Boss', role='boss'
        )
        self.operator = AppUser.objects.create(
            username='reclassify-operator', password_hash='unused', full_name='Operator',
            role='operator', boss=self.boss, branch_name='Niyozbosh,Gulbahor'
        )
        self.other_operator = AppUser.objects.create(
            username='other-reclassify-operator', password_hash='unused', full_name='Other Operator',
            role='operator', boss=self.boss, branch_name='Gulbahor'
        )
        self.manager = AppUser.objects.create(
            username='reclassify-manager', password_hash='unused', full_name='Gulbahor Menenjeri',
            role='filial_rahbari', branch_name='Gulbahor'
        )
        self.lead = Lead.objects.create(
            full_name='Qayta yuboriladigan lead', assigned_operator=self.operator,
            boss=self.boss, current_status='sale', branch_name='Niyozbosh'
        )
        self.decision = LeadVisitDecision.objects.create(
            lead=self.lead, decided_by=self.manager, decision='not_arrived'
        )

    def auth_headers(self, user):
        token = issue_tokens(user)['access']
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_operator_can_resend_sale_to_selected_manager(self):
        response = self.client.post(
            f'/api/operator/lead-visit-decisions/{self.decision.id}/reclassify/',
            data=json.dumps({'status': 'sale', 'selected_branch': 'Gulbahor'}),
            content_type='application/json',
            **self.auth_headers(self.operator),
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.current_status, 'sale')
        self.assertEqual(self.lead.branch_name, 'Gulbahor')
        self.assertFalse(LeadVisitDecision.objects.filter(lead=self.lead).exists())

        manager_response = self.client.get('/api/boss/leads/', **self.auth_headers(self.manager))
        self.assertEqual(manager_response.status_code, 200)
        self.assertIn(self.lead.id, [row['id'] for row in manager_response.json()])

    def test_operator_can_move_card_to_otkaz_without_manager(self):
        response = self.client.post(
            f'/api/operator/lead-visit-decisions/{self.decision.id}/reclassify/',
            data=json.dumps({'status': 'otkaz'}),
            content_type='application/json',
            **self.auth_headers(self.operator),
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.current_status, 'otkaz')
        self.assertFalse(LeadVisitDecision.objects.filter(lead=self.lead).exists())

        manager_response = self.client.get('/api/boss/leads/', **self.auth_headers(self.manager))
        self.assertEqual(manager_response.status_code, 200)
        self.assertNotIn(self.lead.id, [row['id'] for row in manager_response.json()])

    def test_other_operator_cannot_reclassify_card(self):
        response = self.client.post(
            f'/api/operator/lead-visit-decisions/{self.decision.id}/reclassify/',
            data=json.dumps({'status': 'otkaz'}),
            content_type='application/json',
            **self.auth_headers(self.other_operator),
        )
        self.assertEqual(response.status_code, 404)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.current_status, 'sale')
        self.assertTrue(LeadVisitDecision.objects.filter(id=self.decision.id).exists())
