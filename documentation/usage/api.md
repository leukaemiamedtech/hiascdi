# Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss
# HIAS - Hospital Intelligent Automation Server
## HIASCDI - HIAS Contextual Data Interface
### HIASCDI API Usage Guide

![HIASCDI - HIAS Contextual Data Interface](../../assets/images/HIASCDI.jpg)

&nbsp;

# Table Of Contents

- [Introduction](#introduction)
- [API Documentation](#api-documentation)
	- [Overview](#overview)
	- [Secure HTTP Requests](#secure-http-requests)
	- [HTTP Responses](#http-responses)
		- [HTTP Success Response](#http-success-response)
		- [HTTP Success Codes](#http-success-codes)
		- [HTTP Error Response](#http-error-response)
		- [HTTP Error Codes](#http-error-codes)
- [Contributing](#contributing)
  - [Contributors](#contributors)
- [Versioning](#versioning)
- [License](#license)
- [Bugs/Issues](#bugs-issues)

&nbsp;

# Introduction

The HIASCDI Console is a REST API client for HIASCDI that is built in to the HIAS UI. The console has been designed to provide the functionalty required to interact with HIASCDI using the methods provided in the [FIWARE-NGSI v2 Specification](https://fiware.github.io/specifications/ngsiv2/stable/).

&nbsp;

# API Documentation

## Overview
The following is the API Documentation for the HIASCDI API. This API is based on the specifications provided in the [FIWARE-NGSI v2 Specification](https://fiware.github.io/specifications/ngsiv2/stable/).

## Secure HTTP Requests

API calls to the HIASCDI API are made using secure HTTP requests. The HIAS server protects the API endpoints with strong SSL encryption, a firewall and Basic AUTH authentication.

The following HTTP request methods are available:

- GET
- POST
- PATCH
- PUT
- DELETE

## HTTP Responses

### HTTP Success Response

- `description` (string): additional information about the response.

### HTTP Success Codes

- `200` `OK` - Request successful
- `201` `Created` - Resource created
- `204` `No Content` - Request succeeded, client doesn't need to navigate away from current page

### HTTP Error Response

The error payload is a JSON response including the following fields:

- `error` (required, string): a textual description of the error.
- `description` (optional, string): additional information about the error.

### HTTP Error Codes

- `400` `ParseError` - Incoming JSON payload cannot be parsed
- `400` `BadRequest` - Error in URL parameters or payload
- `404` `NotFound` - Resource identified by the request is not found
- `405` `MethodNotAlowed` - Requested method not supported
- `406` `NotAcceptable` - Request meme type not supported
- `409` `TooManyResults` - Request may refer to several resources
- `411` `ContentLengthRequired` - Context-Length header is required
- `413` `NoResourceAvailable` - Attemp to exceed spatial index limit results
- `413` `RequestEntityTooLarge` - Request entity too large
- `415` `UnsupportedMediaType` - Request content type not supported
- `501` `NotImplemented` - Request not supported

&nbsp;

# Contributing

The Peter Moss Acute Myeloid & Lymphoblastic Leukemia AI Research project encourages and youlcomes code contributions, bug fixes and enhancements from the Github.

Please read the [CONTRIBUTING](../CONTRIBUTING.md "CONTRIBUTING") document for a full guide to forking our repositories and submitting your pull requests. You will also find information about our code of conduct on this page.

## Contributors

- [Adam Milton-Barker](https://www.leukemiaresearchassociation.ai/team/adam-milton-barker "Adam Milton-Barker") - [Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss](https://www.leukemiaresearchassociation.ai "Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss") President/Founder & Lead Developer, Sabadell, Spain

&nbsp;

# Versioning

You use SemVer for versioning. For the versions available, see [Releases](../releases "Releases").

&nbsp;

# License

This project is licensed under the **MIT License** - see the [LICENSE](../LICENSE "LICENSE") file for details.

&nbsp;

# Bugs/Issues

You use the [repo issues](../issues "repo issues") to track bugs and general requests related to using this project. See [CONTRIBUTING](../CONTRIBUTING.md "CONTRIBUTING") for more info on how to submit bugs, feature requests and proposals.