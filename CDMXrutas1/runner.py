#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2022 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Manuel Hernandez Rosales
# @author  Pablo Benitez
# @date    2023-09-20

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import numpy as np


# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary 
import traci
import math
import random
import re

#begin and end time of edges closed
bt=60.0
et=3600.0

#edges closed
edgesclosed="616921713#6 618028623#12 79431129 -124181617#1 -124181617#3 -124181617#2 846008895"

#vehicles disallowed
vehdisa="private"

def closingedges():
    ar=edgesclosed.split(' ')
    h = open ('./closededges.add.xml','w')
    h.write("""<?xml version="1.0" encoding="UTF-8"?>\n<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">\n""")
    h.write("<rerouter id='rr1' edges='""" + edgesclosed + "' pos='194.00,195.40' probability='1'>\n")
    h.write("<interval begin='" + str(bt) + "' end='" + str(et) + "'>\n")
    for a in ar:
        h.write("<closingReroute id='" + a + "' allow='" + vehdisa + "'/>\n")
    h.write("</interval>\n")
    h.write("</rerouter>\n")
    h.write("""</additional>""")
    h.close

def newroutes():
    h = open('./osm.passenger.trips.xml', 'r')
    l = open('./ejbloqueo.rou.xml', 'w')
    ar=edgesclosed.split(' ')
    for f in h:
        for via in ar:
            if  f.find(via)>=0:
                    f=f.replace(via, "618106730#3")
        l.write(f)            
    h.close
    l.close

def newroutesp():
    h = open('./osm.pedestrian.rou.xml', 'r')
    l = open('./ejbloqueo.rou.xml', 'w')
    ar=edgesclosed.split(' ')
    for f in h:
        for via in ar:
            if  f.find(via)>=0:
                    f=f.replace(via, "618106730#3")
        l.write(f)            
    h.close
    l.close    

def createejbloqueo():
    h = open ('./ejbloqueo.sumocfg','w')
    h.write("<?xml version='1.0' encoding='UTF-8'?>\n<configuration xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:noNamespaceSchemaLocation='http://sumo.dlr.de/xsd/sumoConfiguration.xsd'>\n<input>\n<net-file value='osm.net.xml'/>\n<route-files value='ejbloqueo.rou.xml'/>\n<additional-files value='closededges.add.xml'/>\n</input>\n</configuration>")
    h.close()

def run():
    step = 0
    #elegimos una semilla aleatoria
    random.seed()
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()    
        step += 1
    traci.close()
    sys.stdout.flush()



def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    closingedges()
    newroutes()
    newroutesp()
    createejbloqueo()
    
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    traci.start([sumoBinary, "-c", "ejbloqueo.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
