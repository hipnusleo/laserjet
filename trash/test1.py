#!encoding:utf-8
class echo
    :
    def output(self)

:
print 'hello
world
'


def __enter__(self):
    print 'enter'
    return self  # 返回自身实例，当然也可以返回任何希望返回的东西


def __exit__(self,
             exception_type, exception_value, exception_traceback):
    # 若发生异常，会在这里捕捉到，可以进行异常处理
    print 'exit'
    # 如果改__exit__可以处理改异常则通过返回True告知该异常不必传播，否则返回False
    if exception_type

== ValueError
:
return True
else:
return False

with
    echo() as e:
    e.output()
    print 'do
something
inside
'
print '-----------'
with
    echo() as e:
    raise ValueError('value
    error
    ')
    print '-----------'
    with
    echo() as e:
        raise Exception('can
    not detect
    ')
