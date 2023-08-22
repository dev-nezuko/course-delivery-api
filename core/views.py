from django.http import JsonResponse
from django.contrib.auth import authenticate
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
            if not isinstance(data, dict):
                raise ValueError
            greeting_text = data.get('greeting', '')
            if not isinstance(greeting_text, str) or not greeting_text.strip():
                return JsonResponse({'error': 'A nonempty greeting string is required'}, status=400)

            greeting_instance = Greeting.objects.create(greeting=greeting_text)

            if greeting_text.lower() == 'hello':
                message = 'Goodbye!'
            else:
                message = 'Greeting received!'

            return JsonResponse({'message': message}, status=200)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


@csrf_exempt
def signin(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        if not isinstance(data, dict):
            raise ValueError
        username = data.get('username')
        password = data.get('password')
        if not isinstance(username, str) or not isinstance(password, str) or not username.strip() or not password:
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'User did not authenticate'}, status=400)
    access_token = create_access_token(user)
    return JsonResponse({'access_token': access_token.token}, status=200)


def create_access_token(user):
    tok = generate_token()
    app = Application.objects.first()
    access_token = AccessToken.objects.create(
        user=user,
        application=app,
        expires=timezone.now() + relativedelta(hours=1),
        token=tok,
        scope="read write",
    )
    return access_token
