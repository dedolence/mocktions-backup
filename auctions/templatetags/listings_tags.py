from django import template
from django.template.base import Template

register = template.Library()

@register.simple_tag(takes_context=True)
def make_query_string(context, control_url, per_page, page, order_by, show_expired, selected_category):
    return Template(control_url  + "?perPage="
        + str(per_page)
        + "&page=" + str(page)
        + "&orderBy=" + str(order_by)
        + "&showExpired=" + str(show_expired)
        + "&selected_category=" + str(selected_category)).render(context)