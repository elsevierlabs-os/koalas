import time
import getpass


class History(list):
    '''This class is a list of events. It can print a pretty output.
    '''

    def __init__(self, data=None):
        if data is not None:
            history = [Event(**event) for event in data]
        else:
            history = [Event()]
        super().__init__(history)

    def __str__(self):
        return '\n' + '\n'.join(['  %s'%event for event in self]) + '\n'

    def __repr__(self):
        return self.__str__()


class Event(dict):
    '''This dictionary holds information about one edit event.
    '''

    def __init__(self, argument='', **kwargs):
        creator = kwargs.get('creator', None) or getpass.getuser()
        date = kwargs.get('date', None) or time.time()
        operation = kwargs.get('operation', None) or 'created'
        argname = getattr(argument, 'name', None)
        argument = argname if argname is not None else str(argument)
        super().__init__(creator=creator, date=date, operation=operation, argument=argument)

    def __str__(self):
        argument = '"%s"'%self['argument'] if self['argument'] else ''
        timefmt = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(self['date']))
        stamp = '(%s on %s)' % (self['creator'], timefmt)
        string = '- %s %s %s' % (self['operation'], argument, stamp)
        return _break_into_lines(string, 77)

    def __repr__(self):
        return self.__str__()


def _break_into_lines(string, linelength, adjlength=0):
    adjlength = adjlength or linelength
    if len(string) <= linelength:
        return string
    elif not string[adjlength] in [' ', ',', '.']:
        return _break_into_lines(string[:], linelength, adjlength-1)
    else:
        return string[:adjlength + 1] + '\n    '\
         + _break_into_lines(string[adjlength + 1:], linelength)
