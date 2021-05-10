#!/usr/bin/env python
""" HIASCDI Entities Module.

This module provides the functionality to create, retrieve
and update HIASCDI entities.

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
import jsonpickle
import os
import sys

from mgoquery import Parser

from bson import json_util, ObjectId
from flask import Response

class entities():
	""" HIASCDI Entities Module.

	This module provides the functionality to create, retrieve
	and update HIASCDI entities.
	"""

	def __init__(self, helpers, mongodb, broker):
		""" Initializes the class. """

		self.helpers = helpers
		self.program = "HIASCDI Entities Module"

		self.mongodb = mongodb
		self.broker = broker

		self.helpers.logger.info(self.program + " initialization complete.")

	def getEntities(self, arguments):
		""" Gets entity data from the MongoDB.

		You can access this endpoint by naviating your browser to https://YourServer/hiascdi/v1/entities
		If you are not logged in to the HIAS network you will be shown an authentication pop up
		where you should provide your HIAS network user and password.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- List entities
		"""

		params = []
		cparams = []
		sort = []
		query = {}
		headers = {}

		keyValues_opt = False
		count_opt = False
		values_opt = False
		unique_opt = False

		options = arguments.get('options') if arguments.get('options') is not None else None
		if options is not None:
			options = options.split(",")
			for option in options:
				keyValues_opt = True if option == "keyValues" else keyValues_opt
				values_opt = True if option == "values" else values_opt
				unique_opt = True if option == "unique" else unique_opt
				count_opt = True if option == "count" else count_opt

		# Removes the MongoDB ID & builtin attributes
		fields = {
			'_id': False
		}

		if keyValues_opt or values_opt:
			# Removes type
			fields.update({'type': False})
			fields.update({'metadata': False})

		# Sets a type query
		if arguments.get('type') is not None:
			eor = []
			types = arguments.get('type').split(",")
			if len(types) == 1:
				query.update({"type":
						{'$in': [types[0]]}
					})
			else:
				for eid in types:
					eor.append({"type":
							{'$in': [eid]}
						})
				params.append({"$or": eor})
		elif arguments.get('typePattern') is not None:
			query.update({"type":
					{'$regex': arguments.get('typePattern')}
				})

		# Sets a id query
		if arguments.get('id') is not None:
			eor = []
			ids = arguments.get('id').split(",")
			if len(ids) == 1:
				query.update({"id":
						{'$in': [ids[0]]}
					})
			else:
				for eid in ids:
					eor.append({"id":
							{'$in': [eid]}
						})
				params.append({"$or": eor})
		elif arguments.get('idPattern') is not None:
			query.update({"id":
					{'$regex': arguments.get('idPattern')}
				})

		# Sets a category query
		if arguments.get('category') is not None:
			eor = []
			categories = arguments.get('category').split(",")
			if len(categories) == 1:
				query.update({"category.value":
						{'$in': [categories[0]]}
					})
			else:
				for category in categories:
					eor.append({"category.value":
							{'$in': [category]}
						})
				params.append({"$or": eor})

		# Sets a attrs query

		if arguments.get('attrs') is not None:
			attribs = arguments.get('attrs').split(",")
			if '*' in attribs:
				if 'dateCreated' not in attribs:
					fields.update({'dateCreated': False})
				if 'dateModified' not in attribs:
					fields.update({'dateModified': False})
				if 'dateExpired' not in attribs:
					fields.update({'dateExpired': False})
			else:
				for attr in attribs:
					fields.update({attr: True})

		# Sets a q query
		if arguments.get('q') is not None:
			qs = arguments.get('q').split(",")
			for q in qs:
				if "==" in q:
					qp = q.split("==")
					query.update({qp[0]: int(qp[1]) if qp[1].isdigit() else qp[1]})
				if  ":" in q:
					qp = q.split(":")
					query.update({qp[0]: int(qp[1]) if qp[1].isdigit() else qp[1]})
				if "!=" in q:
					qp = q.split("!=")
					query.update({qp[0]: {"$ne": int(qp[1]) if qp[1].isdigit() else qp[1]}})
				if "<" in q:
					qp = q.split("<")
					query.update({qp[0]: {"$lt": int(qp[1])}})
				if "<=" in q:
					qp = q.split("<=")
					query.update({qp[0]: {"$lte": int(qp[1])}})
				if ">" in q:
					qp = q.split("<")
					query.update({qp[0]: {"$gt": int(qp[1])}})
				if ">=" in q:
					qp = q.split(">=")
					query.update({qp[0]: {"$gte": int(qp[1])}})

		# Sets a geospatial query
		if arguments.get('georel') is not None and arguments.get('geometry') is not None and arguments.get('coords') is not None:
			georels = arguments.get('georel').split(";")
			georelslen = len(georels)
			coords = arguments.get('coords').split(";")
			coordslen = len(coords)
			geometry = arguments.get('geometry').capitalize()
			geotype = georels[0]
			if geotype == 'near':
				# Near geospatial query
				if geometry != "Point":
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				if georelslen < 2:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				if coordslen > 1:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				data = {"location.value": {
					"$near": {
						"$geometry": {
							"type": geometry,
							"coordinates": [float(p) for p in coords[0].split(",")]
						}
					}
				}}

				modifiers = georels[1:]
				for modifier in modifiers:
					msplit = modifier.split(":")
					data["location.value"]["$near"].update({"$"+msplit[0]: int(msplit[1])})
				query.update(data)
			elif geotype == 'intersects':
				# Intersects geospatial query
				if geometry != "Polygone":
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				if coordslen > 4:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				polygone = []
				for poly in coords:
					polygone.append([float(p) for p in poly.split(",")])

				query.update({"location.value": {
					"$geoIntersects": {
						"$geometry": {
							"type": geometry,
							"coordinates": polygone
						}
					}
				}})
			elif geotype == 'coveredBy':
				# coveredBy geospatial query
				if geometry != "Polygone":
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				if coordslen > 4:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

				polygone = []
				for poly in coords:
					polygone.append([float(p) for p in poly.split(",")])

				query.update({"location.value": {
					"$geoWithin": {
						"$geometry": {
							"type": geometry,
							"coordinates": polygone
						}
					}
				}})
			elif geotype == 'equals':
				# Equals geospatial query
				eor = []
				coords = arguments.get('coords').split(";")
				for coord in coords:
					coord = coord.split(",")
					eor.append({"location.value.coordinates": [
								float(coord[0]), float(coord[1])]})
				params.append({"$or": eor})
			elif geotype == 'disjoint':
				# Disjoint geospatial query
				return self.respond(501, self.helpers.confs["errorMessages"][str(501)])
			else:
				# None supported geospatial query
				return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

		# TO REMOVE
		if arguments.get('values') is not None:
			valuesArr = arguments.get('values').split(",")
			for value in valuesArr:
				pair = value.split("|")
				query.update({pair[0]: int(pair[1]) if pair[1].isdigit() else pair[1]})


		if len(params):
			query.update({"$and": params})

		# Sets the query ordering
		if arguments.get('orderBy') is not None:
			orders = arguments.get('orderBy').split(",")
			for order in orders:
				if order[0] is "!":
					orderBy = -1
					order = order[1:]
				else:
					orderBy = 1
				sort.append((order, orderBy))

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

		try:
			# Creates the full query
			if len(sort) and offset:
				entities = self.mongodb.mongoConn.Entities.find(
					query, fields).skip(offset).sort(sort).limit(limit)
			elif offset:
				entities = self.mongodb.mongoConn.Entities.find(
					query, fields).skip(offset).limit(limit)
			elif len(sort):
				entities = self.mongodb.mongoConn.Entities.find(
					query, fields).sort(sort).limit(limit)
			else:
				entities= self.mongodb.mongoConn.Entities.find(query, fields).limit(limit)

			if count_opt:
				# Sets count header
				headers["Count"] = entities.count()

			entities = list(entities)

			if not len(entities):
				self.helpers.logger.info(
					self.program + " 404: " + self.helpers.confs["errorMessages"][str(404)]["Description"])

				return self.respond(404, self.helpers.confs["errorMessages"][str(404)])
			else:

				if keyValues_opt:
					newData = []
					for i, entity in enumerate(entities):
						dataHolder = {}
						for attr in entity:
							if isinstance(entity[attr], str):
								dataHolder.update({attr: entity[attr]})
							if isinstance(entity[attr], dict):
								dataHolder.update({attr: entity[attr]["value"]})
							if isinstance(entity[attr], list):
								dataHolder.update({attr: entity[attr]})
						newData.append(dataHolder)
					entities = newData

				elif values_opt:
					newData = []
					for i, entity in enumerate(entities):
						dataHolder = []
						for attr in entity:
							if isinstance(entity[attr], str):
								dataHolder.append(entity[attr])
							if isinstance(entity[attr], dict):
								dataHolder.append(entity[attr]["value"])
							if isinstance(entity[attr], list):
								dataHolder.append(entity[attr])
						newData.append(dataHolder)
					entities = newData

				elif unique_opt:
					newData = []
					for i, entity in enumerate(entities):
						dataHolder = []
						for attr in entity:
							if isinstance(entity[attr], str):
								dataHolder.append(entity[attr])
							if isinstance(entity[attr], dict):
								dataHolder.append(entity[attr]["value"])
							if isinstance(entity[attr], list):
								dataHolder.append(entity[attr])
						[newData.append(x) for x in dataHolder if x not in newData]
					entities = newData

				self.helpers.logger.info(
					self.program + " 200: " + self.helpers.confs["successMessage"][str(200)]["Description"])

				return self.respond(200, json.loads(json_util.dumps(entities)), None, headers)
		except Exception as e:
			print(e)
			self.helpers.logger.info(
				self.program + " 404: " + self.helpers.confs["errorMessages"][str(404)]["Description"])

			return self.respond(404, self.helpers.confs["errorMessages"][str(404)])

	def getEntity(self, typeof, _id, attrs, options):
		""" Gets a specific HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Retrieve Entity
		"""

		keyValues_opt = False
		count_opt = False
		values_opt = False
		unique_opt = False

		if options is not None:
			options = options.split(",")
			for option in options:
				keyValues_opt = True if option == "keyValues" else keyValues_opt
				values_opt = True if option == "values" else values_opt
				unique_opt = True if option == "unique" else unique_opt

		query = {'id': _id}

		# Removes the MongoDB ID
		fields = {
			'_id': False
		}

		if attrs is not None:
			attribs = attrs.split(",")
			if '*' in attribs:
				if 'dateCreated' not in attribs:
					fields.update({'dateCreated': False})
				if 'dateModified' not in attribs:
					fields.update({'dateModified': False})
				if 'dateExpired' not in attribs:
					fields.update({'dateExpired': False})
			else:
				for attr in attribs:
					fields.update({attr: True})

		if typeof is not None:
			query.update({"type": typeof})

		entity = list(self.mongodb.mongoConn.Entities.find(query, fields))

		if not entity:
			self.helpers.logger.info(
				self.program + " 404: " + self.helpers.confs["errorMessages"][str(404)]["Description"])

			return self.respond(404, self.helpers.confs["errorMessages"][str(404)])
		elif len(entity) > 1:
			self.helpers.logger.info(
				self.program + " 409: " + self.helpers.confs["errorMessages"][str(409)]["Description"])

			return self.respond(409, self.helpers.confs["errorMessages"][str(409)])
		else:
			data = entity[0]

			if keyValues_opt:
				newData = {}
				for attr in list(data):
					if isinstance(data[attr], str):
						newData.update({attr: data[attr]})
					if isinstance(data[attr], dict):
						newData.update({attr: data[attr]["value"]})
					if isinstance(data[attr], list):
						newData.update({attr: data[attr]})
				data = newData

			elif values_opt:
				newData = []
				for attr in list(data):
					if isinstance(data[attr], str):
						newData.append(data[attr])
					if isinstance(data[attr], dict):
						newData.append(data[attr]["value"])
					if isinstance(data[attr], list):
						newData.append(data[attr])
				data = newData

			elif unique_opt:
				newData = []
				for attr in list(data):
					if isinstance(data[attr], str):
						newData.append(data[attr])
					if isinstance(data[attr], dict):
						newData.append(data[attr]["value"])
					if isinstance(data[attr], list):
						newData.append(data[attr])
				data = []
				[data.append(x) for x in newData if x not in data]

			self.helpers.logger.info(
				self.program + " 200: " + self.helpers.confs["successMessage"][str(200)]["Description"])

			return self.respond(200, json.loads(json_util.dumps(data)))

	def createEntity(self, data):
		""" Creates a new HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Create Entity
		"""

		if data["type"] not in self.mongodb.collextions:
			data["type"] = "Thing"

		_id = self.insert(self.mongodb.mongoConn.Entities, data, data["type"])

		if str(_id) is not False:
			return self.respond(201, {}, "v1/entities/" + data["id"] + "?type=" + data["type"])
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

	def updateEntityPost(self, _id, typeof, data):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Update or Append Entity Attributes
		"""

		updated = False

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		for update in data:
			self.mongodb.mongoConn.Entities.update_one({"id" : _id}, {"$set": {update: data[update]}}, upsert=True)
			updated = True

		if updated:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)])
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

	def updateEntityPatch(self, _id, typeof, data):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Update Existing Entity Attributes
		"""

		failed = False

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		for update in data:
			updated = self.mongodb.mongoConn.Entities.update_one({"id" : _id}, {"$set": {update: data[update]}});
			if updated.matched_count == 0:
				failed = True

		if failed:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])
		else:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)])

	def updateEntityPut(self, _id, typeof, data):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
					- Replace all entity attributes
		"""

		updated = False

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		entity = list(self.mongodb.mongoConn.Entities.find({"id" : _id}))

		for update in data:
			if update in entity[0]:
				self.mongodb.mongoConn.Entities.update({"id" : _id}, {'$unset': {update: ""}})
			updated = self.mongodb.mongoConn.Entities.update_one({"id" : _id}, {"$set": {update: data[update]}}, upsert=True);

		if failed:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])
		else:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)])

	def deleteEntity(self, typeof, _id):
		""" Deletes an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
					- Remove entity
		"""

		if typeof in self.mongodb.collextions:
			collection = self.mongodb.collextions[typeof]
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

		deleted = False
		result = collection.delete_one({"id": _id});

		if result.deleted_count is True:
			self.helpers.logger.info("Mongo data delete OK")
			return self.respond(204, {})
		else:
			self.helpers.logger.info("Mongo data delete FAILED")
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"])

	def insert(self, collection, doc, entity):
		""" Creates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
					- Remove entity
		"""

		try:
			_id = collection.insert(doc)
			self.helpers.logger.info("Mongo data inserted OK")
			if entity is "Device":
				self.mongodb.Locations.find_one_and_update(
						{"id": doc.lid.entity},
						{'$inc': {'devices.value': 1}}
					)
				self.mongodb.Zones.find_one_and_update(
						{"id": doc.zid.entity},
						{'$inc': {'devices.value': 1}}
					)
			if entity is "Application":
				self.mongodb.Locations.find_one_and_update(
						{"id": doc.lid.entity},
						{'$inc': {'applications.value': 1}}
					)
				self.helpers.logger.info("Mongo data update OK")
			return _id
		except:
			e = sys.exc_info()
			self.helpers.logger.info("Mongo data inserted FAILED!")
			self.helpers.logger.info(str(e))
			return False

	def respond(self, responseCode, response, location=None, headers=[]):
		""" Builds the request repsonse """

		response = Response(response=json.dumps(response, indent=4),
						status=responseCode, mimetype="application/json")

		if len(headers):
			response.headers = headers

		return response
