from django.utils import timezone
from django.shortcuts import redirect
from datetime import timedelta

class SessionExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'user' in request.session:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity > timedelta(hours=1):
                    request.session.flush()
                    return redirect('admin_login')
            
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response
