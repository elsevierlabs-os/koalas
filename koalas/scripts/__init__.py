'''
This module contains additional scripts that can be used on WordFrames. Scripts
can be accesed through the `script` accessor like this:
`terms.script.is_binomial_name(on='label')`. To avoid making dependencies of
these scripts obligatory to install, they have to be explicitly imported (e.g.
`import koalas.scripts.binomial_name`). New scripts can easily be added by
providing a function that takes a single value or an entire WordList as input.
Just add one of the decorators from the `register` module
(`register_script_for_single_value` or `register_script_for_series`) like this:
```
@register_script_for_single_value
def my_cool_function(value):
    do something with value
    return result
```
'''
try:
    from .register import _ScriptAccessor
except:
    print('Warning: install pandas > 0.23.0 to use extension scripts')
