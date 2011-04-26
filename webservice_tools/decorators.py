from functools import wraps
from webservice_tools.response_util import ResponseObject
from django.http import QueryDict
import urlparse
import time

def login_required(fn):
    fn.authentication_required = True
    @wraps(fn)
    def inner(*args, **kwargs):
        
        response = ResponseObject()
        try:
            request = [a for a in args if hasattr(a, 'user')][0]
        except IndexError:
            return response.send(errors="Login required method called without request object", status=500)
        if request.user.is_authenticated():
            return fn(*args, **kwargs)
        
        return response.send(errors='401 -- Unauthorized', status=401)
    
    return inner

def data_delete(fn):
    """
    Allows you to supply data for delete, provides a request.DELETE dict for use in the view
    """
    @wraps(fn)
    def inner(*args, **kwargs):
        
        response = ResponseObject()
        try:
            request = [a for a in args if hasattr(a, 'user')][0]
        except IndexError:
            return response.send(errors="Login required method called without request object", status=500)
        
        
        if request.raw_post_data and request.method == 'DELETE':
            request.DELETE = QueryDict(request.raw_post_data)
            t_args = [a for a in args]
            t_args[t_args.index(request)] = request
        return fn(*t_args, **kwargs)
    return inner




def retry(tries=5, exceptions=None, delay=0.3, exception_raise=None):
    """
    Decorator for retrying a function if exception occurs
        
    tries -- num tries 
    exceptions -- exceptions to catch
    delay -- wait between retries
    taken from https://gist.github.com/728327
    """
    exceptions_ = exceptions or (Exception,)
    def _retry(fn):
        @wraps(fn)
        def __retry(*args, **kwargs):
            for _ in xrange(tries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions_, e:
                    time.sleep(delay)
            #if no success after tries raise last exception
            if exception_raise:
                raise exception_raise
            else:
                raise
        return __retry
    return _retry


import hotshot
import os
import time


PROFILE_LOG_BASE = "/tmp"


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer



def make_b(fn):
    def inner(*args, **kwargs):
        b  = [i for i in args if i==1][0]
        temp_args = [a for a in args]
        temp_args[temp_args.index(b)] = 2
        return fn(*temp_args, **kwargs)
    return inner


def foo(fn):
    def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner

def bar(fn):
    def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner

