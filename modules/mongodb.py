#!/usr/bin/env python3
""" HIASCDI MongoDB Helper Module.

The HIASCDI MongoDB Helper Module provides MongoDB helper
functions to the HIASCDI application.

MIT License

Copyright (c) 2021 Asociación de Investigacion en Inteligencia Artificial
Para la Leucemia Peter Moss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contributors:
- Adam Milton-Barker

"""

import sys

from pymongo import MongoClient

class mongodb():
    """ HIASCDI MongoDB Helper Module.

    The HIASCDI MongoDB Helper Module provides MongoDB helper
    functions to the HIASCDI application.
    """

    def __init__(self, helpers):
        """ Initializes the class. """

        self.program = "MongoDB Helper Module"

        self.helpers = helpers
        self.confs = self.helpers.confs
        self.credentials = self.helpers.credentials

        self.helpers.logger.info(self.program + " initialization complete.")

    def start(self):
        """ Connects to HIAS MongoDB database. """

        self.mongoCon = MongoClient(
            self.credentials["mongodb"]["host"])

        self.mongoConn = self.mongoCon[
            self.credentials["mongodb"]["db"]]

        self.mongoConn.authenticate(self.credentials["mongodb"]["un"],
                                    self.credentials["mongodb"]["up"])

        self.collextions = {
            "Actuator": self.mongoConn.Actuators,
            "Agent": self.mongoConn.Entities,
            "Application": self.mongoConn.Entities,
            "ApplicationZone": self.mongoConn.ApplicationZones,
            "Automation": self.mongoConn.Automation,
            "HIASCDI": self.mongoConn.Entities,
            "HIASHDI": self.mongoConn.Entities,
            "Device": self.mongoConn.Entities,
            "Location": self.mongoConn.Entities,
            "Model": self.mongoConn.Entities,
            "Robotics": self.mongoConn.Entities,
            "Patient": self.mongoConn.Entities,
            "Sensors": self.mongoConn.Sensors,
            "Staff": self.mongoConn.Entities,
            "Thing": self.mongoConn.Entities,
            "Zone": self.mongoConn.Entities
        }
