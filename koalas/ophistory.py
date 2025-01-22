
def _WordList(*args, **kwargs):
    from .wordlist import WordList
    return WordList(*args, **kwargs)

class OpHistory:

    def __add__(self, other):
        result = super().__add__(other)
        return result.__finalize__(self, context=('plus', other))

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        return result.__finalize__(self, context=('multiplied with', other))

    def __sub__(self, other):
        result = super().__sub__(other)
        return result.__finalize__(self, context=('minus', other))

    def __truediv__(self, other):
        result = super().__truediv__(other)
        return result.__finalize__(self, context=('divided by', other))

    def __eq__(self, other):
        result = _WordList(super().__eq__(other))
        return result.__finalize__(self, context=('equals', other))
