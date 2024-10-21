from core.easy_router.route import Route

from .api import send_otp, verify_otp

routes = [Route("/send/", send_otp), Route("/verify/", verify_otp)]
