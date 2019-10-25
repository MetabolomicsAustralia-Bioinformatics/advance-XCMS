

class obj(object):
    def __init__(self):
        self.x = 4
        return

a = obj()

b = a
print b.x, a.x
b.y = 1
b.x = 3
print b.x, a.x
print b.y, a.y


