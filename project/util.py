# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME


#--------------------------------------------------------------------------------------------------


def str_to_int(s, default=0):
    try:
        return int(s)
    except:
        return default


#--------------------------------------------------------------------------------------------------


def str_to_float(s, default=0.0):
    try:
        return float(s.replace(",", "."))
    except:
        return default


#--------------------------------------------------------------------------------------------------


def str_to_date(s, default=None):
    import datetime
    res = default
    try:
        date = s.strip().split(".")
        if len(date) >= 3:
            res = datetime.date(int(date[2]), int(date[1]), int(date[0]))
    except:
        pass

    return res


#--------------------------------------------------------------------------------------------------


def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):

    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


#--------------------------------------------------------------------------------------------------


def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and (u.is_superuser or u.is_staff),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


#--------------------------------------------------------------------------------------------------


def decode_cookie_value(s):
    # cookie value is urlencoded, decode hr chars
    from urllib import unquote_plus
    return unicode(unquote_plus(str(s)), 'utf-8')


#--------------------------------------------------------------------------------------------------


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    from functools import update_wrapper, wraps
    from django.utils.decorators import available_attrs
    from django.utils.http import urlquote
    from django.http import HttpResponseRedirect

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            return HttpResponseRedirect('/accounts/login/?next=%s' % (path))
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


#--------------------------------------------------------------------------------------------------


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


#--------------------------------------------------------------------------------------------------
