import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken
from .models import Greeting
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
        self.assertEqual(response_data, {'error': 'username and password are required'})

    def test_missing_password(self):
        data = {'username': 'testuser'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'username and password are required'})




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

    def test_padded_hello_still_gets_goodbye(self):
        token=create_access_token(User.objects.get(username='testuser'))
        response=self.client.post(reverse('greetingendpoint'), json.dumps({'greeting':'  Hello '}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {token.token}')
        self.assertEqual(response.json(),{'message':'Goodbye!'})
        self.assertTrue(Greeting.objects.filter(greeting='Hello').exists())

    def test_greeting_requires_a_bearer_token(self):
        response=self.client.post(reverse('greetingendpoint'), json.dumps({'greeting':'hello'}), content_type='application/json')
        self.assertIn(response.status_code,[401,403])

    def test_unknown_user_is_rejected(self):
        data = {'username': 'nobody', 'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'User did not authenticate'})

    def test_malformed_json_is_rejected(self):
        response = self.client.post(reverse('signin'), '{"username":', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid JSON data'})

    def test_get_is_not_allowed(self):
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 405)

    def test_issued_token_expires_in_one_hour(self):
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        token = AccessToken.objects.get(token=response.json()['access_token'])
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.scope, 'read write')
        remaining = token.expires - timezone.now()
        self.assertTrue(timedelta(minutes=59) < remaining <= timedelta(hours=1))


class GreetingEndpointTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='greeter', password='greeterpassword')
        self.token = create_access_token(self.user)

    def post_greeting(self, body, token=None):
        token = token or self.token.token
        return self.client.post(
            reverse('greetingendpoint'), body, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {token}'
        )

    def test_other_text_is_received_and_stored(self):
        response = self.post_greeting(json.dumps({'greeting': 'good morning'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Greeting received!'})
        self.assertEqual(list(Greeting.objects.values_list('greeting', flat=True)), ['good morning'])

    def test_blank_greeting_is_rejected(self):
        response = self.post_greeting(json.dumps({'greeting': '   '}))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Greeting.objects.exists())

    def test_non_string_greeting_is_rejected(self):
        response = self.post_greeting(json.dumps({'greeting': 42}))
        self.assertEqual(response.status_code, 400)

    def test_malformed_json_is_rejected(self):
        response = self.post_greeting('not json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid JSON data'})

    def test_get_with_valid_token_is_not_allowed(self):
        response = self.client.get(reverse('greetingendpoint'), HTTP_AUTHORIZATION=f'Bearer {self.token.token}')
        self.assertEqual(response.status_code, 405)

    def test_unknown_token_is_rejected(self):
        response = self.post_greeting(json.dumps({'greeting': 'hello'}), token='not-a-real-token')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Greeting.objects.exists())

    def test_expired_token_is_rejected(self):
        self.token.expires = timezone.now() - timedelta(seconds=1)
        self.token.save()
        response = self.post_greeting(json.dumps({'greeting': 'hello'}))
        self.assertEqual(response.status_code, 403)
