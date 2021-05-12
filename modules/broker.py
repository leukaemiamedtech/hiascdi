""" HIASCDI Context Broker Module.

This module provides core helper functions for HIASCDI.

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

import json
import requests

import pandas as pd

class broker():
	""" HIASCDI Context Broker Module.

	This module provides core helper functions for HIASCDI.
	"""

	def __init__(self, helpers, mongodb):
		""" Initializes the class. """

		self.helpers = helpers
		self.program = "HIASCDI Helper Module"

		self.mongodb = mongodb

		self.accepted = []

		self.headers = {
			"content-type": self.helpers.confs["contentType"]
		}

		self.auth = (self.helpers.confs["identifier"],
					self.helpers.confs["auth"])

		self.helpers.logger.info("HIASCDI initialization complete.")

	def checkAcceptsType(self, headers):
		""" Checks the request Accept types. """

		self.accepted = headers.getlist('accept')
		self.accepted = self.accepted[0].split(",")

		if "Accept" not in headers:
			return False

		for i, ctype in enumerate(self.accepted):
			if ctype not in self.helpers.confs["contentTypes"]:
				self.accepted.pop(i)

		if len(self.accepted):
			return True
		else:
			return False

	def checkContentType(self, headers):
		""" Checks the request Content-Type. """

		response = True
		if "Content-Type" not in headers or headers["Content-Type"] not in self.helpers.confs["contentTypes"]:
			response = False
		return response

	def checkJSON(self, payload):
		""" Checks the request body is valid JSON. """

		response = False
		message = "valid"

		try:
			json_object = json.loads(json.dumps(payload))
			response = True
		except TypeError as e:
			response = False
			message = "invalid"

		self.helpers.logger.info("Request data " + message)

		return response

	def checkFloat(self, value):
		""" Checks if a value is a float. """

		try:
			float(value)
			return True
		except ValueError:
			return False

	def checkInteger(self, value):
		""" Checks if a value is a float. """

		return True if value.isdigit() else False

