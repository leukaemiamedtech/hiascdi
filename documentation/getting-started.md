# Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss
# HIAS - Hospital Intelligent Automation Server
## HIASCDI - HIAS Contextual Data Interface
### Getting Started

![HIAS - Hospital Intelligent Automation Server](../assets/images/HIASCDI.jpg)

&nbsp;

# Table Of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
  - [Contributors](#contributors)
- [Versioning](#versioning)
- [License](#license)
- [Bugs/Issues](#bugs-issues)

&nbsp;

# Introduction
This guide will guide you through the installation process for the HIASCDI.

&nbsp;

# Installation
First you need to install the required software. Below are the available installation guides:

- [Ubuntu installation guide](installation/ubuntu.md)

&nbsp;

&nbsp;

# Configuration
[configuration/config.json](../configuration/config.json "configuration/config.json")  holds the configuration for our application.

<details><summary><b>View file contents</b></summary>
<p>
```
{
    "identifier": "",
    "auth": "",
    "program": "HIASCDI",
    "version": "v1",
    "address": "context/v2",
    "host": "",
    "port": 3524,
    "acceptTypes": [
        "application/json",
        "text/plain"
    ],
    "brokerDetails": {
        "entities_url": "/v1/entities",
        "types_url": "/v1/types",
        "subscriptions_url": "/v1/subscriptions",
        "registrations_url": "/v1/registrations"
    },
    "contentType": "application/json",
    "contentTypes": [
        "application/json",
        "text/plain"
    ],
    "endpoints": {
        "entities_url": "/v1/entities",
        "types_url": "/v1/types",
        "subscriptions_url": "/v1/subscriptions",
        "registrations_url": "/v1/registrations"
    },
    "methods": [
        "POST",
        "GET",
        "PUT",
        "PATCH",
        "DELETE"
    ],
    "successMessage": {
        "200": {
            "Description": "OK"
        },
        "204": {
            "Description": "No content"
        }
    },
    "errorMessages": {
        "400": {
            "Error": "Bad Request",
            "Description": "Request not supported!"
        },
        "404": {
            "Error": "Not Found",
            "Description": "Resource not found!"
        },
        "405": {
            "Error": "Method Not Allowed",
            "Description": "Requested method not supported!"
        },
        "406": {
            "Error": "Not Acceptable",
            "Description": "Accepted content type not supported!"
        },
        "409": {
            "Error": "Conflict",
            "Description": "The request could not be completed due to a conflict with the current state of the resource."
        },
        "415": {
            "Error": "Unsupported Media Type",
            "Description": "Request content type not supported!"
        },
        "501": {
            "Error": "Not Implemented",
            "Description": "Request not supported!"
        }
    }
}
```
</p>
</details><br />

&nbsp;

# Testing

<details><summary><b>View output</b></summary>
<p>
```
```
</p>
</details><br />
```

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