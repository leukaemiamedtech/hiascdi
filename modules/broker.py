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

from bson import json_util, ObjectId
from flask import Response

class broker():
	""" HIASCDI Context Broker Module.

	This module provides core helper functions for HIASCDI.
	"""

	def __init__(self, helpers, mongodb):
		""" Initializes the class. """

		self.helpers = helpers
		self.program = "HIASCDI Helper Module"

		self.mongodb = mongodb

		self.headers = {
			"content-type": self.helpers.confs["contentType"]
		}

		self.auth = (self.helpers.credentials["identifier"],
					self.helpers.credentials["auth"])

		self.helpers.logger.info("HIASCDI initialization complete.")

	def checkAcceptsType(self, headers):
		""" Checks the request Accept types. """

		accepted = headers.getlist('accept')
		accepted = accepted[0].split(",")

		if "Accept" not in headers:
			return False

		for i, ctype in enumerate(accepted):
			if ctype not in self.helpers.confs["acceptTypes"]:
				accepted.pop(i)

		if len(accepted):
			return accepted
		else:
			return False

	def checkContentType(self, headers):
		""" Checks the request Content-Type. """

		content_type = headers["Content-Type"]

		if "Content-Type" not in headers or content_type not in self.helpers.confs["contentTypes"]:
			return False
		return content_type

	def checkBody(self, payload, text=False):
		""" Checks the request body is valid. """

		response = False
		message = "valid"

		if text is False:
			try:
				json_object = json.loads(json.dumps(payload.json))
				response = json_object
			except TypeError as e:
				response = False
				message = "invalid"
		else:
			if payload.data == "":
				response = False
				message = "invalid"
			else:
				response = payload.data

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
		""" Checks if a value is a int. """

		return True if value.isdigit() else False

	def cast(self, val):
		""" Casts relevant values as float or int. """

		if self.checkFloat(val):
			val = float(val)
		elif self.checkInteger(val):
			val = int(val)

		return val

	def prepareResponse(self, response):
		""" Converts response to bytes. """

		if isinstance(response, dict):
			response = json.dumps(response)
		elif isinstance(response, list):
			response = json.dumps(response)
		elif isinstance(response, int):
			response = str(response).encode(encoding='UTF-8')
		elif isinstance(response, float):
			response = str(response).encode(encoding='UTF-8')
		elif isinstance(response, str):
			response = response.encode(encoding='UTF-8')
		elif isinstance(response, bool):
			response = response.encode(encoding='UTF-8')

		return response

	def respond(self, responseCode, response, headers={},
				override = False, accepted = []):
		""" Builds the request repsonse """

		return_as = "json"
		if override != False:
			if override == "application/json":
				return_as = "json"
			elif override == "text/plain":
				return_as = "text"
		elif override == False:
			if "application/json" in accepted:
				return_as = "json"
			elif "text/plain" in accepted:
				return_as = "text"

		if return_as == "json":
			response =  Response(response=json.dumps(json.loads(json_util.dumps(response)),
											indent=4), status=responseCode,
						mimetype="application/json")
			headers['Content-Type'] = 'application/json'
		elif return_as == "text":
			if "text/plain" not in accepted:
				response = Response(response=self.helpers.confs["errorMessages"]["400b"],
								status=400, mimetype="application/json")
				headers['Content-Type'] = 'application/json'
			else:
				response = self.broker.prepareResponse(response)
				response = Response(response=response, status=responseCode,
								mimetype="text/plain")
				headers['Content-Type'] = 'text/plain; charset=utf-8'
		response.headers = headers

		return response

