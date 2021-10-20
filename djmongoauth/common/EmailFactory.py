from django.conf import settings
from .EmailTypes import EmailTypes

from .Email import Email

class EmailFactory():
    SITE_URL = settings.SITE_URL
    IS_HTTPS = settings.IS_HTTPS
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    PASSWORD_RESET_EMAIL_SUBJECT = "Reset your password on {}".format(SITE_URL)
    VERIFY_EMAIL_SUBJECT = "Verify your e-mail to finish signing up for {}".format(SITE_URL)

    def __init__(self, **kwargs):
        pass 

    @staticmethod
    def generate_email(type:str, **kwargs):
        if type == EmailTypes.RESET:
            return EmailFactory._generate_password_reset_email(**kwargs)
        elif type == EmailTypes.VERIFY:
            return EmailFactory._generate_verify_email(**kwargs)
        return None

    @staticmethod
    def _generate_verify_email(**kwargs):
        assert kwargs.get("temp_auth")
        assert kwargs.get("user")
        temp_auth = kwargs["temp_auth"]
        user = kwargs["user"]
        verify_link = "{}/verify?a={}".format(
            "{}://{}".format(
                "https" if EmailFactory.IS_HTTPS else "http",
                EmailFactory.SITE_URL
            ),
            temp_auth.authenticator
        )
        expires_at = temp_auth.expires_at.strftime("%Y-%m-%d %H:%M:%S")
        html_message = """
        <p>Hello {username}:</p><p><br></p><p>Please use the following link to verify your email address on {site_url}</p><p>{verify_link}</p><p>This link will expire on {expires_at} UTC</p><p>Thank you for using {site_url}!</p>
        """.format(
            username=user.username,
            site_url=EmailFactory.SITE_URL,
            verify_link=verify_link,
            expires_at=expires_at
        )
        text_message = """
        Hello {username}, please use this link to verify your email address on {site_url}: {verify_link} This link will expire on {expires_at} UTC. Thank you for using {site_url}!
        """.format(
            username=user.username,
            site_url=EmailFactory.SITE_URL,
            verify_link=verify_link,
            expires_at=expires_at
        )
        return Email(
            subject=EmailFactory.VERIFY_EMAIL_SUBJECT,
            text_message=text_message,
            html_message=html_message,
            from_email=EmailFactory.EMAIL_HOST_USER,
            to_email=user.email
        )

    @staticmethod
    def _generate_password_reset_email(**kwargs):
        assert kwargs.get("user", None)
        assert kwargs.get("temp_auth", None)
        user = kwargs["user"]
        temp_auth = kwargs["temp_auth"]
        reset_link = "{}/reset?a={}".format(
            "{}://{}".format(
                "https" if EmailFactory.IS_HTTPS else "http",
                EmailFactory.SITE_URL
            ),
            temp_auth.authenticator
        )
        expires_at = temp_auth.expires_at.strftime("%Y-%m-%d %H:%M:%S")
        html_message = """
        <p>Hello {username},</p><p><br></p><p>A request has been received to change the password for your account on {site_url}</p><p>Please follow this link to reset your password: {reset_link}</p><p>This link will expire on {expires_at} UTC</p><p>If you did not initiate this request, please ignore this email. </p>
        """.format(
            username=user.username,
            site_url=EmailFactory.SITE_URL,
            reset_link=reset_link,
            expires_at=expires_at
        )
        text_message = """
        Hello {username}, a request has been received to change the password for your account on UnreadLetters. Please follow this link to reset your password: {reset_link}. This link will expire on {expires_at} UTC. If you did not initiate this request, please ignore this email.
        """.format(
            username=user.username,
            reset_link=reset_link,
            expires_at=expires_at
        )
        return Email(
            subject=EmailFactory.PASSWORD_RESET_EMAIL_SUBJECT,
            text_message=text_message,
            html_message=html_message,
            from_email=EmailFactory.EMAIL_HOST_USER,
            to_email=user.email
        )


