# A brief demonstration of classes
class RoundThing(object):
#>This initializes the object when it is created.
    def __init__(self, size):
        self.is_round = True
        self.size = size

    #> The parameter self must be explicitly specified when defining a method.
    def roll(self):
        #> Methods have access to the instance variables of their class
        #> without needing the parameters explicitly passed.
        print 'this is a %s ball rolling...' % self.size

#> This is a subclass of RoundThing.
class Ball(RoundThing):
    def __init__(self, material, *args):
        self.material = material
        #> This calls the superclass's __init__ method,
        #> this must be done explicitly in Python.
        super(Ball, self).__init__(*args)

    #> Subclasses can add functionality to methods of their base classes.
    def roll(self):
        print 'rolling like a ball made of %s' % self.material
        super(Ball, self).roll()

    #> Subclasses can also define new methods.
    def bounce(self):
        print 'boing...'

#> This says that the variable circle is an object of class RoundThing.
circle = RoundThing('big')
racket_ball = Ball('rubber', 'small')

#> The interpreter takes care of passing the self parameter to an object's methods.
circle.roll()

racket_ball.roll()
racket_ball.bounce()

#> It is possible to view the internals of a class with this function.
dir(circle)

#> Subclasses are still considered to be instances of their superclass.
print isinstance(racket_ball, RoundThing)

#> The converse is not true.
print isinstance(circle, Ball)
