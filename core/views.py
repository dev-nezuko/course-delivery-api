from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from oauth2_provider.decorators import protected_resource
from django.views.decorators.csrf import csrf_exempt
from .models import Greeting
from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, Application
from django.utils import timezone
from dateutil.relativedelta import relativedelta


@csrf_exempt
@protected_resource()
def greetingendpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            greeting_text = data.get('greeting', '')

            greeting_instance = Greeting.objects.create(greeting=greeting_text)
            greeting_instance.save()

            if greeting_text.lower() == 'hello':
                message = 'Goodbye!'
            else:
                message = 'Greeting received!'

            return JsonResponse({'message': message}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username', '')
            password = data.get('password', '')

            user = User.objects.filter(username=username).first()
            if user and user.password == password:
                access_token = create_access_token(user)
                return JsonResponse({'access_token': access_token.token}, status=200)
            else:
                return JsonResponse({'error': 'User did not authenticate'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def create_access_token(user):
    tok = generate_token()
    app = Application.objects.first()
    access_token = AccessToken.objects.create(
        user=user,
        application=app,
        expires=timezone.now() + relativedelta(hours=1),
        token=tok
    )
    return access_token
