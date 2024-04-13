from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def date_format(value, format_string='%Y-%m-%d'):
    return value.strftime(format_string)

def jinja2_environment(**options):
    env = Environment(**options)
    env.filters['date'] = date_format
    env.globals.update({
        'static': static,
        'url_for': reverse,
    })
    return env
