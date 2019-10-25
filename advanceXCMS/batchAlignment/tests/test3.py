

class Test(object):
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3
        return

    def __repr__(self):
        return (3*'%s,'% ( self.x, self.y, self.z))

t = Test()

x = [t.x,t.y,t.z]
print t
print x
print
t.x = 100
print t
print x

