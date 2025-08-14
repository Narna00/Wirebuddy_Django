class SeparateAdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Change the cookie name depending on the path
        if request.path.startswith("/admin"):
            request.session._session_key = None  # Force re-read with different cookie
            request.session_cookie_name = "admin_sessionid"
        else:
            request.session._session_key = None
            request.session_cookie_name = "frontend_sessionid"

        response = self.get_response(request)

        # Set the correct cookie name in the response
        if hasattr(request, "session"):
            response.set_cookie(
                request.session_cookie_name,
                request.session.session_key,
                max_age=None,
                httponly=True,
                secure=False,  # change to True if using HTTPS
                samesite="Lax"
            )

        return response
