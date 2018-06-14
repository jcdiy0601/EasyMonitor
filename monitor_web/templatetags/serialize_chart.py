#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def display_chart_type(chart_obj, chart_type):
    """
    显示图表类型
    :param chart_obj:
    :param chart_type:
    :return:
    """
    chart_type_choices_list = chart_obj.chart_type_choices
    for chart_type_choices in chart_type_choices_list:
        if chart_type == chart_type_choices[0]:
            return mark_safe(chart_type_choices[1])
