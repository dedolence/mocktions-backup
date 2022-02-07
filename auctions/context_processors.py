from inspect import getmembers, isfunction
from django.urls import reverse
from auctions import ajax_controls
from auctions.ajax_controls import *


def filter_functions(func):
    if isfunction(func[1]) and func[0][:5] == 'ajax_':
        return True
    else:
        return False


def ajax(request):
    # Produce a list of tuples like (function_name, function_object)
    function_list = [func for func in getmembers(ajax_controls) if filter_functions(func)]
    dict = {'ajax': {}}
    for func in function_list:
        """ dict['ajax'][func[0]] = {
            'name': func[0],
            'url': reverse(func[0])
        } """
        dict['ajax'][func[0]] = { 'name': func[0], 'url': reverse(func[0])}
    return dict