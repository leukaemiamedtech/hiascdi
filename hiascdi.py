#!/usr/bin/env python3
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

from bson import json_util, ObjectId
from flask import Flask, request, Response
from threading import Thread

from modules.helpers import helpers
from modules.broker import broker
from modules.entities import entities
from modules.mongodb import mongodb
from modules.mqtt import mqtt
from modules.types import types
from modules.subscriptions import subscriptions

class hiascdi():
    """ HIASCDI NGSIV2 Context Broker.

    The HIASCDI Context Broker handles contextual data for all HIAS
    devices/applications and agents. HIASCDI is based on CEF/FIWARE
    NGSI V2 specification.
    """

    def __init__(self):
        """ Initializes the class. """

        self.helpers = helpers("HIASCDI")
        self.confs = self.helpers.confs
        self.credentials = self.helpers.credentials

        self.component = self.credentials["hiascdi"]["name"]
        self.version = self.credentials["hiascdi"]["version"]

        self.ip = self.helpers.get_ip_addr()
        self.port = self.credentials["server"]["port"]

        self.err406 = self.confs["errorMessages"]["406"]

        self.helpers.logger.info(
            self.component + " " + self.version + " initialization complete.")

    def mongodb_connection(self):
        """ Initiates the mongodb connection class. """

        self.mongodb = mongodb(self.helpers)
        self.mongodb.start()

    def hiascdi_connections(self):
        """ Configures the Context Broker. """

        self.broker = broker(self.helpers, self.mongodb)

    def mqtt_connection(self):
        """ Initiates the iotJumpWay connection. """

        self.mqtt = mqtt(self.helpers, "HIASCDI", {
            "host": self.credentials["iotJumpWay"]["host"],
            "port": self.credentials["iotJumpWay"]["port"],
            "location": self.credentials["iotJumpWay"]["location"],
            "zone": self.credentials["iotJumpWay"]["zone"],
            "entity": self.credentials["iotJumpWay"]["entity"],
            "name": self.credentials["iotJumpWay"]["name"],
            "un": self.credentials["iotJumpWay"]["un"],
            "up": self.credentials["iotJumpWay"]["up"]
        })
        self.mqtt.configure()
        self.mqtt.start()

    def configure_entities(self):
        """ Configures the HIASCDI entities. """

        self.entities = entities(self.helpers, self.mongodb, self.broker)

    def configure_types(self):
        """ Configures the HIASCDI entity types. """

        self.types = types(self.helpers, self.mongodb, self.broker)

    def configure_subscriptions(self):
        """ Configures the HIASCDI subscriptions. """

        self.subscriptions = subscriptions(self.helpers, self.mongodb, self.broker)

    def get_broker(self):

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

    def process_headers(self, request):
        """ Processes the request headers """

        accepted = self.broker.check_accepts_type(request.headers)
        content_type = self.broker.check_content_type(request.headers)

        return accepted, content_type

    def check_body(self, body, text=False):
        """ Checks the request body """

        return self.broker.check_body(body, text)

    def respond(self, responseCode, response, accepted):
        """ Builds the request response """

        headers = {}
        if "application/json" in accepted:
            response =  Response(response=response, status=responseCode,
                    mimetype="application/json")
            headers['Content-Type'] = 'application/json'
        elif "text/plain" in accepted:
            response = self.broker.prepareResponse(response)
            response = Response(response=response, status=responseCode,
                    mimetype="text/plain")
            headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers = headers
        return response

    def life(self):
        """ Sends vital statistics to HIAS """

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()[2]
        hdd = psutil.disk_usage('/').percent
        tmp = psutil.sensors_temperatures()['coretemp'][0].current
        r = requests.get('http://ipinfo.io/json?token=' +
                self.credentials["iotJumpWay"]["ipinfo"])
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


hiascdi = hiascdi()
app = Flask(hiascdi.component)

@app.route('/', methods=['GET'])
def about():
    """ Responds to GET requests sent to the /v1/ API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    return hiascdi.respond(
        200, json.dumps(json.loads(json_util.dumps(
            hiascdi.get_broker())), indent=4), accepted)

@app.route('/entities', methods=['POST'])
def entitiesPost():
    """ Responds to POST requests sent to the /v1/entities API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    if query["id"] is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.entities.create_entity(query, accepted)

@app.route('/entities', methods=['GET'])
def entitiesGet():
    """ Responds to GET requests sent to the /v1/entities API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    return hiascdi.entities.get_entities(request.args, accepted)

@app.route('/entities/<_id>', methods=['GET'])
def entityGet(_id):
    """ Responds to GET requests sent to the /v1/entities/<_id> API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

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

    return hiascdi.entities.get_entity(typeof, _id, attrs,
                                      options, metadata,
                                      False, accepted)

@app.route('/entities/<_id>/attrs', methods=['GET'])
def entityAttrsGet(_id):
    """ Responds to GET requests sent to the /v1/entities/<_id>/attrs API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

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

    return hiascdi.entities.get_entity(typeof, _id, attrs,
                                      options, metadata,
                                      True, accepted)

@app.route('/entities/<_id>/attrs', methods=['POST'])
def entityPost(_id):
    """ Responds to POST requests sent to the /v1/entities/<_id>/attrs API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    if request.args.get('options') is None:
        options = None
    else:
        options = request.args.get('options')

    return hiascdi.entities.update_entity_post(_id, typeof, query,
                                             options, accepted)

@app.route('/entities/<_id>/attrs', methods=['PATCH'])
def entityPatch(_id):
    """ Responds to PATCH requests sent to the /v1/entities/<_id>/attrs API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    query = hiascdi.check_body(request)
    print(query)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    if request.args.get('options') is None:
        options = None
    else:
        options = request.args.get('options')

    if request.args.get('type') is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.entities.update_entity_patch(_id, typeof, query,
                                              options, accepted)

@app.route('/entities/<_id>/attrs', methods=['PUT'])
def entityPut(_id):
    """ Responds to PUT requests sent to the /v1/entities/<_id>/attrs API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    if request.args.get('options') is None:
        options = None
    else:
        options = request.args.get('options')

    return hiascdi.entities.update_entity_put(_id, typeof, query,
                                            options, accepted)

@app.route('/entities/<_id>', methods=['DELETE'])
def entityDelete(_id):
    """ Responds to DELETE requests sent to the /v1/entities/<_id> API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.entities.delete_entity(request.args.get('type'),
                                         _id, accepted)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['GET'])
def entityAttrsGetAttr(_id, _attr):
    """ Responds to GET requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if _attr is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

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

    return hiascdi.entities.get_entity_attributes(typeof, _id, _attr,
                                               metadata, False, accepted)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['PUT'])
def entityAttrPut(_id, _attr):
    """ Responds to PUT requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")

    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if _attr is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    return hiascdi.entities.update_entity_attributes_put(_id, _attr, typeof,
                                                query, accepted)

@app.route('/entities/<_id>/attrs/<_attr>', methods=['DELETE'])
def entityAttrDelete(_id,_attr):
    """ Responds to DELETE requests sent to the /v1/entities/<_id>/attrs/<_attr> API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if _attr is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    return hiascdi.entities.delete_entityAttribute(_id, _attr,
                                                  typeof, accepted)

@app.route('/entities/<_id>/attrs/<_attr>/value', methods=['GET'])
def entityAttrsGetAttrValue(_id, _attr):
    """ Responds to GET requests sent to the /v1/entities/<_id>/attrs/<_attr>/value API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if _attr is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    return hiascdi.entities.get_entity_attributes(typeof, _id, _attr,
                                               None, True, accepted)

@app.route('/entities/<_id>/attrs/<_attr>/value', methods=['PUT'])
def entityAttrsPutAttrValue(_id, _attr):
    """ Responds to PUT requests sent to the /v1/entities/<_id>/attrs/<_attr>/value API endpoint. """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)], "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)], "application/json")

    if _id is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"], accepted)

    if _attr is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"], accepted)

    query = hiascdi.check_body(request, True)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"], accepted)

    if request.args.get('type') is None:
        typeof = None
    else:
        typeof = request.args.get('type')

    return hiascdi.entities.update_entity_attributes_put(_id, _attr, typeof, query,
                                                True, accepted, content_type)

@app.route('/types', methods=['GET'])
def typesGet():
    """ Responds to GET /v1/types """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    return hiascdi.types.get_types(request.args,
                                  accepted)

@app.route('/types', methods=['POST'])
def typesPost():
    """ Responds to POST /v1/types """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    return hiascdi.types.create_type(query, accepted)

@app.route('/types/<_type>', methods=['PATCH'])
def typesPatch(_type):
    """ Responds to PATCH /v1/types/<_types> """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    return hiascdi.types.update_type_patch(_type, query, accepted)

@app.route('/types/<_type>', methods=['GET'])
def typeGet(_type):
    """ Responds to GET /v1/types/<_id> """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _type is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.types.get_type(_type,
                                 accepted)

@app.route('/subscriptions', methods=['GET'])
def subscriptionsGet():
    """ Responds to GET /v1/subscriptions """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    return hiascdi.subscriptions.get_subscriptions(request.args,
                                                  accepted)

@app.route('/subscriptions', methods=['POST'])
def subscriptionsPost():
    """ Responds to POST /v1/subscriptions """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    return hiascdi.subscriptions.create_subscription(query,
                                                    accepted)

@app.route('/subscriptions/<_subscription>', methods=['GET'])
def subscriptionGet(_subscription):
    """ Responds to GET /v1/subscriptions/<_subscription> """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _subscription is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.subscriptions.get_subscription(_subscription, accepted)

@app.route('/subscriptions/<_subscription>', methods=['PATCH'])
def subscriptionPatch(_subscription):
    """ Responds to PATCH /v1/subscriptions/<_subscription> """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _subscription is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    query = hiascdi.check_body(request)
    if query is False:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400p"],
            accepted)

    return hiascdi.subscriptions.update_subscription(_subscription,
                                                    query, accepted)

@app.route('/subscriptions/<_subscription>', methods=['DELETE'])
def subscriptionDelete(_subscription):
    """ Responds to DELETE /v1/subscriptions/<_subscription> """

    accepted, content_type = hiascdi.process_headers(request)
    if accepted is False:
        return hiascdi.respond(
            406, hiascdi.confs["errorMessages"][str(406)],
            "application/json")
    if content_type is False:
        return hiascdi.respond(
            415, hiascdi.confs["errorMessages"][str(415)],
            "application/json")

    if _subscription is None:
        return hiascdi.respond(
            400, hiascdi.confs["errorMessages"]["400b"],
            accepted)

    return hiascdi.subscriptions.delete_subscription(
        _subscription, accepted)

def main():
    signal.signal(signal.SIGINT,
                  hiascdi.signal_handler)
    signal.signal(signal.SIGTERM,
                  hiascdi.signal_handler)

    hiascdi.mqtt_connection()
    hiascdi.mongodb_connection()
    hiascdi.hiascdi_connections()
    hiascdi.configure_entities()
    hiascdi.configure_types()
    hiascdi.configure_subscriptions()

    Thread(target=hiascdi.life, args=(),
           daemon=True).start()

    app.run(host=hiascdi.ip, port=hiascdi.port)

if __name__ == "__main__":
    main()
