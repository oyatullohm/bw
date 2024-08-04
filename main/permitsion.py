from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
from django.shortcuts import render , redirect 

def is_token_valid(token):
    if not token:
        return False
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        print("Token muddati o'tgan")
        return False
    except jwt.InvalidTokenError:
        print("Noto'g'ri token")
        return False

    
def get_token_from_request(request):
    auth_header = request.headers.get('Authorization', None)
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

