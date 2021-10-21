# Using djmongoauth

## What is it?
`djmongoauth` provides out-of-the-box support for basic user management and additional operations including user registration, login, logout, email verification, password recovery for backends built with the Django web framework and MongoDB.

`djmongoauth` is based on `djongo`, a MongoDB ORM for Django.

## Use cases
### User object
User object is the core of the `djmongoauth`. It represents a authenticable entity. The primary attributes of a default user instance are:

- `username`
- `email`
- `password`
- `email_verified`
- `email_verified_at`

### Register a new user
```
def register(request):
    req_body = json.loads(request.body.decode("UTF-8"))
    user = User()
    user.username = req_body["username"]
    user.email = req_body["email"]
    user.password = req_body["password"]
    try:
        user.register()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return HttpResponse(status=201)
```
- `request.method` must be `POST`
- Body of `request` must have these attributes and they must be well-formed: `username`, `email`, `password`. Password can be cleartext (`djmongoauth` takes care of hashing / decryption)

### Log in 
```
def login(request):
    try:
        req_body = json.loads(request.body.decode("UTF-8"))
        x_auth_token = User.login(req_body["username"], req_body["password"])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"token": x_auth_token})
```
- `request.method` must be `POST`
- Body of `request` must have these attributes: `username` and `password`
- `login()` call returns a `x_auth_token`. This token should be returned to your site's frontend and serve as a basic auth token in the `HTTP_AUTHORIZATION` header for all subsequent requests till the token expires

### Log out 
```
def logout(request):
    try:
        User.logout(request)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return HttpResponse(status=204)
```
- `request` must have its `HTTP_AUTHORIATION` header set to the `x_auth_token` returned from `login` call

### Email verification 
```
# handler for verifying email address
def verify_email(request):
    if request.method == "POST":
        return _send_verify_email(request)
    elif request.method == "PUT":
        return _handle_email_verification(request)
    else:
        return HttpResponse(status=405)

def _send_verify_email(request):
    try:
        User.send_email(request, type=EmailTypes.VERIFY)
        return HttpResponse(status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def _handle_email_verification(request):
    try:
        User.handle_email_request(request, EmailTypes.VERIFY)
        return HttpResponse(status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

A verification email will be sent to the user's registered email address. Following is a sample verification email:

```
Hello test_user:

Please use the following link to verify your email address on test.com

https://test.com/verify?a=wMw_qmXu8fZOlcHP1Xpku4e8nuo8rCQim0AHzp5Taqtk0CWq2sThbEMu5kVCcy5leVYDpHKfY6-fMc_4HZBbQg

This link will expire on 2021-09-12 02:04:21 UTC

Thank you for using test.com!
```

- `request` must have its `HTTP_AUTHORIATION` header set to the `x_auth_token` returned from `login` call
- To send a verification email, `POST` this endpoint; to handle a email verification request, `PUT` this endpoint with parameter `a` set. Example: `PUT https://api.test.com/verify?a=wMw_qmXu8fZOlcHP1Xpku4e8nuo8rCQim0AHzp5Taqtk0CWq2sThbEMu5kVCcy5leVYDpHKfY6-fMc_4HZBbQg`
- If using a hosted email domain service (example: GSuite), please ensure that options such as *less secure apps* are enabled (Gmail)

### Password reset
```
def reset_password(request):
    if request.method == "POST":
        return _send_recovery_email(request)
    elif request.method == "PUT":
        return _handle_password_recovery(request)
    else:
        return HttpResponse(status=405)

def _send_recovery_email(request):
    try:
        User.send_email(request, type=EmailTypes.RESET)
        return HttpResponse(status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def _handle_password_recovery(request):
    try:
        User.handle_email_request(request, EmailTypes.RESET)
        return HttpResponse(status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

A password reset email will be sent to the user's registered email address. Following is a sample password reset email:

```
Hello test_user,

A request has been received to change the password for your account on test.com

Please follow this link to reset your password: https://test.com/reset?a=XfNKZT-OXXvvto3fDAyo5l46Ssmx1wQkXzlYGxQKyhFq3FTNve4vrvNYu8b8ha2erghRWtWfwFT5TT7O9xgM6Q

This link will expire on 2021-09-12 02:34:45 UTC

If you did not initiate this request, please ignore this email.
```

- To send a password reset email, `POST` this endpoint; to handle a password reset request, `PUT` this endpoint with parameter a set. Example: `PUT https://api.test.com/reset?a=wMw_qmXu8fZOlcHP1Xpku4e8nuo8rCQim0AHzp5Taqtk0CWq2sThbEMu5kVCcy5leVYDpHKfY6-fMc_4HZBbQg`
- When `PUT`ting this endpoint, body of `request` must have these attributes: `new_password`. `new_password` can be cleartext (`djmongoauth` takes care of hashing / decryption)

## Decorator
`@authenticated`

Use this decorator on request handlers, etc. to ensure a user is already logged in

```
from djmongoauth.decorators.authenticated import authenticated

@authenticated
def my_other_view_handler(request):
    pass 
```
If a user is not properly authenticated (e.g. not logged in / login session has expired), a `DjMongoAuthError` will be raised












