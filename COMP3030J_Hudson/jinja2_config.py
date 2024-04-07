from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment



def jinja2_environment(**options):
    env = Environment(**options)
    env.globals.update({
        'STATIC_URL': static,
        'url_for': reverse,
    })
    return env
