#!/usr/bin/env python
""" HIASCDI Subscriptions Module.

This module provides the functionality to retrieve, create, update
and deletec HIASCDI subscriptions.

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
import uuid
import sys

from bson import json_util, ObjectId

from flask import Response


class subscriptions():
	""" HIASCDI Subscriptions Module.

	This module provides the functionality to retrieve, create, update
	and deletec HIASCDI subscriptions.
	"""

	def __init__(self, helpers, mongodb, broker):
		""" Initializes the class. """

		self.helpers = helpers
		self.program = "HIASCDI Subscriptions Module"

		self.mongodb = mongodb
		self.broker = broker

		self.helpers.logger.info(self.program + " initialization complete.")

	def getSubscriptions(self, arguments, accepted=[]):
		""" Gets subscription data from the MongoDB.

		You can access this endpoint by naviating your browser to https://YourServer/hiascdi/v1/types
		If you are not logged in to the HIAS network you will be shown an authentication pop up
		where you should provide your HIAS network user and password.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Subscriptions
					- Subscription List
						- List Subscriptions
		"""

		count_opt = False

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
			subscriptions = self.mongodb.mongoConn.Subscriptions.find(
				query, fields).skip(offset).limit(limit)
		else:
			subscriptions = self.mongodb.mongoConn.Subscriptions.find(
				query, fields).limit(limit)

		if count_opt:
			# Sets count header
			headers["Count"] = subscriptions.count()

		return self.broker.respond(200, subscriptions, headers, False, accepted)

	def createSubscription(self, data, accepted=[]):
		""" Creates a new HIASCDI Subscription.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Subscriptions
					- Subscription List
						- List Subscriptions
		"""

		nuuid = str(uuid.uuid4())
		newData = {"id": nuuid}
		newData.update(data)
		data = newData

		try:
			_id = self.mongodb.mongoConn.Subscriptions.insert(data)
			return self.broker.respond(201, {}, {"Location": "v1/subscription/" + data["id"]},
								False, accepted)
		except:
			e = sys.exc_info()
			self.helpers.logger.info("Mongo data inserted FAILED!")
			self.helpers.logger.info(str(e))
			return self.broker.respond(400, self.helpers.confs["errorMessages"]["400b"], {},
								False, accepted)

	def getSubscription(self, subscription, accepted=[]):
		""" Gets subscription data from the MongoDB.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Subscriptions
					- Subscription List
						- Subscription By ID
							- Retrieve Subscription
		"""

		query = {'id': subscription}
		headers = {}

		# Removes the MongoDB ID
		fields = {
			'_id': False
		}

		sub = self.mongodb.mongoConn.Subscriptions.find(
				query, fields)

		sub = sub[0]

		return self.broker.respond(200, sub, headers, False, accepted)

	def updateSubscription(self, subscription, data, accepted=[]):
		""" Updates subscription data in MongoDB.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Subscriptions
					- Subscription List
						- Subscription By ID
							- Update Subscription
		"""

		updated = False

		for update in data:
			self.mongodb.mongoConn.Subscriptions.update_one({"id" : subscription},
						{"$set": {update: data[update]}}, upsert=True)
			updated = True

		if updated:
			return self.broker.respond(204, self.helpers.confs["successMessage"][str(204)],
								{}, False, accepted)
		else:
			return self.broker.respond(400, self.helpers.confs["errorMessages"]["400b"],
								{}, False, accepted)