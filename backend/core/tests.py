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

    def test_new_manager_takes_over_old_not_arrived_decision(self):
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
        decision = LeadVisitDecision.objects.create(
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
        decision.refresh_from_db()
        self.assertEqual(decision.decision, 'arrived')
        self.assertEqual(decision.decided_by_id, new_manager.id)
