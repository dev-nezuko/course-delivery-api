# OAuth-protected greeting exercise

A small Django exercise in credential checking, bearer-token creation, and a protected JSON endpoint. A signed-in user sends a greeting; `hello` produces `Goodbye!`, and other text produces `Greeting received!`. Accepted greetings are stored in SQLite.

The repository name comes from its original context, but the implementation does not contain courses, enrollment, lessons, or an LMS. The useful example here is the request/authentication path.

## Try it locally

The original requirements capture a broad historical development environment. For this exercise, the relevant components are Django 4.2, Django OAuth Toolkit 2.3, OAuthlib, python-dateutil, Pillow for the existing profile model, and DRF configuration. Use an isolated environment rather than installing the full list globally.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

An OAuth application record can be created through the toolkit/admin interface. The sign-in helper selects the first stored application when present; it is an exercise shortcut, not a complete client-authenticated authorization-server flow.

```http
POST /signin
Content-Type: application/json

{"username":"<local test user>","password":"<local test password>"}
```

A successful response contains `access_token`; do not paste real responses into logs, README examples, or screenshots. Send it only in the authorization header:

```http
POST /greeting
Authorization: Bearer <local test token>
Content-Type: application/json

{"greeting":"hello"}
```

Expected JSON is `{"message":"Goodbye!"}`. The routes have **no trailing slash**. Sign-in and greeting accept POST; malformed input returns a client error. Inactive users no longer receive a token through the sign-in shortcut. Tokens expire after one hour.

## Keep the scope small

The default mode is local development. A fresh process-local signing secret is generated when no `DJANGO_SECRET_KEY` is supplied; set a stable private value if sessions must survive restarts. `DJANGO_DEBUG=0` requires that variable. Never reuse an old committed development signing key for deployment.

There is no sign-in throttling, production client-authorization flow, audit trail, or account enrollment API. TLS, deployment settings, and token lifecycle policy need separate work before shared use. The unrelated `Profile` model is present, but no profile-management flow is implemented.

## Checks

```sh
python manage.py test core
```

Eight tests cover valid/invalid credentials, required fields, nonobject JSON, inactive accounts, and authorized/unauthorized greeting requests. They do not establish a full external OAuth flow. Unused font files with valid magic and no application references, obsolete publisher ignore entries, tracked IDE files, and commented-out test scaffolding were removed in the normal project update.
