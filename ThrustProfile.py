##
#   Thrust Profile.py
# 
#   Created by Brian Schrader on 4/24/14.
#
#   This script uses initial values to calculate a mass flow, and therefor a thrust profile.
##

import math


class ThrustProfile:
    ################
    # Default Values
    ################
    p_air_total = 31026407.8  # Pa ~4500PSI
    vol_water_total = .005  # m^3 ~1Gal
    vol_air_total = .0075  # m^3 ~1.5Gal
    dt = 0.01
    # Constants
    p_atmosphere = 101.01  # Pa
    rho_water = 1000.0  # kg/m^3
    d_noz = 0.01  # m
    m_water_total = 0  # kg
    m_air_total = 0  # kg
    # Current Values
    p_air_current = 0
    vol_air_current = 0
    vol_water_current = 0
    m_water_current = 0
    m_air_current = 0
    m_dot_water = 0
    m_dot_air = 0
    time = 0
    u_e = 0
    # Output Stuff
    thrust = []
    m_dot_list = []
    m_water_list = []
    time_list = []

    # Init starting values.
    def __init__(self):
        """ Default Constructor """

    def init(self):
        """ Custom Constructor """
        # m_air = V * (P/RT)
        self.m_water_total = self.rho_water * self.vol_water_total
        self.m_air_total = self.vol_air_total * (self.p_air_total / (287 * 293))
        self.m_air_current = self.m_air_total
        self.m_water_current = self.m_water_total
        self.vol_air_current = self.vol_air_total
        self.vol_water_current = self.vol_water_total
        self.p_air_current = self.p_air_total
        self.time = 0
        self.u_e = 0

    # Output to file and console.
    def output(self):
        of = open("_thrust_profile.csv", "w")
        count = len(self.thrust)
        # Add metadata to file.
        foo = "Burntime (s),{0}\nTotal Air Pressure (kPA),{1}\nTotal Air Mass (kg),{2}\nTotal Water Mass (kg),{3}\n" \
              "Total Tank Volume (m^3),{4}\nVolume Air/Water Ratio,{5},{6}\nMass Air/Water Percents,{7},{8}\n".format(
            str(self.time), str(
                self.p_air_total / 1000), str(self.m_air_total), str(
                self.m_water_total), str(
                self.vol_air_total + self.vol_water_total), str(
                abs(self.vol_air_total) / (self.vol_air_total + self.vol_water_total) * 100), str(
                abs(self.vol_air_total) / (self.vol_air_total + self.vol_water_total) * 100), str(
                abs(self.m_air_total) / (self.m_air_total + self.m_water_total) * 100), str(
                abs(self.m_water_total) / (self.m_air_total + self.m_water_total) * 100))
        of.write(foo)
        # Time
        of.write("Time (s),")
        for i in range(count):
            of.write(str(self.time_list[i]) + ",")
        of.write("\n")
        # Thrust Profile
        of.write("Thrust Profile (N),")
        for i in range(count):
            of.write(str(self.thrust[i]) + ",")
        of.write("\n")
        # M_dot
        of.write("Mass Flow (kg/s),")
        for i in range(count):
            of.write(str(self.m_dot_list[i]) + ",")
        of.write("\n")
        # M_water
        of.write("Fuel Mass (kg),")
        for i in range(count):
            of.write(str(self.m_water_list[i]) + ",")
        of.close()

        # Print to the console.
        print "\nBurn time: " + str(self.time) + " s"
        print "Starting Water Mass: " + str(self.m_water_total) + " kg"
        print "Starting Air Mass: " + str(self.m_air_total) + " kg"
        print "Starting Tank Pressure: %.02d kPa" % (self.p_air_total / 1000)
        print "Ending mass flow rate: " + str(self.m_dot_water) + " kg/s"
        print "Volume Air/Water Ratio: " + str(
            abs(self.vol_air_total) / (self.vol_air_total + self.vol_water_total) * 100) + " " + str(
            abs(self.vol_water_total) / (self.vol_air_total + self.vol_water_total) * 100)
        print "Mass Air/Water Percents: " + str(abs(
            self.m_air_total) / (self.m_air_total + self.m_water_total) * 100) + " " + str(
            abs(self.m_water_total) / (self.m_air_total + self.m_water_total) * 100)

    # Calculate a mass flow.
    def massflow(self):
        """ m_dot = rho * u_e * A """
        # Via Bernoulli's
        # Assuming no loss of water inside the tank.

        self.u_e = math.sqrt(2 * abs(self.p_air_current - self.p_atmosphere) / self.rho_water)
        area = 3.14 * pow((self.d_noz / 2), 2)  # Get Nozzle area
        self.m_dot_water = self.rho_water * self.u_e * area * 0.98  # Get new mass flow. The .98 is the C_d for orifice.
        self.m_dot_list.append(self.m_dot_water)
        self.m_water_current -= self.m_dot_water * self.dt  # update water mass.
        self.m_water_list.append(self.m_water_current)
        oldVolumeAir = self.vol_air_current
        dv = self.m_dot_water * self.dt / self.rho_water  # Get the change in volume
        self.vol_water_current -= dv  # Decrement the water volume.
        self.vol_air_current += dv  # Increment the air volume.
        self.p_air_current *= (oldVolumeAir / self.vol_air_current) ** 1.4  # Get the new air pressure

    # Calculate thrust profile.
    def calcThrust(self):
        """ thrust = m_dot * u_e + A * (p_a - p_e) """
        self.thrust.append(self.m_dot_water * self.u_e)

    def calcBlowdownThrust(self):
        # Blowdown Calcs
        global m_dot_air
        area = 3.14 * (self.d_noz / 2) ** 2
        self.thrust.append((self.m_dot_air * self.u_e) + area * (self.p_air_current - self.p_atmosphere))

    def massFlowBlowdown(self):
        """ m_dot = rho * u_e * A """
        # Via Bernoulli's
        # Assuming no loss of water inside the tank.
        rho_air = self.p_air_current / (287 * 293)
        self.u_e = math.sqrt(2 * abs(self.p_air_current - self.p_atmosphere) / rho_air) * 0.98
        area = 3.14 * pow((self.d_noz / 2), 2)  # Get Nozzle area
        self.m_dot_air = rho_air * self.u_e * area  # Get new mass flow.
        self.m_dot_list.append(self.m_dot_air)
        self.m_air_current -= self.m_dot_air * self.dt  # update air mass.
        self.m_water_list.append(self.m_air_current)
        self.p_air_current = self.m_air_current / (self.vol_air_total + self.vol_water_total) * (293 * 287)


    def main(self):
        print "\nStarting..."
        self.init()
        while self.m_water_current > 0:
            self.time += self.dt
            # Do Mass Flow/Thrust Analysis
            self.massflow()
            self.calcThrust()
            if self.p_air_current < self.p_atmosphere:
                break
        self.output()
        print "Ending...\n"

    # Public method.
    def getThrustProfile(self, p_air, vol_air, vol_water, noz):
        """ Returns a list of tuples {Time, Thrust, MassFlow, Current Mass, Current Air Volume, Current Water Volume,
        Total Air Volume, Total Water Volume, Current Air Mass, Current Water Mass} for the entire burn. WARNING: Does
        not include blow-down. """
        self.d_noz = noz
        self.p_air_total = p_air  # Pa
        self.vol_water_total = vol_air  # m^3
        self.vol_air_total = vol_water  # m^3
        self.init()
        stuff = []
        self.init()
        # Burn
        while self.m_water_current > 0:
            self.time += self.dt
            self.time_list.append(self.time)
            # Do Mass Flow/Thrust Analysis
            self.massflow()
            self.calcThrust()
            item = self.time, self.thrust[-1], self.m_dot_list[-1], (
                self.m_water_current + self.m_air_current), self.vol_air_current, self.vol_water_current, \
                   self.vol_air_total, self.vol_water_total, self.m_air_current, self.m_water_current
            stuff.append(item)
            if self.p_air_current < self.p_atmosphere:
                break
        # Blow down
        while self.p_air_current > self.p_atmosphere:
            self.time += self.dt
            self.time_list.append(self.time)
            # Mass Flow analysis
            self.massFlowBlowdown()
            self.calcBlowdownThrust()
            # Add shit to list
            item = self.time, self.thrust[-1], self.m_dot_list[-1], (
                self.m_water_current + self.m_air_current), self.vol_air_current, self.vol_water_current, \
                   self.vol_air_total, self.vol_water_total, self.m_air_current, self.m_water_current
            stuff.append(item)
        self.output()
        return stuff
