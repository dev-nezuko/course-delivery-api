# import json
# from django.test import TestCase, Client
# from django.contrib.auth.models import User
# from django.utils import timezone
# from dateutil.relativedelta import relativedelta
# from oauth2_provider.models import Application, AccessToken
# from .models import Greeting
# from .views import create_access_token
# import pdb

# # class GreetingViewTestCase(TestCase):
# #     def setUp(self):
# #         self.client = Client()

# #     def test_post_valid_greeting(self):
# #         data = {'greeting': 'Hello'}
# #         response = self.client.post('/greeting/', json.dumps(data), content_type='application/json')
# #         self.assertEqual(response.status_code, 200)
# #         self.assertEqual(json.loads(response.content), {'message': 'Goodbye!'})
# #         self.assertEqual(Greeting.objects.count(), 1)

# #     def test_post_invalid_json(self):
# #         response = self.client.post('/greeting/', 'invalid_json', content_type='application/json')
# #         self.assertEqual(response.status_code, 400)
# #         self.assertEqual(json.loads(response.content), {'error': 'Invalid JSON data'})

#     # More test cases for different scenarios...

# class SignInViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')

#     def test_post_valid_credentials(self):
#         data = {'username': 'testuser', 'password': 'testpassword'}
#         pdb.set_trace()
#         response = self.client.post('signin', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('access_token', json.loads(response.content))

#     def test_post_invalid_credentials(self):
#         data = {'username': 'testuser', 'password': 'wrongpassword'}
#         response = self.client.post('/signin/', json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(json.loads(response.content), {'error': 'User did not authenticate'})

#     # More test cases for different scenarios...

# class AccessTokenTestCase(TestCase):
#     def test_create_access_token(self):
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         app = Application.objects.create(name='TestApp', client_type='confidential', authorization_grant_type='password')
#         access_token = create_access_token(user)
#         self.assertIsInstance(access_token, AccessToken)
#         self.assertEqual(access_token.user, user)
#         self.assertEqual(access_token.application, app)
#         self.assertLessEqual(access_token.expires, timezone.now() + relativedelta(hours=1))

#     # More test cases for different scenarios...

# # Additional test cases and edge cases can be added to increase coverage.



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

    # Add more test cases as needed...

# class AccessTokenTestCase(TestCase):
#     def test_create_access_token(self):
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         app = Application.objects.create(name='TestApp', client_type='confidential', authorization_grant_type='password')
#         access_token = create_access_token(user)
#         self.assertIsInstance(access_token, AccessToken)
#         self.assertEqual(access_token.user, user)
#         self.assertEqual(access_token.application, app)
#         self.assertLessEqual(access_token.expires, timezone.now() + relativedelta(hours=1))

    # More test cases for different scenarios...
