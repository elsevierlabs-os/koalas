from pandas.api.extensions import register_series_accessor

def register_script_for_single_value(function):
    def wrapped_script(self, *args, **kwargs):
        return self.parent.apply(lambda x: function(x, *args, **kwargs))
    name = function.__name__
    setattr(_ScriptAccessor, name, wrapped_script)
    return function

def register_script_for_series(function):
    def wrapped_script(self, *args, **kwargs):
        return function(self.parent, *args, **kwargs)
    name = function.__name__
    setattr(_ScriptAccessor, name, wrapped_script)
    return function

@register_series_accessor('script')
class _ScriptAccessor:

    def __init__(self, parent):
        self.parent = parent
