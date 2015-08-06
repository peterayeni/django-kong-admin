from __future__ import unicode_literals
from django.template import Library

register = Library()

@register.inclusion_tag('kong_admin/custom_admin_actions.html', takes_context=True)
def custom_admin_actions(context):
    """
    Track the number of times the action field has been rendered on the page,
    so we know which value to use.
    """
    context['action_index'] = context.get('action_index', -1) + 1
    return context
