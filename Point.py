
class Point:
    """ Model for a point. """
    time = 0.0
    acceleration = 0.0
    velocity = 0.0
    x = 0.0
    y = 0.0
    drag = 0.0
    thrust = 0.0
    mach = 0.0
    mass = 0.0
    comment = ""

    def __init__(self, _x, _y, _time, _velocity, _acceleration, _comment):
        self.time = _time
        self.x = _x
        self.y = _y
        self.velocity = _velocity
        self.acceleration = _acceleration
        self.comment = _comment

