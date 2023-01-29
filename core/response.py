from django.http.response import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import resolve_url


class ExpAndHttpResponseRedirect( HttpResponseRedirect ):
    allowed_schemes = ['http', 'https', 'exp']


class ExpAndHttpResponsePermanentRedirect( HttpResponsePermanentRedirect ):
    allowed_schemes = ['http', 'https', 'exp']


def redirect(to, *args, permanent=False, **kwargs):
    """
    Return an HttpResponseRedirect to the appropriate URL for the arguments
    passed.

    The arguments could be:

        * A model: the model's `get_absolute_url()` function will be called.

        * A view name, possibly with arguments: `urls.reverse()` will be used
          to reverse-resolve the name.

        * A URL, which will be used as-is for the redirect location.

    Issues a temporary redirect by default; pass permanent=True to issue a
    permanent redirect.
    """
    redirect_class = ExpAndHttpResponsePermanentRedirect if permanent else ExpAndHttpResponseRedirect
    return redirect_class( resolve_url( to, *args, **kwargs ) )
