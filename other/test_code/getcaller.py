import sys, inspect

def get_calling_function():
    """finds the calling function in many decent cases."""
    fr = sys._getframe(1)   # inspect.stack()[1][0]
    co = fr.f_code
    for get in (
        lambda:fr.f_globals[co.co_name],
        lambda:getattr(fr.f_locals['self'], co.co_name),
        lambda:getattr(fr.f_locals['cls'], co.co_name),
        lambda:fr.f_back.f_locals[co.co_name], # nested
        lambda:fr.f_back.f_locals['func'],  # decorators
        lambda:fr.f_back.f_locals['meth'],
        lambda:fr.f_back.f_locals['f'],
        ):
        try:
            func = get()
        except (KeyError, AttributeError):
            pass
        else:
            if func.__code__ == co:
                return func
    raise AttributeError("func not found")




def target():

    print inspect.stack()[1][3]

    return

def caller():
    target()
    return

caller()
