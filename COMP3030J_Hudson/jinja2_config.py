from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'STATIC_URL': static,
        'url':reverse,
    })
    return env