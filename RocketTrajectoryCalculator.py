##
#   RocketTrajectoryCalculator.py
#
#   Created by Brian Schrader on 4/25/14.
#
#
##

import Point
import ThrustProfile
import Rocket
import math


class Solver:
    """ Solves for the trajectory.
    Make sure to set:
    - air pressure (psi)
    - air volume (m^3)
    - water volume (m^3)
    - structural mass (lb)
    - payload mass (lb)
    - frontal area (ft^2)"""
    # Private Variables
    __psi_100 = 689475.729
    __ft_2 = 0.092903
    __lb_kg = 0.453592
    # Default Values
    airPressure = 25 * __psi_100  # Pa
    airVolume = .0015  # m^3
    waterVolume = .0005  # m^3
    structuralMass = 5 * __lb_kg  # kg
    payloadMass = 1 * __lb_kg  # kg
    frontalArea = .25 * __ft_2  # m^2
    tankThickness = 00.1  # m
    tankRadius = 0.1  # m
    d_noz = 0.01  # m
    rocket = Rocket.Rocket()

    # Class Methods
    @staticmethod
    def importDragData():
        """ Returns a list of drag tuples from the given drag csv. """
        drag = []
        dragfile = open("drag.csv", "r")
        dragstr = dragfile.read()
        for line in dragstr.splitlines():
            point = line.split(',')[0], line.split(',')[1], line.split(',')[2]
            drag.append(point)
        return drag

    @staticmethod
    def writeOut(data):
        """ Writes the given list of points to a file named 'out.csv'. """
        _file = open("_out.csv", "w")
        _file.write("Time (s),X (m),Y (m),Velocity (m/s),Acceleration (g),Mass (kg),Thrust (N),Drag (custom),Comment\n")
        _file.write(
            str(data[-1].time) + "," + str(data[-1].x) + "," + str(data[-1].y) + ",," + str(
                data[-1].acceleration / 9.81) + "," + str(data[-1].mass) + ",,,Max Height\n-,-,-,-,-\n")
        for point in data:
            _file.write(
                str(point.time) + "," + str(point.x) + "," + str(point.y) + "," + str(point.velocity) + "," + str(
                    point.acceleration / 9.81) + "," + str(point.mass) + "," + str(point.thrust) + "," + str(
                    point.drag) + "," + point.comment + "\n")
        _file.close()

    # Instance Methods
    def __init__(self):
        pass

    def calculate(self):
        """ Main """
        self.rocket = Rocket.Rocket()
        self.rocket.drag = self.importDragData()
        thrustProfile = ThrustProfile.ThrustProfile()
        self.rocket.flightStats = thrustProfile.getThrustProfile(self.airPressure, self.airVolume, self.waterVolume,
                                                                 self.d_noz)
        # Set values.
        self.rocket.payloadMass = self.payloadMass
        self.rocket.structuralMass = self.structuralMass
        self.rocket.frontalArea = self.frontalArea
        self.rocket.tankRadius = self.tankRadius
        self.rocket.tankThickness = self.tankThickness
        # Start Calculations
        self.rocket.calcLength()
        self.getStresses()
        self.rocket.launch()
        # Output
        points = self.rocket.getAllPoints()
        print "\nDry Mass: {0}(kg) or {1}(lb)".format(self.structuralMass + self.payloadMass, (self.structuralMass +
                                                                                               self.payloadMass) /
                                                                                               self.__lb_kg)
        print "\nApogee Height: {0}(m)".format(str(self.getMaxHeight()))
        print "\nTank Stats:\nVolume: {0}(L) Length: {1}(m) Area: {2}(m^2) Radius: {3}(cm)".format(
            str(self.rocket.volume * 1000),
            str(self.rocket.length),
            str(self.rocket.frontalArea),
            str(math.sqrt(
                self.rocket.frontalArea /
                3.14) * 100))
        print "Hoop Stress: {0}(MPa) Longitudinal Stress: {1}(MPa)".format(str(self.rocket.hoopStressCurrent / 1000000),
                                                                           str(self.rocket.longStressCurrent / 1000000))
        self.writeOut(points)

    def getMaxHeight(self):
        points = self.rocket.getAllPoints()
        if len(points) > 0:
            maxPoint = points[-1]
            return maxPoint.y

    def getStresses(self):
        """ Calculates the stresses and forces on the rocket body. Accounts for both internal pressure loads and
        external drag forces. """
        # self.flightStats: {Time, Thrust, MassFlow, Current Mass, Current Air Volume, Current Water Volume, Total
                            # Air Volume, Total Water Volume, Current Air Mass, Current Water Mass}
        # Get the current tank status.
        self.rocket.hoopStressCurrent = self.airPressure * self.tankRadius / self.tankThickness
        self.rocket.longStressCurrent = self.airPressure * self.tankRadius / (2 * self.tankThickness)
        return 0