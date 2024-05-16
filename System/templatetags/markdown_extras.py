import markdown2
from django import template

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return markdown2.markdown(text)