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

	def getEntities(self, arguments, accepted=[]):
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

		# Processes the options parameter
		options = arguments.get('options') if arguments.get('options') is not None else None
		if options is not None:
			options = options.split(",")
			for option in options:
				keyValues_opt = True if option == "keyValues" else keyValues_opt
				values_opt = True if option == "values" else values_opt
				unique_opt = True if option == "unique" else unique_opt
				count_opt = True if option == "count" else count_opt

		# Removes the MongoDB ID
		fields = {
			'_id': False
		}

		if arguments.get('type') is not None:
			# Sets a type query
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

		if arguments.get('id') is not None:
			# Sets a id query
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

		if arguments.get('category') is not None:
			# Sets a category query
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

		attribs = []
		if arguments.get('attrs') is not None:
			# Sets a attrs query
			attribs = arguments.get('attrs').split(",")
			if '*' in attribs:
				# Removes builtin attributes
				if 'dateCreated' not in attribs:
					fields.update({'dateCreated': False})
				if 'dateModified' not in attribs:
					fields.update({'dateModified': False})
				if 'dateExpired' not in attribs:
					fields.update({'dateExpired': False})
			else:
				for attr in attribs:
					fields.update({attr: True})

		mattribs = []
		if arguments.get('metadata') is not None:
			# Sets a metadata query
			mattribs = arguments.get('metadata').split(",")
			if '*' in mattribs:
				# Removes builtin attributes
				if 'dateCreated' not in mattribs:
					fields.update({'dateCreated': False})
				if 'dateModified' not in mattribs:
					fields.update({'dateModified': False})
				if 'dateExpired' not in mattribs:
					fields.update({'dateExpired': False})
			else:
				for attr in mattribs:
					fields.update({attr: True})

		if arguments.get('q') is not None:
			# Sets a q query
			qs = arguments.get('q').split(";")
			for q in qs:
				if "==" in q:
					qp = q.split("==")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$in': [searcher]}
					})
				elif  ":" in q:
					qp = q.split(":")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$in': [searcher]}
					})
				elif "!=" in q:
					qp = q.split("!=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$ne': searcher}
					})
				elif ">=" in q:
					qp = q.split(">=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$gte': searcher}
					})
				elif "<=" in q:
					qp = q.split("<=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$lte': searcher}
					})
				elif "<" in q:
					qp = q.split("<")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$lt': searcher}
					})
				elif ">" in q:
					qp = q.split(">")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$gt': searcher}
					})

		elif arguments.get('mq') is not None:
			# Sets an mq query
			qs = arguments.get('mq').split(";")
			for q in qs:
				if "==" in q:
					qp = q.split("==")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$in': [searcher]}
					})
				elif  ":" in q:
					qp = q.split(":")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$in': [searcher]}
					})
				elif "!=" in q:
					qp = q.split("!=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$ne': searcher}
					})
				elif ">=" in q:
					qp = q.split(">=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$gte': searcher}
					})
				elif "<=" in q:
					qp = q.split("<=")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$lte': searcher}
					})
				elif "<" in q:
					qp = q.split("<")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$lt': searcher}
					})
				elif ">" in q:
					qp = q.split(">")
					searcher = qp[1]

					if self.broker.checkFloat(qp[1]):
						searcher = float(searcher)

					if self.broker.checkInteger(qp[1]):
						searcher = int(searcher)

					query.update({qp[0]:
						{'$gt': searcher}
					})

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
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

				if georelslen < 2:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

				if coordslen > 1:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

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
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

				if coordslen > 4:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

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
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

				if coordslen > 4:
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

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
				return self.respond(501, self.helpers.confs["errorMessages"][str(501)],
									None, {}, False, accepted)
			else:
				# Non-supported geospatial query
				return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
									None, {}, False, accepted)

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

				return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
									None, {}, False, accepted)
			else:

				# Converts data to key -> value
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

				# Converts data to values
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

				# Converts data to unique values
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

				return self.respond(200, entities, None, headers)
		except Exception as e:
			print(e)
			self.helpers.logger.info(
				self.program + " 404: " + self.helpers.confs["errorMessages"][str(404)]["Description"])

			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)

	def createEntity(self, data, accepted=[]):
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

		_id = self.insert(self.mongodb.mongoConn.Entities, data, data["type"], accepted)

		if str(_id) is not False:
			return self.respond(201, {}, "v1/entities/" + data["id"] + "?type=" + data["type"],
								None, {}, False, accepted)
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

	def insert(self, collection, doc, entity, accepted=[]):
		""" Creates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Create Entity
						- Create Entity
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

	def getEntity(self, typeof, _id, attrs, options, metadata,
					attributes=False, accepted=[]):
		""" Gets a specific HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Retrieve Entity / Retrieve Entity Attributes
		"""

		keyValues_opt = False
		count_opt = False
		values_opt = False
		unique_opt = False

		# Processes the options parameter
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

		clear_builtin = False

		attribs = []
		if attrs is not None:
			# Processes attrs parameter
			attribs = attrs.split(",")
			if '*' in attribs:
				# Removes builtin attributes
				if 'dateCreated' not in attribs:
					fields.update({'dateCreated': False})
				if 'dateModified' not in attribs:
					fields.update({'dateModified': False})
				if 'dateExpired' not in attribs:
					fields.update({'dateExpired': False})
			else:
				clear_builtin = True
				for attr in attribs:
					fields.update({attr: True})
		else:
			fields.update({'dateCreated': False})
			fields.update({'dateModified': False})
			fields.update({'dateExpired': False})

		mattribs = []
		if metadata is not None:
			# Processes metadata parameter
			mattribs = metadata.split(",")
			if '*' not in mattribs:
				clear_builtin = True
				for attr in mattribs:
					fields.update({attr: True})

		if typeof is not None:
			query.update({"type": typeof})

		entity = list(self.mongodb.mongoConn.Entities.find(query, fields))

		if not entity:
			self.helpers.logger.info(
				self.program + " 404: " + self.helpers.confs["errorMessages"][str(404)]["Description"])

			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		elif len(entity) > 1:
			self.helpers.logger.info(
				self.program + " 409: " + self.helpers.confs["errorMessages"][str(409)]["Description"])

			return self.respond(409, self.helpers.confs["errorMessages"][str(409)],
								None, {}, False, accepted)
		else:
			data = entity[0]

			if keyValues_opt:
				newData = {}
				# Converts data to key -> value
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
				# Converts data to values
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
				# Converts data to unique values
				for attr in list(data):
					if isinstance(data[attr], str):
						newData.append(data[attr])
					if isinstance(data[attr], dict):
						newData.append(data[attr]["value"])
					if isinstance(data[attr], list):
						newData.append(data[attr])
				data = []
				[data.append(x) for x in newData if x not in data]

			if clear_builtin:
				# Clear builtin data
				if "dateCreated" in data and 'dateCreated' not in attribs:
					del data["dateCreated"]
				if "dateModified" in data and 'dateModified' not in attribs:
					del data["dateModified"]
				if "dateExpired" in data and 'dateExpired' not in attribs:
					del data["dateExpired"]

			if attributes:
				if "id" in data and 'id' not in attribs:
					del data["id"]
				if "type" in data and 'type' not in attribs:
					del data["type"]

			self.helpers.logger.info(
				self.program + " 200: " + self.helpers.confs["successMessage"][str(200)]["Description"])

			return self.respond(200, data)

	def updateEntityPost(self, _id, typeof, data, options, accepted=[]):
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
		error = False
		_append = False
		_keyValues = False

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		if options is not None:
			options = options.split(",")
			for option in options:
				_append = True if option == "append" else _append
				_keyValues = True if option == "keyValues" else keyValues

		if _append:
			entity = list(self.mongodb.mongoConn.Entities.find({'id': _id}))
			for update in data:
				if update in entity[0]:
					error = True
				else:
					self.mongodb.mongoConn.Entities.update_one({"id" : _id},
											{"$set": {update: data[update]}}, upsert=True)
					updated = True
		else:
			for update in data:
				updated = self.mongodb.mongoConn.Entities.update_one({"id" : _id},
											{"$set": {update: data[update]}}, upsert=True)
				updated = True

		if updated and error is False:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)],
								None, {}, False, accepted)
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

	def updateEntityPatch(self, _id, typeof, data, options, accepted=[]):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Update Existing Entity Attributes
		"""

		updated = False
		error = False

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		_keyValues = False

		if options is not None:
			options = options.split(",")
			for option in options:
				_keyValues = True if option == "keyValues" else keyValues

		entity = list(self.mongodb.mongoConn.Entities.find({'id': _id}))
		for update in data:
			if update not in entity[0]:
				error = True
			else:
				self.mongodb.mongoConn.Entities.update_one({"id" : _id},
												{"$set": {update: data[update]}})
				updated = True

		if updated and error is False:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)],
								None, {}, False, accepted)
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

	def updateEntityPut(self, _id, typeof, data, options, accepted=[]):
		""" Updates an HIASCDI Entity.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Entities
					- Entity by ID
						- Replace all entity attributes
		"""

		if "id" in data:
			del data['id']

		if "type" in data:
			del data['type']

		fields = {
			'_id': False,
			'id': False,
			'type': False,
			'dateCreated': False,
			'dateModified': False,
			'dateExpired': False
		}

		updated = False
		_keyValues = False

		if options is not None:
			options = options.split(",")
			for option in options:
				_keyValues = True if option == "keyValues" else keyValues

		entity = list(self.mongodb.mongoConn.Entities.find({"id": _id}, fields))

		for e in entity:
			self.mongodb.mongoConn.Entities.update({"id": _id}, {'$unset': {e: ""}})

		for update in data:
			self.mongodb.mongoConn.Entities.update_one({"id" : _id},
									{"$set": {update: data[update]}}, upsert=True)
			updated = True

		if updated:
			return self.respond(204, self.helpers.confs["successMessage"][str(204)],
								None, {}, False, accepted)
		else:
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

	def deleteEntity(self, typeof, _id, accepted=[]):
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
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

		deleted = False
		result = collection.delete_one({"id": _id})

		if result.deleted_count is True:
			self.helpers.logger.info("Mongo data delete OK")
			return self.respond(204, {})
		else:
			self.helpers.logger.info("Mongo data delete FAILED")
			return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
								None, {}, False, accepted)

	def getEntityAttribute(self, typeof, _id, _attr, metadata, is_value=False, accepted=[]):
		""" Gets a specific HIASCDI Entity Attribute.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Attribute
					- Attribute by Entity ID
						- Get Attribute Data
		"""

		query = {'id': _id}

		# Removes the MongoDB ID
		fields = {
			'_id': False
		}

		mattribs = []
		if metadata is not None:
			# Processes metadata parameter
			mattribs = metadata.split(",")
			for attr in mattribs:
				fields.update({_attr + "." + attr: True})

		if typeof is not None:
			query.update({"type": typeof})

		entity = list(self.mongodb.mongoConn.Entities.find(query, fields))

		if not entity:
			self.helpers.logger.info(self.program + " 404: " + \
							self.helpers.confs["errorMessages"][str(404)]["Description"])
			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		elif len(entity) > 1:
			self.helpers.logger.info(self.program + " 409: " + \
							self.helpers.confs["errorMessages"][str(409)]["Description"])
			return self.respond(409, self.helpers.confs["errorMessages"][str(409)],
								None, {}, False, accepted)
		else:
			data = entity[0]

			if _attr not in data:
				self.helpers.logger.info(self.program + " 400: " + \
									self.helpers.confs["errorMessages"]["400b"]["Description"])
				return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
									None, {}, False, accepted)

			override = False
			data = data[_attr]
			if is_value:
				if "value" not in data:
					self.helpers.logger.info(self.program + " 400: " + \
						self.helpers.confs["errorMessages"]["400b"]["Description"])
					return self.respond(400, self.helpers.confs["errorMessages"]["400b"],
										None, {}, False, accepted)

				data = data["value"]
				override = "text/plain"

			self.helpers.logger.info(
				self.program + " 200: " + self.helpers.confs["successMessage"][str(200)]["Description"])

			return self.respond(200, data, None, {}, override, accepted)

	def updateEntityAttrPut(self, _id, _attr, typeof, data, is_value, accepted = None, content_type = None):
		""" Updates an HIASCDI Entity Attribute.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Attribute
					- Attribute by Entity ID
						- Update Attribute Data
		"""

		query = {"id": _id}

		if typeof is not None:
			query.update({"type": typeof})

		entity = list(self.mongodb.mongoConn.Entities.find(query))

		if not entity:
			self.helpers.logger.info(self.program + " 404: " + \
							self.helpers.confs["errorMessages"][str(404)]["Description"])
			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		elif len(entity) > 1:
			self.helpers.logger.info(self.program + " 409: " + \
							self.helpers.confs["errorMessages"][str(409)]["Description"])
			return self.respond(409, self.helpers.confs["errorMessages"][str(409)],
								None, {}, False, accepted)
		elif _attr not in entity[0]:
			self.helpers.logger.info(self.program + " 404: " + \
				self.helpers.confs["errorMessages"][str(404)]["Description"])
			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		else:
			if is_value:
				data = data.decode()
				path = _attr + '.value'
				if content_type == "text/plain":
					if '"' in data:
						data = str(data.replace('"', ""))
					elif data == "true":
						data = True
					elif data == "false":
						data = False
					elif data == "null":
						data = None
					else:
						if "." in data:
							try:
								data = float(data)
							except:
								return self.respond(400,
													self.helpers.confs["errorMessages"]["400p"],
													None, {}, False, accepted)
						else:
							try:
								data = int(float(data))
							except:
								return self.respond(400,
													self.helpers.confs["errorMessages"]["400p"],
													None, {}, False, accepted)

			else:
				path = _attr

			self.mongodb.mongoConn.Entities.update_one({"id": _id},
										{"$set": {path: data}}, upsert=True)
			return self.respond(204, self.helpers.confs["successMessage"][str(204)],
								None, {}, False, accepted)

	def deleteEntityAttribute(self, _id, _attr, typeof, accepted=[]):
		""" Updates an HIASCDI Entity Attribute.

		References:
			FIWARE-NGSI v2 Specification
			https://fiware.github.io/specifications/ngsiv2/stable/

			Reference
				- Attribute
					- Attribute by Entity ID
						- Update Attribute Data
		"""

		query = {"id": _id}

		if typeof is not None:
			query.update({"type": typeof})

		entity = list(self.mongodb.mongoConn.Entities.find(query))

		if not entity:
			self.helpers.logger.info(self.program + " 404: " +
							self.helpers.confs["errorMessages"][str(404)]["Description"])
			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		elif len(entity) > 1:
			self.helpers.logger.info(self.program + " 409: " +
							self.helpers.confs["errorMessages"][str(409)]["Description"])
			return self.respond(409, self.helpers.confs["errorMessages"][str(409)],
								None, {}, False, accepted)
		elif _attr not in entity[0]:
			self.helpers.logger.info(self.program + " 404: " +
							self.helpers.confs["errorMessages"][str(404)]["Description"])
			return self.respond(404, self.helpers.confs["errorMessages"][str(404)],
								None, {}, False, accepted)
		else:
			self.mongodb.mongoConn.Entities.update({"id": _id},
											{'$unset': {_attr: ""}})
			return self.respond(204, self.helpers.confs["successMessage"][str(204)],
								None, {}, False, accepted)

	def respond(self, responseCode, response, location=None,
				headers={}, override = False, accepted = []):
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
