from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Оновлює окремі GET-параметри без втрати решти.
    Використання: {% url_replace page=2 %}
    Результат: ?subject=1&type=exam&page=2
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
