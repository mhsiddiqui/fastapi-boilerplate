from core.easy_router.route import Route, include

routes = [
    Route(path="/api/auth/v1", endpoint=include("src.features.auth.routes"), tags=["Authentication"]),
    Route(path="/api/account/v1", endpoint=include("src.features.account.routes"), tags=["Account"]),
    Route(path="/api/otp/v1", endpoint=include("src.features.otp.routes"), tags=["OTP"]),
]
