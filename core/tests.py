import json
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from oauth2_provider.models import AccessToken
from .views import create_access_token

class SignInViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_valid_credentials(self):
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('access_token', response_data)

    def test_invalid_credentials(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'User did not authenticate'})

    def test_missing_username(self):
        data = {'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'Invalid JSON data'})

    def test_missing_password(self):
        data = {'username': 'testuser'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'Invalid JSON data'})




    def test_nonobject_payload_is_rejected(self):
        response=self.client.post(reverse('signin'), '[]', content_type='application/json')
        self.assertEqual(response.status_code,400)

    def test_inactive_account_is_rejected(self):
        user=User.objects.get(username='testuser')
        user.set_password("synthetic-inactive-test-password")
        user.is_active=False
        user.save()
        response=self.client.post(reverse('signin'), json.dumps({'username':'testuser','password':'synthetic-inactive-test-password'}), content_type='application/json')
        self.assertEqual(response.status_code,400)

    def test_bearer_token_can_submit_a_greeting(self):
        token=create_access_token(User.objects.get(username='testuser'))
        response=self.client.post(reverse('greetingendpoint'), json.dumps({'greeting':'hello'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {token.token}')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),{'message':'Goodbye!'})

    def test_greeting_requires_a_bearer_token(self):
        response=self.client.post(reverse('greetingendpoint'), json.dumps({'greeting':'hello'}), content_type='application/json')
        self.assertIn(response.status_code,[401,403])
