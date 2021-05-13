#!/usr/bin/env python
""" HIASCDI Types Module.

This module provides the functionality to retrieve
HIASCDI entity types.

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
import os

from bson import json_util, ObjectId

from flask import Response

class types():
	""" HIASCDI Types Module.

	This module provides the functionality to retrieve
	HIASCDI entity types.
	"""

	def __init__(self, helpers, mongodb, broker):
		""" Initializes the class. """

		self.helpers = helpers
		self.program = "HIASCDI Types Module"

		self.mongodb = mongodb
		self.broker = broker

		self.helpers.logger.info(self.program + " initialization complete.")

	def getTypes(self, arguments, accepted=[]):
		""" Gets entity types data from the MongoDB.

		You can access this endpoint by naviating your browser to https://YourServer/hiascdi/v1/types
		If you are not logged in to the HIAS network you will be shown an authentication pop up
		where you should provide your HIAS network user and password.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Types
					- Entity types
						- List Entity types
		"""

		count_opt = False
		values_opt = False

		query = {}
		headers = {}

		# Removes the MongoDB ID
		fields = {
			'_id': False
		}

		# Processes the options parameter
		options = arguments.get('options') if arguments.get(
			'options') is not None else None
		if options is not None:
			options = options.split(",")
			for option in options:
				values_opt = True if option == "values" else values_opt
				count_opt = True if option == "count" else count_opt

		# Prepares the offset
		if arguments.get('offset') is None:
			offset = False
		else:
			offset = int(arguments.get('offset'))

		# Prepares the query limit
		if arguments.get('limit') is None:
			limit = 0
		else:
			limit = int(arguments.get('limit'))

		if offset:
			types = self.mongodb.mongoConn.Types.find(
				query, fields).skip(offset).limit(limit)
		else:
			types = self.mongodb.mongoConn.Types.find(
				query, fields).limit(limit)

		if count_opt:
			# Sets count header
			headers["Count"] = types.count()

		if values_opt:
			# Converts data to values
			newData = []
			for i, typ in enumerate(types):
				newData.append(typ["type"])
			types = newData

		return self.broker.respond(200, types, headers, False, accepted)

	def createType(self, data, accepted=[]):
		""" Creates a new HIASCDI Entity Type.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Types
					- Entity types
						- Create Entity types (Custom)
		"""

		try:
			_id = self.mongodb.mongoConn.Types.insert(data)
			return self.broker.respond(201, {}, {"Location": "v1/types/" + data["type"]},
								False, accepted)
		except:
			e = sys.exc_info()
			self.helpers.logger.info("Mongo data inserted FAILED!")
			self.helpers.logger.info(str(e))
			return self.broker.respond(400, self.helpers.confs["errorMessages"]["400b"], {},
								False, accepted)

	def updateTypePatch(self, _id, data, accepted=[]):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Types
					- Entity types
						- Update Entity types (Custom)
		"""

		updated = False
		error = False

		for update in data:
			self.mongodb.mongoConn.Types.update_one({"type": data['type']},
											{"$set": {update: data[update]}})
			updated = True

		if updated and error is False:
			return self.broker.respond(204, self.helpers.confs["successMessage"][str(204)],
								{}, False, accepted)
		else:
			return self.broker.respond(400, self.helpers.confs["errorMessages"]["400b"],
								{}, False, accepted)

	def getType(self, _type, accepted=[]):
		""" Gets entity type data from the MongoDB.

		You can access this endpoint by naviating your browser to https://YourServer/hiascdi/v1/types
		If you are not logged in to the HIAS network you will be shown an authentication pop up
		where you should provide your HIAS network user and password.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Types
					- Entity type
						- Retrieve Entity type
		"""

		query = {'type': _type}
		headers = {}

		# Removes the MongoDB ID
		fields = {
			'_id': False,
			'type': False
		}

		_type = self.mongodb.mongoConn.Types.find(
				query, fields)

		return self.broker.respond(200, _type, headers, False, accepted)

