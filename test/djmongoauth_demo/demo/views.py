from django.http import HttpResponse, JsonResponse
import json 
from django.views.decorators.csrf import csrf_exempt
from djmongoauth.models import User
from djmongoauth.common.EmailTypes import EmailTypes
from djmongoauth.decorators.authenticated import authenticated

@csrf_exempt
def register(request):
    if request.method != "POST":
        return HttpResponse(status=405)    # incorrect request method
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

@csrf_exempt
def login(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        req_body = json.loads(request.body.decode("UTF-8"))
        x_auth_token = User.login(req_body["username"], req_body["password"])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"token": x_auth_token})

@csrf_exempt
@authenticated
def logout(request):
    try:
        User.logout(request)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return HttpResponse(status=204)

@csrf_exempt
@authenticated
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
    

@csrf_exempt
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


