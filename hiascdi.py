#!/usr/bin/env python
""" HIASCDI NGSIV2 Context Broker.

The HIASCDI Context Broker handles contextual data for all HIAS
devices/applications and agents. HIASCDI is based on CEF/FIWARE
NGSI V2 specification.

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
import psutil
import requests
import os
import signal
import sys
import threading
import urllib

sys.path.append('../..')

from bson import json_util, ObjectId
from flask import Flask, request, Response
from threading import Thread

from modules.mongodb import mongodb
from modules.mqtt import mqtt

from components.hiascdi.modules.helpers import helpers
from components.hiascdi.modules.broker import broker
from components.hiascdi.modules.entities import entities

class HIASCDI():
	""" HIASCDI NGSIV2 Context Broker.

	The HIASCDI Context Broker handles contextual data for all HIAS
	devices/applications and agents. HIASCDI is based on CEF/FIWARE
	NGSI V2 specification.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.helpers = helpers("HIASCDI")
		self.confs = self.helpers.confs

		self.component = self.confs["program"]
		self.version = self.confs["version"]

		self.err406 = self.confs["errorMessages"]["406"]

		self.helpers.logger.info(
			self.component + " " + self.version + " initialization complete.")

	def mongoDbConnection(self):
		""" Initiates the mongodb connection class. """

		self.mongodb = mongodb(self.helpers, True)
		self.mongodb.start()

	def hiascdiConnection(self):
		""" Configures the Context Broker. """

		self.broker = broker(self.helpers, self.mongodb)

	def iotConnection(self):
		""" Initiates the iotJumpWay connection. """

		self.mqtt = mqtt(self.helpers, "HIASCDI", {
			"host": self.helpers.credentials["iotJumpWay"]["host"],
			"port": self.helpers.credentials["iotJumpWay"]["mqtt"]["port"],
			"location": self.helpers.credentials["iotJumpWay"]["location"],
			"zone": self.helpers.credentials["iotJumpWay"]["zone"],
			"entity": self.helpers.credentials["iotJumpWay"]["mqtt"]["entity"],
			"name": self.helpers.credentials["iotJumpWay"]["mqtt"]["name"],
			"un": self.helpers.credentials["iotJumpWay"]["mqtt"]["un"],
			"up": self.helpers.credentials["iotJumpWay"]["mqtt"]["up"]
		})
		self.mqtt.configure()
		self.mqtt.start()

	def configureEntities(self):
		""" Configures the Context Broker. """

		self.entities = entities(self.helpers, self.mongodb, self.broker)

	def getBroker(self):

		return {
				"entities_url": self.confs["endpoints"]["entities_url"],
				"types_url": self.confs["endpoints"]["types_url"],
				"subscriptions_url": self.confs["endpoints"]["subscriptions_url"],
				"registrations_url": self.confs["endpoints"]["registrations_url"],
				"CPU": psutil.cpu_percent(),
				"Memory": psutil.virtual_memory()[2],
				"Diskspace": psutil.disk_usage('/').percent,
				"Temperature": psutil.sensors_temperatures()['coretemp'][0].current
			}

	def processHeaders(self, request):

		if self.broker.checkAcceptsType(request.headers):
			return self.respond(406, self.confs["errorMessages"][str(406)])

		if self.broker.checkContentType(request.headers) is not True:
			return self.respond(415, self.confs["errorMessages"][str(415)])

	def checkBody(self, body):

		return self.broker.checkJSON(body)

	def respond(self, responseCode, response):
		""" Builds the request repsonse """

		headers = {}

		if "application/json" in self.broker.accepted:
			response =  Response(response=response, status=responseCode,
							mimetype="application/json")
			headers['Content-Type'] = 'application/json'
		elif "text/plain" in self.broker.accepted:
			if isinstance(response, dict):
				response = json.dumps(response)
			if isinstance(response, list):
				response = json.dumps(response)
			response = Response(response=response, status=responseCode,
						mimetype="text/plain")
			headers['Content-Type'] = 'text/plain; charset=utf-8'

		if len(headers):
			response.headers = headers

		return response

	def life(self):
		""" Sends vital statistics to HIAS """

		cpu = psutil.cpu_percent()
		mem = psutil.virtual_memory()[2]
		hdd = psutil.disk_usage('/').percent
		tmp = psutil.sensors_temperatures()['coretemp'][0].current
		r = requests.get('http://ipinfo.io/json?token=' +
					self.helpers.credentials["iotJumpWay"]["ipinfo"])
		data = r.json()
		location = data["loc"].split(',')

		# Send iotJumpWay notification
		self.mqtt.publish("Life", {
			"CPU": str(cpu),
			"Memory": str(mem),
			"Diskspace": str(hdd),
			"Temperature": str(tmp),
			"Latitude": float(location[0]),
			"Longitude": float(location[1])
		})

		self.helpers.logger.info("HIASCDI life statistics published.")
		threading.Timer(300.0, self.life).start()

	def signal_handler(self, signal, frame):
		self.helpers.logger.info("Disconnecting")
		sys.exit(1)


HIASCDI = HIASCDI()
app = Flask(HIASCDI.component)

@app.route('/', methods=['GET'])
def about():
	""" Responds to GET requests sent to the /v1/ API endpoint. """

	HIASCDI.processHeaders(request)

	return HIASCDI.respond(200, HIASCDI.getBroker())

@app.route('/entities', methods=['POST'])
def entitiesPost():
	""" Responds to POST requests sent to the /v1/entities API endpoint. """

	HIASCDI.processHeaders(request)
	print(self.broker.accepted)

	query=request.json

	if query is None or not HIASCDI.checkBody(query):
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400p"])

	if query["id"] is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	return HIASCDI.entities.createEntity(query)

@app.route('/entities', methods=['GET'])
def entitiesGet():
	""" Responds to GET requests sent to the /v1/entities API endpoint. """

	HIASCDI.processHeaders(request)

	return HIASCDI.entities.getEntities(request.args)

@app.route('/entities/<_id>', methods=['GET'])
def entityGet(_id):
	""" Responds to GET requests sent to the /v1/entities/<_id> API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('attrs') is None:
		attrs = None
	else:
		attrs = request.args.get('attrs')

	if request.args.get('options') is None:
		options = None
	else:
		options = request.args.get('options')

	if request.args.get('metadata') is None:
		metadata = None
	else:
		metadata = request.args.get('metadata')

	return HIASCDI.entities.getEntity(typeof, _id, attrs, options, metadata)

@app.route('/entities/<_id>/attrs', methods=['GET'])
def entityAttrsGet(_id):
	""" Responds to GET requests sent to the /v1/entities/<_id>/attrs API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('attrs') is None:
		attrs = None
	else:
		attrs = request.args.get('attrs')

	if request.args.get('options') is None:
		options = None
	else:
		options = request.args.get('options')

	if request.args.get('metadata') is None:
		metadata = None
	else:
		metadata = request.args.get('metadata')

	return HIASCDI.entities.getEntity(typeof, _id, attrs, options, metadata, True)

@app.route('/entities/<_id>/attrs', methods=['POST'])
def entityPost(_id):
	""" Responds to POST requests sent to the /v1/entities/<_id>/attrs API endpoint. """

	HIASCDI.processHeaders(request)

	query = request.json

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if query is None or not HIASCDI.checkBody(query):
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400p"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('options') is None:
		options = None
	else:
		options = request.args.get('options')

	return HIASCDI.entities.updateEntityPost(_id, typeof, query, options)

@app.route('/entities/<_id>/attrs', methods=['PATCH'])
def entityPatch(_id):
	""" Responds to PATCH requests sent to the /v1/entities/<_id>/attrs API endpoint. """

	HIASCDI.processHeaders(request)

	query = request.json

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if query is None or not HIASCDI.checkBody(query):
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400p"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('options') is None:
		options = None
	else:
		options = request.args.get('options')

	if request.args.get('type') is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	return HIASCDI.entities.updateEntityPatch(_id, typeof, query, options)

@app.route('/entities/<_id>/attrs', methods=['PUT'])
def entityPut(_id):
	""" Responds to PUT requests sent to the /v1/entities/<_id>/attrs API endpoint. """

	HIASCDI.processHeaders(request)

	query = request.json

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if query is None or not HIASCDI.checkBody(query):
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400p"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('options') is None:
		options = None
	else:
		options = request.args.get('options')

	return HIASCDI.entities.updateEntityPut(_id, typeof, query, options)

@app.route('/entities/<_id>', methods=['DELETE'])
def entityDelete(_id):
	""" Responds to DELETE requests sent to the /v1/entities/<_id> API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	return HIASCDI.entities.deleteEntity(request.args.get('type'), _id)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['GET'])
def entityAttrsGetAttr(_id, _attr):
	""" Responds to GET requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if _attr is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	if request.args.get('attrs') is None:
		attrs = None
	else:
		attrs = request.args.get('attrs')

	if request.args.get('metadata') is None:
		metadata = None
	else:
		metadata = request.args.get('metadata')

	return HIASCDI.entities.getEntityAttribute(typeof, _id, _attr, metadata)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['PUT'])
def entityAttrPut(_id, _attr):
	""" Responds to PUT requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

	HIASCDI.processHeaders(request)

	query = request.json

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if _attr is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if query is None or not HIASCDI.checkBody(query):
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400p"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	return HIASCDI.entities.updateEntityAttrPut(_id, _attr, typeof, query)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['DELETE'])
def entityAttrDelete(_id,_attr):
	""" Responds to DELETE requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if _attr is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	return HIASCDI.entities.deleteEntityAttribute(_id, _attr, typeof)

@app.route('/entities/<_id>/attrs/<_attr>/value', methods=['GET'])
def entityAttrsGetAttrValue(_id, _attr):
	""" Responds to GET requests sent to the /v1/entities/<_id>/attrs/<_attr>/value API endpoint. """

	HIASCDI.processHeaders(request)

	if _id is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if _attr is None:
		return HIASCDI.respond(400, HIASCDI.helpers.confs["errorMessages"]["400b"])

	if request.args.get('type') is None:
		typeof = None
	else:
		typeof = request.args.get('type')

	return HIASCDI.entities.getEntityAttribute(typeof, _id, _attr, None, True)

def main():
	signal.signal(signal.SIGINT, HIASCDI.signal_handler)
	signal.signal(signal.SIGTERM, HIASCDI.signal_handler)

	HIASCDI.iotConnection()
	HIASCDI.mongoDbConnection()
	HIASCDI.hiascdiConnection()
	HIASCDI.configureEntities()

	Thread(target=HIASCDI.life, args=(), daemon=True).start()

	app.run(host=HIASCDI.helpers.confs["host"],
			port=HIASCDI.helpers.confs["port"])

if __name__ == "__main__":
	main()
