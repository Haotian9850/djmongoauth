import functools
from ..models import Session, User
from ..DjMongoAuthError import DjMongoAuthError
from bson.objectid import ObjectId

def authenticated():
    def decorator(func):
        @functools.wraps(func)
        def wrapper_authenticated(*args, **kwargs):
            # args[0] is django request
            request = args[0]
            assert request
            try:
                exp, user_id, username, session_key = Session.parse_x_auth_token(request.META["HTTP_AUTHORIZATION"])
                user = User.objects.get(_id=ObjectId(user_id))
                valid_session = False
                # check session
                all_sessions = Session.objects.filter(session_key=session_key)
                for session in all_sessions:
                    if not session.has_expired():
                        valid_session = True
                        break 
                if not valid_session:
                    raise DjMongoAuthError("No active session found for user {}".format(username))
            except Exception as e:
                raise DjMongoAuthError("User is not authenticated: {}".format(str(e)))
            return func(*args, **kwargs) 
        return wrapper_authenticated
    return decorator