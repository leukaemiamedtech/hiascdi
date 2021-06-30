# Ubuntu Installation

![HIASCDI](../img/project-banner.jpg)

# Introduction
This installation guide provides a step by step guide that takes you through the installation process for the **HIASCDI**.

&nbsp;

# Prerequisites
For this project you will need to ensure you have the following prerequisites installed and running.

## HIAS Core

**HIASCDI** is a core component of the [HIAS - Hospital Intelligent Automation Server](https://github.com/AIIAL/HIAS-Core). Before beginning this tutorial you should complete the HIAS installation guide and have your HIAS server online. The HIAS Core installation installs the core components of the HIAS server: [HIASBCH](https://github.com/AIIAL/HIASBCH), [HIASHDI](https://github.com/AIIAL/HIASHDI) and [HIASCDI](https://github.com/AIIAL/HIASCDI).

## HIAS IoT Agent

You will need a [HIAS MQTT IoT Agent](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent) installed on your HIAS Network. IoT Agents receive data sent from HIAS Network devices and applications and store the data in HIASCDI and HIASHDI.

## HIASBCH Blockchain Agent

You will need a [HIASBCH MQTT Blockchain Agent](https://github.com/AIIAL/HIASBCH-MQTT-Blockchain-Agent) installed on your HIAS Network. Blockchain Agents receive data from the IoT Agents and store immutable hashes of the data they receive. Please note, there is currently no Blockchain Agent for the AMQP protocol.

&nbsp;

# Operating System
The **HIASCDI** supports the following operating system(s):

- Ubuntu 18.04

&nbsp;

# Installation
You are now ready to install the **HIASCDI** software.

## Clone the repository

Clone the [**HIASCDI**](https://github.com/AIIAL/HIAS-TassAI-Facial-Recognition-Agent " **HIASCDI**") repository from the [Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss](https://github.com/AIIAL "Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss") Github Organization.

To clone the repository and install the project, make sure you have Git installed. Now navigate to your HIAS installation project root and then use the following command.

``` bash
 git clone https://github.com/AIIAL/HIASCDI.git
 mv HIASCDI components/hiascdi/
```

This will clone the **HIASCDI** repository and move the cloned repository to the components directory in the HIAS project (components/hiascdi/).

``` bash
 cd components/
 ls
```

Using the ls command in your HIAS project root directory should show you the following.

```
 hiascdi
```

Navigate to the **HIAS/components/hiascdi/** directory in your HIAS project root, this is your project root directory for this tutorial.

### Developer forks

Developers from the Github community that would like to contribute to the development of this project should first create a fork, and clone that repository. For detailed information please view the [CONTRIBUTING](../../CONTRIBUTING.md "CONTRIBUTING") guide. You should pull the latest code from the development branch.

``` bash
 git clone -b "1.0.0" https://github.com/AIIAL/HIASCDI.git
```

The **-b "1.0.0"** parameter ensures you get the code from the latest master branch. Before using the below command please check our latest master branch in the button at the top of the project README.

# Start The Service
You will now create a service that will run and manage your HIASCDI installation. Making sure you are in the HIAS project root, use the following command:

``` bash
sh components/scripts/service.sh
```

&nbsp;

# API Documentation

Please review the [HIASCDI API Usage Guide](../usage/api.md) for details on how to use the HIASCDI API.

&nbsp;

# Contributing
Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss encourages and welcomes code contributions, bug fixes and enhancements from the Github community.

## Ways to contribute

The following are ways that you can contribute to this project:

- [Bug Report](https://github.com/AIIAL/HIASCDI/issues/new?assignees=&labels=&template=bug_report.md&title=)
- [Feature Request](https://github.com/AIIAL/HIASCDI/issues/new?assignees=&labels=&template=feature_request.md&title=)
- [Feature Proposal](https://github.com/AIIAL/HIASCDI/issues/new?assignees=&labels=&template=feature-proposal.md&title=)
- [Report Vulnerabillity](https://github.com/AIIAL/HIASCDI/issues/new?assignees=&labels=&template=report-a-vulnerability.md&title=)

Please read the [CONTRIBUTING](https://github.com/AIIAL/HIASCDI/blob/main/CONTRIBUTING.md "CONTRIBUTING") document for a contribution guide.

You can also join in with, or create, a discussion in our [Github Discussions](https://github.com/AIIAL/HIASCDI/discussions) area.

## Contributors

All contributors to this project are listed below.

- [Adam Milton-Barker](https://www.leukemiaairesearch.com/association/volunteers/adam-milton-barker "Adam Milton-Barker") - [Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss](https://www.leukemiaresearchassociation.ai "Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss") President/Founder & Lead Developer, Sabadell, Spain

&nbsp;

# Versioning
We use [SemVer](https://semver.org/) for versioning.

&nbsp;

# License
This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/AIIAL/HIASCDI/blob/main/LICENSE "LICENSE") file for details.

&nbsp;

# Bugs/Issues

You use the [repo issues](https://github.com/AIIAL/HIASCDI/issues/new/choose "repo issues") to track bugs and general requests related to using this project. See [CONTRIBUTING](https://github.com/AIIAL/HIASCDI/blob/main/CONTRIBUTING.md "CONTRIBUTING") for more info on how to submit bugs, feature requests and proposals.