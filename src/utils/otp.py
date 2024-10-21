import hashlib

from pyotp import totp

from core.settings import settings

from .email import EmailUtil


class OTPUtils:
    def __init__(self, phone_no=None, email=None, key="", subject=""):
        self.phone_no = phone_no
        self.email = email
        self.key = key
        self.subject = subject

    def get_user_info(self):
        if self.phone_no:
            return self.phone_no
        elif self.email:
            return self.email

    def totp(self):
        return totp.TOTP(
            settings.OTP_SECRET,
            digest=hashlib.sha256,
            name=self.key + self.get_user_info(),
            interval=settings.OTP_SECRET,
        )

    def create(self):
        """
        Create OTP and send SMS to user
        :return: otp
        """
        t_otp = self.totp()
        otp = t_otp.now()
        data = {"otp": otp, "purpose": "registration"}
        if self.subject:
            data["subject"] = self.subject
        data["title"] = self.subject
        EmailUtil(
            to_emails=[self.email],
            subject=self.subject,
            html_template="messages/email/otp.html",
            template_data=data,
        ).send()
        return otp

    def verify(self, otp):
        """
        Verify otp
        :return: if otp is valid or not
        """
        if settings.OTP_DEBUG:
            return self.totp().verify(otp) or otp == settings.TESTING_OTP
        return self.totp().verify(otp)
