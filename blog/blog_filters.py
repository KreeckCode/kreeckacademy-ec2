from django import template

register = template.Library()

@register.filter
def split_content(value, word_count):
    words = value.split()
    if len(words) > word_count:
        return ' '.join(words[:word_count]), ' '.join(words[word_count:])
    return value, ''
