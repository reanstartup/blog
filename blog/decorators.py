from functools import wraps
from django.shortcuts import redirect

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
