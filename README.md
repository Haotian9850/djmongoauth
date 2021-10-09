# Using djmongouser

## What is it?
`djmongouser` provides out-of-the-box support for basic authentication and some additional operations including user registration, login, logout, email verification, password reset and recovery for backends built with the Django web framework and MongoDB.

`djmongouser` is based on `djongo`, a MongoDB ORM for Django.

## Use cases
### User object
User object is the core of the `djmongouser`. It represents a authenticable entity. The primary attributes of a default user instance are:

- `username`
- `email`
- `password`
- `email_verified`
- `email_verified_at`

### Register a new user
```
from djmongouser.utils import register
from djmongouser.DjMongoUserError import DjMongoUserError

def my_view_handler(request):
    try:
        register(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
    ...
```
- `request.method` must be `POST`
- Body of `request` must have these attributes and they must be well-formed: `username`, `email`, `password`. Password can be cleartext (`djmongouser` takes care of hashing / decrypting)

### Log in 
```
from djmongouser.utils import register
from djmongouser.DjMongoUserError import DjMongoUserError

def my_view_handler(request):
    x_auth_token = None 
    try:
        x_auth_token = login(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
    assert x_auth_token
```
- `request.method` must be `POST`
- Body of `request` must have these attributes: `username` and `password`
- `login()` call returns a `x_auth_token`. This token should be returned to your site's frontend and serve as a basic auth token in the `HTTP_AUTHORIZATION` header for all subsequent requests till the token expires [TODO: add customizable exp time for auth token]

### Log out 
```
from djmongouser.utils import logout
from djmongouser.DjMongoUserError import DjMongoUserError

def my_view_handler(request):
    try:
        logout(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
```
- `request` must have its `HTTP_AUTHORIATION` header set to the `x_auth_token` returned from `login` call

### Email verification 
```
from djmongouser.utils import send_verification_email, handle_email_verificiation_request
from djmongouser.DjMongoUserError import DjMongoUserError

# handler for verifying email address
def my_view_handler_1(request):
    try:
        send_verificaiton_email(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.

# handle email verification request
def my_view_handler_2(request):
    try:
        handle_email_verification_request(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
```
- `request` must have its `HTTP_AUTHORIATION` header set to the `x_auth_token` returned from `login` call
- If using a hosted email domain service (example: GSuite), please ensure that options such as *less secure apps* are enabled (Gmail)

### Password reset
```
from djmongouser.utils import send_password_reset_email, handle_password_reset_request
from djmongouser.DjMongoUserError import DjMongoUserError

# handler for resetting password
def my_view_handler_1(request):
    try:
        send_password_reset_email(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.

# handle password reset request
def my_view_handler_2(request):
    try:
        handle_password_reset_request(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
```
- Body of `request` for `my_view_handler_1` must have these attributes: `username`

### Password recovery
```
from djmongouser.utils import send_password_recovery_email, handle_password_recovery_request
from djmongouser.DjMongoUserError import DjMongoUserError

# handler for password recovery
def my_view_handler_1(request):
    try:
        send_password_recovery_email(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.

# handle password recovery request
def my_view_handler_2(request):
    try:
        handle_password_recovery_request(request)
    except DjMongoUserError as e:
        # your business logic to handle errors, etc.
```
- Body of `request` for `my_view_handler_1` must have these attributes: `username`








