import pandas as pd
import html


def format_col(x):
    return '<' + x + '>' if x.startswith('http') else x

def format_obj_col(x):
    return '<' + x + '>' if x.startswith('http') else '"' + x + '"@en'

def make_triples(sub, pre, obj, filename):
    sub = sub if type(sub) is str else sub.apply(format_col)
    pre = pre if type(pre) is str else pre.apply(format_col)
    obj = obj if type(obj) is str else obj.apply(html.unescape).apply(format_obj_col)
    triples = pd.DataFrame({'s': sub, 'p': pre, 'o': obj})
    turtle = '\n'.join(triples.s + ' ' + triples.p + ' ' + triples.o +' .')
    with open(filename, mode='w', encoding='utf-8') as f:
        f.write(turtle)
