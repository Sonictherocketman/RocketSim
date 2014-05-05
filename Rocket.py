##
#   RocketSolver.py
#
#   Created by Brian Schrader on 4/25/14.
#
#
##

import Point


class Rocket:
    """ Put comment here. """
    # Constants
    __speedOfSound = 340.29  # m/s @ sea level
    # Bookkeeping
    __points = []
    __previousPoint = Point.Point(0, 0, 0, 0, 0, "Launch Point")
    __apogeePoint = Point.Point(0, 0, 0, 0, 0, "")
    __burnoutPoint = Point.Point(0, 0, 0, 0, 0, "")
    __impactPoint = Point.Point(0, 0, 0, 0, 0, "")
    __flightTime = 0  # seconds
    __dt = 0.01  # seconds
    # Data
    drag = []
    thrust = []
    flightStats = []
    # Status
    hasReachedApogee = False
    hasLaunched = False
    isPowered = True
    isCruising = False
    # Structure and Configuration
    payloadMass = 0.0  # kg
    structuralMass = 0.0  # kg
    propellantMass = 0.0  # kg
    burnTime = 0.0  # s
    currentMass = 0.0  # kg
    frontalArea = 0.1  # m^2
    length = 0.0  # m
    # Tank Stats
    volume = 0.0  # m^3
    hoopStressCurrent = 0.0
    longStressCurrent = 0.0
    hoopStress = []
    longStress = []
    tankThickness = 0.0
    tankRadius = 0.0

    # Private Methods
    def __init__(self):
        """ Default Constructor """
        self.ready = True

    def __dragForMach(self, mach, powered):
        """ Determines the drag value for the given mach number. The mach number is accurate to 5%
        :param mach: float Mach Number
        :param powered: bool Whether or not the flight is powered.
        :rtype : float Drag Value
        """
        acceptableError = 0.05
        for drag in self.drag:
            try:
                machFromDrag = float(drag[0])
            except FloatingPointError:
                print "Value {0} could not be made into a number.".format(drag[0])
            percentError = abs(mach - machFromDrag) / (mach + machFromDrag)
            if percentError <= acceptableError:
                # Result found
                if powered:
                    return float(drag[2])
                if not powered:
                    return float(drag[1])
        return 0

    def __thrust(self, time):
        """ Returns the thrust value for the given time value. """
        for moment in self.flightStats:
            if time == moment[0]:  # Find the correct time in the list of thrust profile info.
                return int(moment[1])
        return 0

    def __massflow(self, time):
        """ Returns the mass flow value for the given time.
        :param time: int Burn time in seconds
        :rtype : int
        """
        for moment in self.flightStats:
            if time == moment[0]:  # Find the correct time in the list of mass flow profile info.
                return int(moment[2])

        return 0

    def __fuelMass(self, time):
        """ Returns the mass value for the given time.
        :param time: int Burn time in seconds
        :rtype : int
        """
        for moment in self.flightStats:
            if time == moment[0]:  # Find the correct time in the list of mass profile info.
                return int(moment[3])
        return 0

    def __burnTime(self):
        if self.burnTime == 0.0:
            moment = self.flightStats[-1]
            self.burnTime = moment[0]
            return int(moment[0])
        else:
            return self.burnTime

    # Public Methods
    def launch(self):
        """ Launches the rocket. Once this is finished the points are available for use. """
        self.hasLaunched = True
        self.__burnTime()
        while not self.hasReachedApogee:
            self.__flightTime += self.__dt
            self.__points.append(self.getNextPoint())

    def getAllPoints(self):
        return self.__points

    def getNextPoint(self):
        """ This method does the actual calculations for the rocket's location and trajectory.
        :rtype : Point
        :type self: Rocket
        :rtype Point: Point the next point in the trajectory.
        """
        point = Point.Point(0, 0, 0, 0, 0, "")
        if len(self.__points) > 0:
            prevPoint = self.__previousPoint = self.__points[-1]
        else:
            prevPoint = self.__previousPoint
        rho = 1.225 / (10 ** 4)  # kg/m^3
        mach = prevPoint.velocity / self.__speedOfSound

        self.currentMass = self.__fuelMass(self.__flightTime) + self.structuralMass + self.payloadMass
        dragCoeff = self.__dragForMach(mach, self.isPowered)
        aerodrag = dragCoeff * 0.5 * rho * self.frontalArea * (
            prevPoint.velocity ** 2)
        drag = aerodrag + 9.81
        if self.isPowered:
            # Powered Climb
            thrust = self.__thrust(self.__flightTime)
            acceleration = (thrust - drag) / self.currentMass
            vel = prevPoint.velocity + 0.5 * self.__dt * (acceleration + prevPoint.acceleration)
            y = vel * self.__dt + prevPoint.y
            x = 0  # The rocket is being launched at a 90 degree angle to the ground. Ignoring wind, there is no
            # horizontal travel.
        else:
            # Cruising Upward
            thrust = 0.0
            acceleration = (thrust - drag) / self.currentMass
            vel = prevPoint.velocity + 0.5 * self.__dt * (prevPoint.acceleration + acceleration)
            y = vel * self.__dt + prevPoint.y  # We can do this since there is no horizontal motion.
            x = 0

        point.x = x
        point.y = y
        point.velocity = vel
        point.acceleration = acceleration
        point.drag = aerodrag
        point.thrust = thrust
        point.time = self.__flightTime
        point.mass = self.currentMass

        # Update Mission Status
        if prevPoint.y > point.y:
            self.hasReachedApogee = True
            point.comment = "Apogee"
        if self.__flightTime > self.burnTime and not self.isCruising:
            self.isPowered = False
            self.isCruising = True
            point.comment = "Burnout Reached"

        return point

    def calcLength(self):
        """ Calculate the length of the rocket. """
        moment = self.flightStats[0]
        vol_total = moment[6] + moment[7]
        length = vol_total / self.frontalArea  # Assumes the same shape over the length of the rocket.
        self.length = length
        self.volume = vol_total
        return length