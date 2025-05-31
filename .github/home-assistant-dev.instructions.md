---
applyTo: '**'
---
# Home Assistant Developer Instructions
Home Assistant Core
The core of Home Assistant is built from the ground up to be easily extensible using integrations. In this section, we're focusing on how to develop integrations.

Before you start, make sure that you have read up on the overall Home Assistant architecture so that you are familiar with the concepts that make up Home Assistant.

If you run into trouble following this documentation, don't hesitate to join our #devs_core channel on Discord.

# https://developers.home-assistant.io/docs/architecture_components
Integration architecture
Home Assistant Core can be extended with integrations. Each integration is responsible for a specific domain within Home Assistant. Integrations can listen for or trigger events, offer actions, and maintain states. Integrations are made up of a component (the base logic) and platforms (bits that integrate with other integrations). Integrations are written in Python and can do all the goodness that Python has to offer. Out of the box, Home Assistant offers a bunch of built-in integrations.

Diagram showing interaction between integrations and the Home Assistant core.
Home Assistant distinguishes the following integration types:

Define an Internet of Things domain
These integrations define a specific device category of Internet of Things devices in Home Assistant, like a light. It's up to the light integration to define what data is available in Home Assistant and in what format. It also provides actions to control lights.

For a list of defined domains, see entities.

To suggest a new domain, start a discussion in the architecture repository. Make sure to show what data your proposed entity would include and how it can be controlled. Include examples from multiple brands.

Interact with external devices & services
These integrations interact with external devices & services and make them available in Home Assistant via integrations that define IoT domains like light. An example of such an integration is Philips Hue. Philips Hue lights are made available as light entities in Home Assistant.

Integrations which interact with external devices & services are generally not allowed to consume the state of entities from other integrations, with the exception of entities from other integrations which have a location, e.g. the state of zone and device_tracker entities.

For more information, see entity architecture.

Represent virtual/computed data points
These integrations represent entities either based on virtual data, like the input_boolean integration, a virtual switch. Or they derive their data based on other data available in Home Assistant, like the template integration or utility_meter integration.

Actions that can be triggered by the user or respond to events
These integrations provide small pieces of home automation logic that do common tasks within your house. The most popular one is the automation integration, allowing users to create automations through a configuration format.

It can also be more specific, like the flux integration, which controls lights based on the sun setting.

Creating your first integration
Alright, so it's time to write your first code for your integration. AWESOME. Don't worry, we've tried hard to keep it as easy as possible. From a Home Assistant development environment, type the following and follow the instructions:

python3 -m script.scaffold integration

This will set you up with everything that you need to build an integration that is able to be set up via the user interface. More extensive examples of integrations are available from our example repository.

tip
This example repository shows custom integrations that live in the <config_dir>/custom_components directory. These MUST have a version key in their manifest file. Core integrations live in the homeassistant/components directory, and do not need a version key. The architecture is the same in both cases.

The minimum
The scaffold integration contains a bit more than just the bare minimum. The minimum is that you define a DOMAIN constant that contains the domain of the integration. The second part is that it needs to define a setup method that returns a boolean if the set-up was successful.

Create a file homeassistant/components/hello_state/__init__.py with one of the two following codeblocks, depending on what you need:

Sync component:
DOMAIN = "hello_state"


def setup(hass, config):
    hass.states.set("hello_state.world", "Paulus")

    # Return boolean to indicate that initialization was successful.
    return True

And if you prefer an async component:
DOMAIN = "hello_state"


async def async_setup(hass, config):
    hass.states.async_set("hello_state.world", "Paulus")

    # Return boolean to indicate that initialization was successful.
    return True

In addition, a manifest file is required with the following keys as the bare minimum. Create homeassistant/components/hello_state/manifest.json.

{
  "domain": "hello_state",
  "name": "Hello, state!"
}

To load this, add hello_state: to your configuration.yaml file.

What the scaffold offers
When using the scaffold script, it will go past the bare minimum of an integration. It will include a config flow, tests for the config flow and basic translation infrastructure to provide internationalization for your config flow.

Integration file structure
Each integration is stored inside a directory named after the integration domain. The domain is a short name consisting of characters and underscores. This domain has to be unique and cannot be changed. Example of the domain for the mobile app integration: mobile_app. So all files for this integration are in the folder mobile_app/.

The bare minimum content of this folder looks like this:

manifest.json: The manifest file describes the integration and its dependencies. More info
__init__.py: The component file. If the integration only offers a platform, you can keep this file limited to a docstring introducing the integration """The Mobile App integration.""".
Integrating devices - light.py, switch.py etc
If your integration is going to integrate one or more devices, you will need to do this by creating a platform that interacts with an entity integration. For example, if you want to represent a light device inside Home Assistant, you will create light.py, which will contain a light platform for the light integration.

More info on available entity integrations.
More info on creating platforms.
Integrating service actions - services.yaml
If your integration is going to register service actions, it will need to provide a description of the available actions. The description is stored in services.yaml. More information about services.yaml.

Data update coordinator - coordinator.py
There are multiple ways for your integration to receive data, including push or poll. Commonly integrations will fetch data with a single coordinated poll across all entities, which requires the use of a DataUpdateCoordinator. If you want to use one, and you choose to create a subclass of it, it is recommended to define the coordinator class in coordinator.py. More information about DataUpdateCoordinator.

Where Home Assistant looks for integrations
Home Assistant will look for an integration when it sees the domain referenced in the config file (i.e. mobile_app:) or if it is a dependency of another integration. Home Assistant will look at the following locations:

<config directory>/custom_components/<domain>
homeassistant/components/<domain> (built-in integrations)
You can override a built-in integration by having an integration with the same domain in your <config directory>/custom_components folder. The manifest.json file requires a version tag when you override a core integration. An overridden core integration can be identified by a specific icon in the upper right corner of the integration box in the overview Open your Home Assistant instance and show your integrations. Note that overriding built-in integrations is not recommended as you will no longer get updates. It is recommended to pick a unique name.


Integration tests file structure
Tests for each integration are stored inside a directory named after the integration domain. For example, tests for the mobile app integration should be stored in tests/components/mobile_app.

The content of this folder looks like this:

__init__.py: Required for pytest to find the tests, you can keep this file limited to a docstring introducing the integration tests """Tests for the Mobile App integration.""".
conftest.py: Pytest test fixtures
test_xxx.py: Tests testing a corresponding part of the integration. Tests of functionality in __init__.py, for example setting up, reloading and unloading a config entry, should be in a file named test_init.py.
Sharing test fixtures with other integrations
If your integration is an entity integration which other integrations have platforms with, for example light or sensor, the integration can provide test fixtures which can be used when writing tests for other integrations.

For example, the light integration may provide fixtures for creating mocked light entities by adding fixture stubs to tests/components/conftest.py, and the actual implementation of the fixtures in tests/components/light/common.py.

Integration manifest
Every integration has a manifest file to specify its basic information. This file is stored as manifest.json in your integration directory. It is required to add such a file.

{
  "domain": "hue",
  "name": "Philips Hue",
  "after_dependencies": ["http"],
  "codeowners": ["@balloob"],
  "dependencies": ["mqtt"],
  "documentation": "https://www.home-assistant.io/components/hue",
  "integration_type": "hub",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/balloob/hue/issues",
  "loggers": ["aiohue"],
  "requirements": ["aiohue==1.9.1"],
  "quality_scale": "platinum"
}

Or a minimal example that you can copy into your project:

{
  "domain": "your_domain_name",
  "name": "Your Integration",
  "codeowners": [],
  "dependencies": [],
  "documentation": "https://www.example.com",
  "integration_type": "hub",
  "iot_class": "cloud_polling",
  "requirements": []
}

Domain
The domain is a short name consisting of characters and underscores. This domain has to be unique and cannot be changed. Example of the domain for the mobile app integration: mobile_app. The domain key has to match the directory this file is in.

Name
The name of the integration.

Version
For core integrations, this should be omitted.

The version of the integration is required for custom integrations. The version needs to be a valid version recognized by AwesomeVersion like CalVer or SemVer.

Integration type
Integrations are split into multiple integration types. Each integration must provide an integration_type in their manifest, that describes its main focus.

warning
When not set, we currently default to hub. This default is temporary during our transition period, every integration should set an integration_type and it thus will become mandatory in the future.

Type	Description
device	Provides a single device like, for example, ESPHome.
entity	Provides a basic entity platform, like sensor or light. This should generally not be used.
hardware	Provides a hardware integration, like Raspbery Pi or Hardkernel. This should generally not be used.
helper	Provides an entity to help the user with automations like input boolean, derivative or group.
hub	Provides a hub integration, with multiple devices or services, like Philips Hue.
service	Provides a single service, like DuckDNS or AdGuard.
system	Provides a system integration and is reserved, should generally not be used.
virtual	Not an integration on its own. Instead it points towards another integration or IoT standard. See virtual integration section.
info
The difference between a hub and a service or device is defined by the nature of the integration. A hub provides a gateway to multiple other devices or services. service and device are integrations that provide a single device or service per config entry.

Documentation
The website containing documentation on how to use your integration. If this integration is being submitted for inclusion in Home Assistant, it should be https://www.home-assistant.io/integrations/<domain>

Issue tracker
The issue tracker of your integration, where users reports issues if they run into one. If this integration is being submitted for inclusion in Home Assistant, it should be omitted. For built-in integrations, Home Assistant will automatically generate the correct link.

Dependencies
Dependencies are other Home Assistant integrations you want Home Assistant to set up successfully before the integration is loaded. Adding an integration to dependencies will ensure the depending integration is loaded before setup, but it does not guarantee all dependency configuration entries have been set up. Adding dependencies can be necessary if you want to offer functionality from that other integration, like webhooks or an MQTT connection. Adding an after dependency might be a better alternative if a dependency is optional but not critical. See the MQTT section for more details on handling this for MQTT.

Built-in integrations shall only specify other built-in integrations in dependencies. Custom integrations may specify both built-in and custom integrations in dependencies.

After dependencies
This option is used to specify dependencies that might be used by the integration but aren't essential. When after_dependencies is present, set up of an integration will wait for the integrations listed in after_dependencies, which are configured either via YAML or a config entry, to be set up first before the integration is set up. It will also make sure that the requirements of after_dependencies are installed so methods from the integration can be safely imported, regardless of whether the integrations listed in after_dependencies are configured or not. For example, if the camera integration might use the stream integration in certain configurations, adding stream to after_dependencies of camera's manifest, will ensure that stream is loaded before camera if it is configured and that any dependencies of stream are installed and can be imported by camera. If stream is not configured, camera will still load.

Built-in integrations shall only specify other built-in integrations in after_dependencies. Custom integrations may specify both built-in and custom integrations in after_dependencies.

Code owners
GitHub usernames or team names of people that are responsible for this integration. You should add at least your GitHub username here, as well as anyone who helped you to write code that is being included.

Config flow
Specify the config_flow key if your integration has a config flow to create a config entry. When specified, the file config_flow.py needs to exist in your integration.

{
  "config_flow": true
}

Single config entry only
Specify the single_config_entry key if your integration supports only one config entry. When specified, it will not allow the user to add more than one config entry for this integration.

{
  "single_config_entry": true
}

Requirements
Requirements are Python libraries or modules that you would normally install using pip for your component. Home Assistant will try to install the requirements into the deps subdirectory of the Home Assistant configuration directory if you are not using a venv or in something like path/to/venv/lib/python3.6/site-packages if you are running in a virtual environment. This will make sure that all requirements are present at startup. If steps fail, like missing packages for the compilation of a module or other install errors, the component will fail to load.

Requirements is an array of strings. Each entry is a pip compatible string. For example, the media player Cast platform depends on the Python package PyChromecast v3.2.0: ["pychromecast==3.2.0"].

Custom requirements during development & testing
During the development of a component, it can be useful to test against different versions of a requirement. This can be done in two steps, using pychromecast as an example:

pip install pychromecast==3.2.0 --target ~/.homeassistant/deps
hass --skip-pip-packages pychromecast

This will use the specified version, and prevent Home Assistant from trying to override it with what is specified in requirements. To prevent any package from being automatically overridden without specifying dependencies, you can launch Home Assistant with the global --skip-pip flag.

If you need to make changes to a requirement to support your component, it's also possible to install a development version of the requirement using pip install -e:

git clone https://github.com/balloob/pychromecast.git
pip install -e ./pychromecast
hass --skip-pip-packages pychromecast

It is also possible to use a public git repository to install a requirement. This can be useful, for example, to test changes to a requirement dependency before it's been published to PyPI. Syntax:

{
  "requirements": ["<library>@git+https://github.com/<user>/<project>.git@<git ref>"]
}


<git ref> can be any git reference: branch, tag, commit hash, ... . See PIP documentation about git support.

The following example will install the except_connect branch of the pycoolmaster library directly from GitHub:

{
  "requirements": ["pycoolmaster@git+https://github.com/issacg/pycoolmaster.git@except_connect"]
}


Custom integration requirements
Custom integrations should only include requirements that are not required by the Core requirements.txt.

Loggers
The loggers field is a list of names that the integration's requirements use for their getLogger calls.

Bluetooth
If your integration supports discovery via bluetooth, you can add a matcher to your manifest. If the user has the bluetooth integration loaded, it will load the bluetooth step of your integration's config flow when it is discovered. We support listening for Bluetooth discovery by matching on connectable local_name, service_uuid, service_data_uuid, manufacturer_id, and manufacturer_data_start. The manufacturer_data_start field expects a list of bytes encoded as integer values from 0-255. The manifest value is a list of matcher dictionaries. Your integration is discovered if all items of any of the specified matchers are found in the Bluetooth data. It's up to your config flow to filter out duplicates.

Matches for local_name may not contain any patterns in the first three (3) characters.

If the device only needs advertisement data, setting connectable to false will opt-in to receive discovery from Bluetooth controllers that do not have support for making connections.

The following example will match Nespresso Prodigio machines:

{
  "bluetooth": [
    {
      "local_name": "Prodigio_*"
    }
  ]
}

The following example will match service data with a 128 bit uuid used for SwitchBot bot and curtain devices:

{
  "bluetooth": [
    {
      "service_uuid": "cba20d00-224d-11e6-9fb8-0002a5d5c51b"
    }
  ]
}

If you want to match service data with a 16 bit uuid, you will have to convert it to a 128 bit uuid first, by replacing the 3rd and 4th byte in 00000000-0000-1000-8000-00805f9b34fb with the 16 bit uuid. For example, for Switchbot sensor devices, the 16 bit uuid is 0xfd3d, the corresponding 128 bit uuid becomes 0000fd3d-0000-1000-8000-00805f9b34fb. The following example will therefore match service data with a 16 bit uuid used for SwitchBot sensor devices:

{
  "bluetooth": [
    {
      "service_data_uuid": "0000fd3d-0000-1000-8000-00805f9b34fb"
    }
  ]
}

The following example will match HomeKit devices:

{
  "bluetooth": [
    {
      "manufacturer_id": 76,
      "manufacturer_data_start": [6]
    }
  ]
}

Zeroconf
If your integration supports discovery via Zeroconf, you can add the type to your manifest. If the user has the zeroconf integration loaded, it will load the zeroconf step of your integration's config flow when it is discovered.

Zeroconf is a list so you can specify multiple types to match on.

{
  "zeroconf": ["_googlecast._tcp.local."]
}

Certain zeroconf types are very generic (i.e., _printer._tcp.local., _axis-video._tcp.local. or _http._tcp.local). In such cases you should include a Name (name), or Properties (properties) filter:

{
  "zeroconf": [
    {"type":"_axis-video._tcp.local.","properties":{"macaddress":"00408c*"}},
    {"type":"_axis-video._tcp.local.","name":"example*"},
    {"type":"_airplay._tcp.local.","properties":{"am":"audioaccessory*"}},
   ]
}


Note that all values in the properties filters must be lowercase, and may contain a fnmatch type wildcard.

SSDP
If your integration supports discovery via SSDP, you can add the type to your manifest. If the user has the ssdp integration loaded, it will load the ssdp step of your integration's config flow when it is discovered. We support SSDP discovery by the SSDP ST, USN, EXT, and Server headers (header names in lowercase), as well as data in UPnP device description. The manifest value is a list of matcher dictionaries, your integration is discovered if all items of any of the specified matchers are found in the SSDP/UPnP data. It's up to your config flow to filter out duplicates.

The following example has one matcher consisting of three items, all of which must match for discovery to happen by this config.

{
  "ssdp": [
    {
      "st": "roku:ecp",
      "manufacturer": "Roku",
      "deviceType": "urn:roku-com:device:player:1-0"
    }
  ]
}

HomeKit
If your integration supports discovery via HomeKit, you can add the supported model names to your manifest. If the user has the zeroconf integration loaded, it will load the homekit step of your integration's config flow when it is discovered.

HomeKit discovery works by testing if the discovered modelname starts with any of the model names specified in the manifest.json.

{
  "homekit": {
    "models": [
      "LIFX"
    ]
  }
}

Discovery via HomeKit does not mean that you have to talk the HomeKit protocol to communicate with your device. You can communicate with the device however you see fit.

When a discovery info is routed to your integration because of this entry in your manifest, the discovery info is no longer routed to integrations that listen to the HomeKit zeroconf type.

MQTT
If your integration supports discovery via MQTT, you can add the topics used for discovery. If the user has the mqtt integration loaded, it will load the mqtt step of your integration's config flow when it is discovered.

MQTT discovery works by subscribing to MQTT topics specified in the manifest.json.

{
  "mqtt": [
    "tasmota/discovery/#"
  ]
}

If your integration requires mqtt, make sure it is added to the dependencies.

Integrations depending on MQTT should wait using await mqtt.async_wait_for_mqtt_client(hass) for the MQTT client to become available before they can subscribe. The async_wait_for_mqtt_client method will block and return True till the MQTT client is available.

DHCP
If your integration supports discovery via DHCP, you can add the type to your manifest. If the user has the dhcp integration loaded, it will load the dhcp step of your integration's config flow when it is discovered. We support passively listening for DHCP discovery by the hostname and OUI, or matching device registry mac address when registered_devices is set to true. The manifest value is a list of matcher dictionaries, your integration is discovered if all items of any of the specified matchers are found in the DHCP data. Unix filename pattern matching is used for matching. It's up to your config flow to filter out duplicates.

If an integration wants to receive discovery flows to update the IP Address of a device when it comes online, but a hostname or oui match would be too broad, and it has registered in the device registry with mac address using the CONNECTION_NETWORK_MAC, it should add a DHCP entry with registered_devices set to true.

If the integration supports zeroconf or ssdp, these should be preferred over dhcp as it generally offers a better user experience.

The following example has two matchers consisting of two items. All of the items in any of the matchers must match for discovery to happen by this config.

For example:

If the hostname was Rachio-XYZ and the macaddress was 00:9D:6B:55:12:AA, the discovery would happen (1st matcher).
If the hostname was Dachio-XYZ or Pachio-XYZ, and the macaddress was 00:9D:6B:55:12:AA, the discovery would happen (3rd matcher).
If the hostname was Rachio-XYZ and the macaddress was 00:00:00:55:12:AA, the discovery would not happen (no matching MAC).
If the hostname was NotRachio-XYZ and the macaddress was 00:9D:6B:55:12:AA, the discovery would not happen (no matching hostname).
{
  "dhcp": [
    {
    "hostname": "rachio-*",
    "macaddress": "009D6B*"
    },
    {
    "hostname": "[dp]achio-*",
    "macaddress": "009D6B*"
    }
  ]
}

Example with setting registered_devices to true:

{
  "dhcp": [
    {
    "hostname": "myintegration-*",
    },
    {
    "registered_devices": true,
    }
  ]
}

USB
If your integration supports discovery via usb, you can add the type to your manifest. If the user has the usb integration loaded, it will load the usb step of your integration's config flow when it is discovered. We support discovery by VID (Vendor ID), PID (Device ID), Serial Number, Manufacturer, and Description by extracting these values from the USB descriptor. For help identifiying these values see How To Identify A Device. The manifest value is a list of matcher dictionaries. Your integration is discovered if all items of any of the specified matchers are found in the USB data. It's up to your config flow to filter out duplicates.

warning
Some VID and PID combinations are used by many unrelated devices. For example VID 10C4 and PID EA60 matches any Silicon Labs CP2102 USB-Serial bridge chip. When matching these type of devices, it is important to match on description or another identifer to avoid an unexpected discovery.

The following example has two matchers consisting of two items. All of the items in any of the two matchers must match for discovery to happen by this config.

For example:

If the vid was AAAA and the pid was AAAA, the discovery would happen.
If the vid was AAAA and the pid was FFFF, the discovery would not happen.
If the vid was CCCC and the pid was AAAA, the discovery would not happen.
If the vid was 1234, the pid was ABCD, the serial_number was 12345678, the manufacturer was Midway USB, and the description was Version 12 Zigbee Stick, the discovery would happen.
{
  "usb": [
    {
    "vid": "AAAA",
    "pid": "AAAA"
    },
    {
    "vid": "BBBB",
    "pid": "BBBB"
    },
    {
    "vid": "1234",
    "pid": "ABCD",
    "serial_number": "1234*",
    "manufacturer": "*midway*",
    "description": "*zigbee*"
    },
  ]
}

Integration quality scale
The Integration Quality Scale scores an integration on the code quality and user experience. Each level of the quality scale consists of a list of requirements. If an integration matches all requirements, it's considered to have reached that level.

New integrations are required to fulfill at least the bronze tier so be sure to look at the Integration Quality Scale list of requirements. It helps to improve the code and user experience tremendously.

{
 "quality_scale": "silver"
}

IoT class
The IoT class describes how an integration connects with, e.g., a device or service. For more information about IoT Classes, read the blog about "Classifying the Internet of Things".

The following IoT classes are accepted in the manifest:

assumed_state: We are unable to get the state of the device. Best we can do is to assume the state based on our last command.
cloud_polling: The integration of this device happens via the cloud and requires an active internet connection. Polling the state means that an update might be noticed later.
cloud_push: Integration of this device happens via the cloud and requires an active internet connection. Home Assistant will be notified as soon as a new state is available.
local_polling: Offers direct communication with device. Polling the state means that an update might be noticed later.
local_push: Offers direct communication with device. Home Assistant will be notified as soon as a new state is available.
calculated: The integration does not handle communication on its own, but provides a calculated result.
Virtual integration
Some products are supported by integrations that are not named after the product. For example, Yale Home locks are integrated via the August integration, and the IKEA SYMFONISK product line can be used with the Sonos integration.

There are also cases where a product line only supports a standard IoT standards like Zigbee or Z-Wave. For example, the U-tec ultraloq works via Z-Wave and has no specific dedicated integration.

For end-users, it can be confusing to find how to integrate those products with Home Asssistant. To help with these above cases, Home Assistant has "Virtual integrations". These integrations are not real integrations but are used to help users find the right integration for their device.

A virtual integration is an integration that just has a single manifest file, without any additional code. There are two types of virtual integrations: A virtual integration supported by another integration and one that uses an existing IoT standard.

info
Virtual integrations can only be provided by Home Assistant Core and not by custom integrations.

Supported by
The "Supported by" virtual integration is an integration that points to another integration to provide its implementation. For example, Yale Home locks are integrated via the August (august) integration.

Example manifest:

{
  "domain": "yale_home",
  "name": "Yale Home",
  "integration_type": "virtual",
  "supported_by": "august"
}

The domain and name are the same as with any other integration, but the integration_type is set to virtual. The logo for the domain of this virtual integration must be added to our brands repository, so in this case, a Yale Home branding is used.

The supported_by is the domain of the integration providing the implementation for this product. In the example above, the Yale Home lock is supported by the August integration and points to its domain august.

Result:

Yale Home is listed on our user documentation website under integrations with an automatically generated stub page that directs the user to the integration to use.
Yale Home is listed in Home Assistant when clicking "add integration". When selected, we explain to the user that this product is integrated using a different integration, then the user continues to the Xioami Miio config flow.
IoT standards
The "IoT Standards" virtual integration is an integration that uses an existing IoT standard to provide connectivity with the device. For example, the U-tec ultraloq works via Z-Wave and has no specific dedicated integration.

Example manifest:

{
  "domain": "ultraloq",
  "name": "ultraloq",
  "integration_type": "virtual",
  "iot_standards": ["zwave"],
}


The domain and name are the same as with any other integration, but the integration_type is set to virtual. The logo for the domain of this virtual integration should be added to our brands repository.

The iot_standards is the standard this product uses for connectivity. In the example above, the U-tech ultraloq products use Z-Wave to integrate with Home Assistant.

Result:

U-tech ultraloq is listed on our user documentation website under integrations with an automatically generated stub page that directs the user to the integration to use.
U-tech ultraloq is listed in Home Assistant when clicking "add integration". When selected, we guide the user in adding this Z-Wave device (and in case Z-Wave isn't set up yet, into setting up Z-Wave first).
info
Brands also support setting IoT standards.

It is preferred to set IoT standards on the brand level, and only use a virtual integration in case it would impose confusion for the end user.


Config flow
Integrations can be set up via the user interface by adding support for a config flow to create a config entry. Integrations that want to support config entries will need to define a Config Flow Handler. This handler will manage the creation of entries from user input, discovery or other sources (like Home Assistant OS).

Config Flow Handlers control the data that is stored in a config entry. This means that there is no need to validate that the config is correct when Home Assistant starts up. It will also prevent breaking changes because we will be able to migrate configuration entries to new formats if the version changes.

When instantiating the handler, Home Assistant will make sure to load all dependencies and install the requirements of the integration.

Updating the manifest
You need to update your integrations manifest to inform Home Assistant that your integration has a config flow. This is done by adding config_flow: true to your manifest (docs).

Defining your config flow
Config entries use the data flow entry framework to define their config flows. The config flow needs to be defined in the file config_flow.py in your integration folder, extend homeassistant.config_entries.ConfigFlow and pass a domain key as part of inheriting ConfigFlow.

from homeassistant import config_entries
from .const import DOMAIN


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1


Once you have updated your manifest and created the config_flow.py, you will need to run python3 -m script.hassfest (one time only) for Home Assistant to activate the config entry for your integration.

Config flow title
The title of a config flow can be influenced by integrations, and is determined in this priority order:

If title_placeholders is set to a non-empty dictionary in the config flow, it will be used to dynamically calculate the config flow's title. Reauth and reconfigure flows automatically set title_placeholders to {"name": config_entry_title}.
If the integration provides a localized flow_title, that will be used, with any translation placeholders substituted from the title_placeholders.
If the integration does not provide a flow_title but the title_placeholders includes a name, the name will be used as the flow's title.
Set the flow title to the integration's localized title, if it exists.
Set the flow title to the integration manifest's name, if it exists.
Set the flow title to the integration's domain.
Note that this priority order means that:

A localized flow_title is ignored if the title_placeholders dictionary is missing or empty, even if the localized flow_title does not have any placeholders
If title_placeholders is not empty, but there's no localized flow_title and the title_placeholders does not include a name, it is ignored.
Defining steps
Your config flow will need to define steps of your configuration flow. Each step is identified by a unique step name (step_id). The step callback methods follow the pattern async_step_<step_id>. The docs for Data Entry Flow describe the different return values of a step. Here is an example of how to define the user step:

import voluptuous as vol

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )


There are a few step names reserved for system use:

Step name	Description
bluetooth	Invoked if your integration has been discovered via Bluetooth as specified using bluetooth in the manifest.
discovery	DEPRECATED Invoked if your integration has been discovered and the matching step has not been defined.
dhcp	Invoked if your integration has been discovered via DHCP as specified using dhcp in the manifest.
hassio	Invoked if your integration has been discovered via a Supervisor add-on.
homekit	Invoked if your integration has been discovered via HomeKit as specified using homekit in the manifest.
mqtt	Invoked if your integration has been discovered via MQTT as specified using mqtt in the manifest.
ssdp	Invoked if your integration has been discovered via SSDP/uPnP as specified using ssdp in the manifest.
usb	Invoked if your integration has been discovered via USB as specified using usb in the manifest.
user	Invoked when a user initiates a flow via the user interface or when discovered and the matching and discovery step are not defined.
reconfigure	Invoked when a user initiates a flow to reconfigure an existing config entry via the user interface.
zeroconf	Invoked if your integration has been discovered via Zeroconf/mDNS as specified using zeroconf in the manifest.
reauth	Invoked if your integration indicates it requires reauthentication, e.g., due to expired credentials.
import	Reserved for migrating from YAML configuration to config entries.
Unique IDs
A config flow can attach a unique ID, which must be a string, to a config flow to avoid the same device being set up twice. The unique ID does not need to be globally unique, it only needs to be unique within an integration domain.

By setting a unique ID, users will have the option to ignore the discovery of your config entry. That way, they won't be bothered about it anymore. If the integration uses Bluetooth, DHCP, HomeKit, Zeroconf/mDNS, USB, or SSDP/uPnP to be discovered, supplying a unique ID is required.

If a unique ID isn't available, alternatively, the bluetooth, dhcp, zeroconf, hassio, homekit, ssdp, usb, and discovery steps can be omitted, even if they are configured in the integration manifest. In that case, the user step will be called when the item is discovered.

Alternatively, if an integration can't get a unique ID all the time (e.g., multiple devices, some have one, some don't), a helper is available that still allows for discovery, as long as there aren't any instances of the integration configured yet.

Here's an example of how to handle discovery where a unique ID is not always available:

if device_unique_id:
    await self.async_set_unique_id(device_unique_id)
else:
    await self._async_handle_discovery_without_unique_id()

Managing Unique IDs in Config Flows
When a unique ID is set, the flow will immediately abort if another flow is in progress for this unique ID. You can also quickly abort if there is already an existing config entry for this ID. Config entries will get the unique ID of the flow that creates them.

Call inside a config flow step:

# Assign a unique ID to the flow and abort the flow
# if another flow with the same unique ID is in progress
await self.async_set_unique_id(device_unique_id)

# Abort the flow if a config entry with the same unique ID exists
self._abort_if_unique_id_configured()

Should the config flow then abort, the text resource with the key already_configured from the abort part of your strings.json will be displayed to the user in the interface as an abort reason.

{
  "config": {
    "abort": {
      "already_configured": "[%key:common::config_flow::abort::already_configured_device%]"
    }
  }
}


Unique ID requirements
A unique ID is used to match a config entry to the underlying device or API. The unique ID must be stable, should not be able to be changed by the user and must be a string.

The Unique ID can be used to update the config entry data when device access details change. For example, for devices that communicate over the local network, if the IP address changes due to a new DHCP assignment, the integration can use the Unique ID to update the host using the following code snippet:

    await self.async_set_unique_id(serial_number)
    self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})


Example acceptable sources for a unique ID
Serial number of a device
MAC address: formatted using homeassistant.helpers.device_registry.format_mac; Only obtain the MAC address from the device API or a discovery handler. Tools that rely on reading the arp cache or local network access such as getmac will not function in all supported network environments and are not acceptable.
A string representing the latitude and longitude or other unique geo location
Unique identifier that is physically printed on the device or burned into an EEPROM
Sometimes acceptable sources for a unique ID for local devices
Hostname: If a subset of the hostname contains one of the acceptable sources, this portion can be used
Sometimes acceptable sources for a unique ID for cloud services
Email Address: Must be normalized to lowercase
Username: Must be normalized to lowercase if usernames are case-insensitive.
Account ID: Must not have collisions
Unacceptable sources for a unique ID
IP Address
Device Name
Hostname if it can be changed by the user
URL
Discovery steps
When an integration is discovered, their respective discovery step is invoked (ie async_step_dhcp or async_step_zeroconf) with the discovery information. The step will have to check the following things:

Make sure there are no other instances of this config flow in progress of setting up the discovered device. This can happen if there are multiple ways of discovering that a device is on the network.
In most cases, it's enough to set the unique ID on the flow and check if there's already a config entry with the same unique ID as explained in the section about managing unique IDs in config flows
In some cases, a unique ID can't be determined, or the unique ID is ambiguous because different discovery sources may have different ways to calculate it. In such cases:
Implement the method def is_matching(self, other_flow: Self) -> bool on the flow.
Call hass.config_entries.flow.async_has_matching_flow(self).
Your flow's is_matching method will then be called once for each other ongoing flow.
Make sure that the device is not already set up.
Invoking a discovery step should never result in a finished flow and a config entry. Always confirm with the user.
Discoverable integrations that require no authentication
If your integration is discoverable without requiring any authentication, you'll be able to use the Discoverable Flow that is built-in. This flow offers the following features:

Detect if devices/services can be discovered on the network before finishing the config flow.
Support all manifest-based discovery protocols.
Limit to only 1 config entry. It is up to the config entry to discover all available devices.
To get started, run python3 -m script.scaffold config_flow_discovery and follow the instructions. This will create all the boilerplate necessary to configure your integration using discovery.

Configuration via OAuth2
Home Assistant has built-in support for integrations that offer account linking using the OAuth2 authorization framework. To be able to leverage this, you will need to structure your Python API library in a way that allows Home Assistant to be responsible for refreshing tokens. See our API library guide on how to do this.

The built-in OAuth2 support works out of the box with locally configured client ID / secret using the Application Credentials platform and with the Home Assistant Cloud Account Linking service. This service allows users to link their account with a centrally managed client ID/secret. If you want your integration to be part of this service, reach out to us at partner@openhomefoundation.org.

To get started, run python3 -m script.scaffold config_flow_oauth2 and follow the instructions. This will create all the boilerplate necessary to configure your integration using OAuth2.

Translations
Translations for the config flow handlers are defined under the config key in the integration translation file strings.json. Example of the Hue integration:

{
  "title": "Philips Hue Bridge",
  "config": {
    "step": {
      "init": {
        "title": "Pick Hue bridge",
        "data": {
          "host": "Host"
        }
      },
      "link": {
        "title": "Link Hub",
        "description": "Press the button on the bridge to register Philips Hue with Home Assistant.\n\n![Location of button on bridge](/static/images/config_philips_hue.jpg)"
      }
    },
    "error": {
      "register_failed": "Failed to register, please try again",
      "linking": "Unknown linking error occurred."
    },
    "abort": {
      "discover_timeout": "Unable to discover Hue bridges",
      "no_bridges": "No Philips Hue bridges discovered",
      "all_configured": "All Philips Hue bridges are already configured",
      "unknown": "Unknown error occurred",
      "cannot_connect": "Unable to connect to the bridge",
      "already_configured": "Bridge is already configured"
    }
  }
}


When the translations are merged into Home Assistant, they will be automatically uploaded to Lokalise where the translation team will help to translate them in other languages. While developing locally, you will need to run python3 -m script.translations develop to see changes made to strings.json More info on translating Home Assistant.

Config entry migration
As mentioned above - each Config Entry has a version assigned to it. This is to be able to migrate Config Entry data to new formats when Config Entry schema changes.

Migration can be handled programatically by implementing function async_migrate_entry in your integration's __init__.py file. The function should return True if migration is successful.

The version is made of a major and minor version. If minor versions differ but major versions are the same, integration setup will be allowed to continue even if the integration does not implement async_migrate_entry. This means a minor version bump is backwards compatible unlike a major version bump which causes the integration to fail setup if the user downgrades Home Assistant Core without restoring their configuration from backup.

# Example migration function
async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1:

        new_data = {**config_entry.data}
        if config_entry.minor_version < 2:
            # TODO: modify Config Entry data with changes in version 1.2
            pass
        if config_entry.minor_version < 3:
            # TODO: modify Config Entry data with changes in version 1.3
            pass

        hass.config_entries.async_update_entry(config_entry, data=new_data, minor_version=3, version=1)

    _LOGGER.debug("Migration to configuration version %s.%s successful", config_entry.version, config_entry.minor_version)

    return True


Reconfigure
A config entry can allow reconfiguration by adding a reconfigure step. This provides a way for integrations to allow users to change config entry data without the need to implement an OptionsFlow for changing setup data which is not meant to be optional.

This is not meant to handle authentication issues or reconfiguration of such. For that we have the reauth step, which should be implemented to automatically start in such case there is an issue with authentication.

import voluptuous as vol

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Example integration."""

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            # TODO: process user input
            self.async_set_unique_id(user_id)
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=data,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({vol.Required("input_parameter"): str}),
        )


On success, reconfiguration flows are expected to update the current entry and abort; they should not create a new entry. This is usually done with the return self.async_update_reload_and_abort helper. Automated tests should verify that the reconfigure flow updates the existing config entry and does not create additional entries.

Checking whether you are in a reconfigure flow can be done using if self.source == SOURCE_RECONFIGURE. It is also possible to access the corresponding config entry using self._get_reconfigure_entry(). Ensuring that the unique_id is unchanged should be done using await self.async_set_unique_id followed by self._abort_if_unique_id_mismatch().

Reauthentication
Gracefully handling authentication errors such as invalid, expired, or revoked tokens is needed to advance on the Integration Quality Scale. This example of how to add reauth to the OAuth flow created by script.scaffold following the pattern in Building a Python library. If you are looking for how to trigger the reauthentication flow, see handling expired credentials.

This example catches an authentication exception in config entry setup in __init__.py and instructs the user to visit the integrations page in order to reconfigure the integration.

To allow the user to change config entry data which is not optional (OptionsFlow) and not directly related to authentication, for example a changed host name, integrations should implement the reconfigure step.


from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant
from . import api

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup up a config entry."""

    # TODO: Replace with actual API setup and exception
    auth = api.AsyncConfigEntryAuth(...)
    try:
        await auth.refresh_tokens()
    except TokenExpiredError as err:
        raise ConfigEntryAuthFailed(err) from err

    # TODO: Proceed with integration setup

The flow handler in config_flow.py also needs to have some additional steps to support reauth which include showing a confirmation, starting the reauth flow, updating the existing config entry, and reloading to invoke setup again.


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle OAuth2 authentication."""

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> dict:
        """Create an oauth config entry or update existing entry for reauth."""
        self.async_set_unique_id(user_id)
        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(),
                data_updates=data,
            )
        self._abort_if_unique_id_configured()
        return await super().async_oauth_create_entry(data)


By default, the async_update_reload_and_abort helper method aborts the flow with reauth_successful after update and reload. By default, the entry will always be reloaded. If the config entry only should be reloaded in case the config entry was updated, specify reload_even_if_entry_is_unchanged=False.

Depending on the details of the integration, there may be additional considerations such as ensuring the same account is used across reauth, or handling multiple config entries.

The reauth confirmation dialog needs additional definitions in strings.json for the reauth confirmation and success dialogs:

{
  "config": {
    "step": {
      "reauth_confirm": {
        "title": "[%key:common::config_flow::title::reauth%]",
        # TODO: Replace with the name of the integration
        "description": "The Example integration needs to re-authenticate your account"
      }
    },
    "abort": {
      "reauth_successful": "[%key:common::config_flow::abort::reauth_successful%]"
    },
}


See Translations local development instructions.

Authentication failures (such as a revoked oauth token) can be a little tricky to manually test. One suggestion is to make a copy of config/.storage/core.config_entries and manually change the values of access_token, refresh_token, and expires_at depending on the scenario you want to test. You can then walk advance through the reauth flow and confirm that the values get replaced with new valid tokens.

On success, reauth flows are expected to update the current entry and abort; they should not create a new entry. This is usually done with the return self.async_update_reload_and_abort helper. Automated tests should verify that the reauth flow updates the existing config entry and does not create additional entries.

Checking whether you are in a reauth flow can be done using if self.source == SOURCE_REAUTH. It is also possible to access the corresponding config entry using self._get_reauth_entry(). Ensuring that the unique_id is unchanged should be done using await self.async_set_unique_id followed by self._abort_if_unique_id_mismatch().

Subentry flows
An integration can implement subentry flows to allow users to add, and optionally reconfigure, subentries. An example of this is an integration providing weather forecasts, where the config entry stores authentication details and each location for which weather forecasts should be provided is stored as a subentry.

Subentry flows are similar to config flows, except that subentry flows don't support reauthentication or discovery; a subentry flow can only be initiated via the user or reconfigure steps.

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Example integration."""

    ...

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {"location": LocationSubentryFlowHandler}

class LocationSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding and modifying a location."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to add a new location."""
        ...

Subentry unique ID
Subentries can set a unique ID. The rules are similar to unique IDs of config entries, except that subentry unique IDs only need to be unique within the config entry.

Subentry translations
Translations for subentry flow handlers are defined under the config_subentries key in the integration translation file strings.json, for example:

{
  "config_subentries": {
    "location": {
      "title": "Weather location",
      "step": {
        "user": {
          "title": "Add location",
          "description": "Configure the weather location"
        },
        "reconfigure": {
          "title": "Update location",
          "description": "..."
        }
      },
      "error": {
      },
      "abort": {
      }
    }
  }
}

Subentry reconfigure
Subentries can be reconfigured, similar to how config entries can be reconfigured. To add support for reconfigure to a subentry flow, implement a reconfigure step.

class LocationSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding and modifying a location."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to add a new location."""
        ...

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to modify an existing location."""
        # Retrieve the parent config entry for reference.
        config_entry = self._get_reconfigure_entry()
        # Retrieve the specific subentry targeted for update.
        config_subentry = self._get_reconfigure_subentry()
        ...


Testing your config flow
Integrations with a config flow require full test coverage of all code in config_flow.py to be accepted into core. Test your code includes more details on how to generate a coverage report.

Options flow
An integration that is configured via a config entry can expose options to the user to allow tweaking behavior of the integration, like which devices or locations should be integrated.

Config Entry Options uses the Data Flow Entry framework to allow users to update the options of a config entry. Components that want to support config entry options will need to define an Options Flow Handler.

Options support
For an integration to support options it needs to have an async_get_options_flow method in its config flow handler. Calling it will return an instance of the components options flow handler.

@staticmethod
@callback
def async_get_options_flow(
    config_entry: ConfigEntry,
) -> OptionsFlowHandler:
    """Create the options flow."""
    return OptionsFlowHandler()

Flow handler
The Flow handler works just like the config flow handler, except that the first step in the flow will always be async_step_init. The current config entry details are available through the self.config_entry property.

OPTIONS_SCHEMA=vol.Schema(
    {
        vol.Required("show_things"): bool,
    }
)
class OptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )

Signal updates
If the integration should act on updated options, you can register an update listener to the config entry that will be called when the entry is updated. A listener is registered by adding the following to the async_setup_entry function in your integration's __init__.py.

entry.async_on_unload(entry.add_update_listener(update_listener))

Using the above means the Listener is attached when the entry is loaded and detached at unload. The Listener shall be an async function that takes the same input as async_setup_entry. Options can then be accessed from entry.options.

async def update_listener(hass, entry):
    """Handle options update."""


Integration diagnostics
Integrations can provide diagnostics to help the user gather data to aid in troubleshooting. Diagnostics can be provided for config entries but also individually for each device entry.

Users can download config entry diagnostics from the config entry options menu, on the integration page. For device diagnostics, users can download them from the device info section (or from its menu, depending on the integration). Note that if an integration does not implement device diagnostics, the device page will provide config entry diagnostics.

warning
It is critical to ensure that no sensitive data is exposed. This includes but is not limited to:

Passwords and API keys
Authentication tokens
Location data
Personal information
Home Assistant provides the async_redact_data utility function which you can use to safely remove sensitive data from the diagnostics output.

The following is an example on how to implement both config entry and device entry diagnostics:

TO_REDACT = [
    CONF_API_KEY,
    APPLIANCE_CODE
]

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MyConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "data": entry.runtime_data.data,
    }

async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: MyConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    appliance = _get_appliance_by_device_id(hass, device.id)
    return {
        "details": async_redact_data(appliance.raw_data, TO_REDACT),
        "data": appliance.data,
    }

An integration can provide both types of diagnostics or just one of them.


Integration system health
The system health platform allows integrations to provide information that helps users understand the state of the integration. This can include details such as the availability of an endpoint, the current server that the integration is connected to, how much of a request quota is still available, etc.

Users can find the aggregated system health by going to Settings > Repairs and selecting System information in the three dots menu.

Implementing the system health platform
Add a system_health.py file to the integration and implement the async_register method, to register the info callback:

"""Provide info to system health."""

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

@callback
def async_register(hass: HomeAssistant, register: system_health.SystemHealthRegistration) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


The info callback should return a dictionary whose values can be of any type, including coroutines. In case a coroutine is set for a dictionary entry, the frontend will display a waiting indicator and will automatically update once the coroutine finishes and provides a result.

async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get info for the info page."""
    config_entry: ExampleConfigEntry = hass.config_entries.async_entries(DOMAIN)[0]
    quota_info = await config_entry.runtime_data.async_get_quota_info()

    return {
        "consumed_requests": quota_info.consumed_requests,
        "remaining_requests": quota_info.requests_remaining,
        # checking the url can take a while, so set the coroutine in the info dict
        "can_reach_server": system_health.async_check_can_reach_url(hass, ENDPOINT),
    }


tip
The system_health component provides the async_check_can_reach_url helper as a way to easily implement checking the availability of a URL.

Translate each key in the info dictionary using the system_health section in the strings.json file, to provide good descriptions:

  "system_health": {
    "info": {
      "can_reach_server": "Reach Example server",
      "remaining_requests": "Remaining allowed requests"
    }
  }


Integration configuration via YAML
configuration.yaml is a configuration file defined by the user. It is automatically created by Home Assistant on first launch. It defines which components to load.

Note about YAML for devices and/or services
Integrations that communicate with devices and/or services are configured via a config flow. In rare cases, we can make an exception. Existing integrations that should not have a YAML configuration are allowed and encouraged to implement a configuration flow and remove YAML support. Changes to existing YAML configuration for these same existing integrations will no longer be accepted.

For more detail read ADR-0010

Pre-processing
Home Assistant will do some pre-processing on the config based on the components that are specified to load.

CONFIG_SCHEMA
If a component defines a variable CONFIG_SCHEMA, the config object that is passed in will be the result of running the config through CONFIG_SCHEMA. CONFIG_SCHEMA should be a voluptuous schema.

PLATFORM_SCHEMA
If a component defines a variable PLATFORM_SCHEMA, the component will be treated as an entity component. The configuration of entity components is a list of platform configurations.

Home Assistant will gather all platform configurations for this component. It will do so by looking for configuration entries under the domain of the component (ie light) but also under any entry of domain + extra text.

While gathering the platform configs, Home Assistant will validate them. It will see if the platform exists and if the platform defines a PLATFORM_SCHEMA, validate against that schema. If not defined, it will validate the config against the PLATFORM_SCHEMA defined in the component. Any configuration that references non existing platforms or contains invalid config will be removed.

The following configuration.yaml:

unrelated_component:
  some_key: some_value

switch:
  platform: example1

switch living room:
  - platform: example2
    some_config: true
  - platform: invalid_platform

will be passed to the component as

{
    "unrelated_component": {
        "some_key": "some_value"
    },
    "switch": [
        {
            "platform": "example1"
        },
        {
            "platform": "example2",
            "some_config": True
        }
    ],
}

Integration service actions
Home Assistant provides ready-made actions for a lot of things, but it doesn't always cover everything. Instead of trying to change Home Assistant, it is preferred to add it as a service action under your own integration first. Once we see a pattern in these service actions, we can talk about generalizing them.

This is a simple "hello world" example to show the basics of registering a service action. To use this example, create the file <config dir>/custom_components/hello_action/__init__.py and copy the below example code.

Actions can be called from automations and from the actions "Developer tools" in the frontend.

DOMAIN = "hello_action"

ATTR_NAME = "name"
DEFAULT_NAME = "World"


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    def handle_hello(call):
        """Handle the service action call."""
        name = call.data.get(ATTR_NAME, DEFAULT_NAME)

        hass.states.set("hello_action.hello", name)

    hass.services.register(DOMAIN, "hello", handle_hello)

    # Return boolean to indicate that initialization was successful.
    return True


To load the integration in Home Assistant is necessary to create a manifest.json and to add an entry in your configuration.yaml. When your component is loaded, a new service should be available to call.

# configuration.yaml entry
hello_action:

An example of manifest.json:

{
    "domain": "hello_action",
    "name": "Hello Action",
    "documentation": "https://developers.home-assistant.io/docs/dev_101_services",
    "iot_class": "local_push",
    "version": "0.1.0"
}


Open the frontend and in the sidebar, click the first icon in the developer tool section. This will open the Actions developer tool. On the right, find your action and click on it. This will automatically fill in the correct values.

Pressing "Perform action" will now call your service action without any parameters. This will cause your service action to create a state with the default name 'World'. If you want to specify the name, you have to specify a parameter by providing it through service action Data. In YAML mode, add the following and press "Perform Service" again.

service: hello_action.hello
data:
  name: Planet

The service action will now overwrite the previous state with "Planet".

Service action descriptions
Adding actions is only useful if users know about them. In Home Assistant we use a services.yaml as part of your integration to describe the service actions.

Actions are published under the domain name of your integration, so in services.yaml we only use the service action name as the base key.

Service action description example
# Example services.yaml entry

# Service ID
set_speed:
  # If the service action accepts entity IDs, target allows the user to specify
  # entities by entity, device, or area. If `target` is specified, `entity_id`
  # should not be  defined in the `fields` map. By default it shows only targets
  # matching entities from the same domain as the action, but if further
  # customization is required, target supports the entity, device, and area
  # selectors (https://www.home-assistant.io/docs/blueprint/selectors/).
  # Entity selector parameters will automatically be applied to device and area,
  # and device selector parameters will automatically be applied to area.
  target:
    entity:
      domain: fan
      # If not all entities from the action's domain support a action, entities
      # can be further filtered by the `supported_features` state attribute. An
      # entity will only be possible to select if it supports at least one of the
      # listed supported features.
      supported_features:
        - fan.FanEntityFeature.SET_SPEED
        # If a service action requires more than one supported feature, the item
        # should be given as a list of required supported features. For example,
        # if the service action requires both SET_SPEED and OSCILLATE it would
        # be expressed like this
        - - fan.FanEntityFeature.SET_SPEED
          - fan.FanEntityFeature.OSCILLATE
  # Different fields that your service action accepts
  fields:
    # Key of the field
    speed:
      # Whether or not field is required (default = false)
      required: true
      # Advanced fields are only shown when the advanced mode is enabled for the user
      # (default = false)
      advanced: true
      # Example value that can be passed for this field
      example: "low"
      # The default field value
      default: "high"
      # Selector (https://www.home-assistant.io/docs/blueprint/selectors/) to control
      # the input UI for this field
      selector:
        select:
          translation_key: "fan_speed"
          options:
            - "off"
            - "low"
            - "medium"
            - "high"
    # Fields can be grouped in collapsible sections, this is useful to initially hide
    # advanced fields and to group related fields. Note that the collapsible section
    # only affect presentation to the user, service action data will not be nested.
    advanced_fields:
      # Whether or not the section is initially collapsed (default = false)
      collapsed: true
      # Input fields in this section
      fields:
        speed_pct:
          selector:
            number:
              min: 0
              max: 100


info
The name and description of the service actions are set in our translations and not in the service action description. Each service action and service action field must have a matching translation defined.

Grouping of service action fields
Input fields can be visually grouped in sections. Grouping input fields by sections influences only how the inputs are displayed to the user, and not how service action data is structured.

In the service action description example, the speed_pct input field is inside an initially collapsed section advanced_fields. The service action data for the service in the example is {"speed_pct": 50}, not {"advanced_fields": {"speed_pct": 50}}.

Filtering service action fields
In some cases, entities from a action's domain may not support all service action fields. By providing a filter for the field description, the field will only be shown if at least one selected entity supports the field according to the configured filter.

A filter must specify either supported_features or attribute, combing both is not supported.

A supported_features filter is specified by of a list of supported features. The field will be shown if at least one selected entity supports at least one of the listed features.

An attribute filter combines an attribute with a list of values. The field will be shown if at least one selected entity's attribute is set to one of the listed attribute states. If the attribute state is a list, the field will be shown if at least one item in a selected entity's attribute state is set to one of the listed attribute states.

This is a partial example of a field which is only shown if at least one selected entity supports ClimateEntityFeature.TARGET_TEMPERATURE:

  fields:
    temperature:
      name: Temperature
      description: New target temperature for HVAC.
      filter:
        supported_features:
          - climate.ClimateEntityFeature.TARGET_TEMPERATURE

This is a partial example of a field which is only shown if at least one selected entity's supported_color_modes attribute includes either light.ColorMode.COLOR_TEMP or light.ColorMode.HS:

    color_temp:
      name: Color temperature
      description: Color temperature for the light in mireds.
      filter:
        attribute:
          supported_color_modes:
            - light.ColorMode.COLOR_TEMP
            - light.ColorMode.HS

Icons
Actions can also have icons. These icons are used in the Home Assistant UI when displaying the service action in places like the automation and script editors.

The icon to use for each service action can be defined in the icons.json translation file in the integration folder, under the services key. The key should be the service action name, and the value should be the icon to use.

The following example shows how to provide icons for the turn_on and turn_off service actions of an integration:

{
  "services": {
    "turn_on": {"service": "mdi:lightbulb-on"},
    "turn_off": {"service": "mdi:lightbulb-off"}
  }
}

In addition, icons can optionally be specified for collapsible sections.

The following example shows how to provide an icon for the advanced_options section:

{
  "services": {
    "start_brewing": {
      "service": "mdi:flask",
      "sections": {
        "advanced_options": "mdi:test-tube"
      }
    }
  }
}

Entity service actions
Sometimes you want to provide extra actions to control your entities. For example, the Sonos integration provides action to group and ungroup devices. Entity service actions are special because there are many different ways a user can specify entities. It can use areas, a group or a list of entities.

You need to register entity service actions in your platforms, like <your-domain>/media_player.py. These service actions will be made available under your domain and not under the platform domain (e.g. media player domain). A schema can be passed to async_register_entity_service if the entity service action has fields. The schema must be either of:

A dictionary which will automatically be passed to cv._make_entity_service_schema
A validator returned by cv._make_entity_service_schema
A validator returned by cv._make_entity_service_schema, wrapped in a vol.Schema
A validator returned by cv._make_entity_service_schema, wrapped in a vol.All
Example code:

from homeassistant.helpers import config_validation as cv, entity_platform, service

async def async_setup_entry(hass, entry):
    """Set up the media player platform for Sonos."""

    platform = entity_platform.async_get_current_platform()

    # This will call Entity.set_sleep_timer(sleep_time=VALUE)
    platform.async_register_entity_service(
        SERVICE_SET_TIMER,
        {
            vol.Required('sleep_time'): cv.time_period,
        },
        "set_sleep_timer",
    )


If you need more control over the service action call, you can also pass an async function that will be called instead of "set_sleep_timer":

async def custom_set_sleep_timer(entity, service_call):
    await entity.set_sleep_timer(service_call.data['sleep_time'])

Response data
Actions may respond to an action call with data for powering more advanced automations. There are some additional implementation requirements:

Response data must be a dict and serializable in JSON homeassistant.util.json.JsonObjectType in order to interoperate with other parts of the system, such as the frontend.
Errors must be raised as exceptions just like any other service action call as we do not want end users to need complex error handling in scripts and automations. The response data should not contain error codes used for error handling.
Example code:

import datetime
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.util.json import JsonObjectType


SEARCH_ITEMS_SERVICE_NAME = "search_items"
SEARCH_ITEMS_SCHEMA = vol.Schema({
    vol.Required("start"): datetime.datetime,
    vol.Required("end"): datetime.datetime,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the platform."""

    async def search_items(call: ServiceCall) -> ServiceResponse:
        """Search in the date range and return the matching items."""
        items = await my_client.search(call.data["start"], call.data["end"])
        return {
            "items": [
                {
                    "summary": item["summary"],
                    "description": item["description"],
                } for item in items
            ],
        }

      hass.services.async_register(
          DOMAIN,
          SEARCH_ITEMS_SERVICE_NAME,
          search_items,
          schema=SEARCH_ITEMS_SCHEMA,
          supports_response=SupportsResponse.ONLY,
      )


The use of response data is meant for cases that do not fit the Home Assistant state. For example, a response stream of objects. Conversely, response data should not be used for cases that are a fit for entity state. For example, a temperature value should just be a sensor.

Supporting response data
Action calls are registered with a SupportsResponse value to indicate response data is supported.

Value	Description
OPTIONAL	Performs an action and can optionally return response data. The service action should conditionally check the ServiceCall property return_response to decide whether or not response data should be returned, or None.
ONLY	Doesn't perform any actions and always returns response data.


Integration platforms
Home Assistant has various built-in integrations that abstract device types. There are lights, switches, covers, climate devices, and many more. Your integration can hook into these integrations by creating a platform. You will need a platform for each integration that you are integrating with.

To create a platform, you will need to create a file with the domain name of the integration that you are building a platform for. So if you are building a light, you will add a new file light.py to your integration folder.

We have created two example integrations that should give you a look at how this works:

Example sensor platform: hello world of platforms.
Example light platform: showing best practices.
Interfacing with devices
One Home Assistant rule is that the integration should never interface directly with devices. Instead, it should interact with a third-party Python 3 library. This way, Home Assistant can share code with the Python community and keep the project maintainable.

Once you have your Python library ready and published to PyPI, add it to the manifest. It will now be time to implement the Entity base class that is provided by the integration that you are creating a platform for.

Find your integration at the entity index to see what methods and properties are available to implement.

Integration with multiple platforms
Most integrations consist of a single platform. And in that case, it's fine to just define that one platform. However, if you are going to add a second platform, you will want to centralize your connection logic. This is done inside the component (__init__.py).

If your integration is configurable via configuration.yaml, it will cause the entry point of your configuration to change, as now users will need to set up your integration directly, and it is up to your integration to set up the platforms.

Loading platforms when configured via a config entry
If your integration is set up via a config entry, you will need to forward the config entry to the appropriate integration to set up your platform. For more info, see the config entry documentation.

Loading platforms when configured via configuration.yaml
If your integration is not using config entries, it will have to use our discovery helpers to set up its platforms. Note, this approach does not support unloading.

To do this, you will need to use the load_platform and async_load_platform methods from the discovery helper.

See also a full example that implements this logic

Fetching data
Your integration will need to fetch data from an API to be able to provide this to Home Assistant. This API can be available over the web (local or cloud), sockets, serial ports exposed via USB sticks, etc.

Push vs poll
APIs come in many different shapes and forms but at its core they fall in two categories: push and poll.

With push, we subscribe to an API and we get notified by the API when new data is available. It pushes the changes to us. Push APIs are great because they consume less resources. When a change happens, we can get notified of a change and don't have to re-fetch all the data and find changes. Because entities can be disabled, you should make sure that your entity subscribes inside the async_added_to_hass callback and unsubscribes on remove.

With polling, we will fetch the latest data from the API at a specified interval. Your integration will then supply this data to its entity, which is written to Home Assistant.

Because polling is so common, Home Assistant by default assumes that your entity is based on polling. If this is not the case, return False from the Entity.should_poll property. When you disable polling, your integration will be responsible for calling one of the methods to indicate to Home Assistant that it's time to write the entity state to Home Assistant:

If you are executing from within an async function and don't need your entity update method called, call Entity.async_write_ha_state(). This is an async callback that will write the state to the state machine within yielding to the event loop.
Entity.schedule_update_ha_state(force_refresh=False)/Entity.async_schedule_update_ha_state(force_refresh=False) will schedule an update of the entity. If force_refresh is set to True, Home Assistant will call your entities update method (update()/async_update()) prior to writing the state.
Polling API endpoints
We're going to explain a few different API types here and the best way to integrate them in Home Assistant. Note that some integrations will encounter a combination of the ones below.

Coordinated, single API poll for data for all entities
This API will have a single method to fetch data for all the entities that you have in Home Assistant. In this case we will want to have a single periodical poll on this endpoint, and then let entities know as soon as new data is available for them.

Home Assistant provides a DataUpdateCoordinator class to help you manage this as efficiently as possible.

When using the DataUpdateCoordinator, the data being polled is often expected to stay mostly the same. For example, if you are polling a light that is only turned on once a week, that data may be the same nearly all the time. The default behavior is always calling back listeners when the data is updated, even if it does not change. If the data returned from the API can be compared for changes with the Python __eq__ method, set always_update=False when creating the DataUpdateCoordinator to avoid unnecessary callbacks and writes to the state machine.

"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = MyCoordinator(hass, config_entry, my_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        MyEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config_entry, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            config_entry=config_entry,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True
        )
        self.my_api = my_api
        self._device: MyDevice | None = None

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self._device = await self.my_api.get_device()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                listening_idx = set(self.async_contexts())
                return await self.my_api.fetch_data(listening_idx)
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class MyEntity(CoordinatorEntity, LightEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()


Separate polling for each individual entity
Some APIs will offer an endpoint per device. It sometimes won't be possible to map a device from your API to a single entity. If you create multiple entities from a single API device endpoint, please see the previous section.

If you can map exactly one device endpoint to a single entity, you can fetch the data for this entity inside the update()/async_update() methods. Make sure polling is set to True and Home Assistant will call this method regularly.

If your entities need to fetch data before being written to Home Assistant for the first time, pass update_before_add=True to the add_entities method: add_entities([MyEntity()], update_before_add=True).

You can control the polling interval for your integration by defining a SCAN_INTERVAL constant in your platform. Careful with setting this too low. It will take up resources in Home Assistant, can overwhelm the device hosting the API or can get you blocked from cloud APIs. The minimum allowed value is 5 seconds.

from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=5)

Pushing API endpoints
If you have an API endpoint that pushes data, you can still use the data update coordinator if you want. Do this by not passing polling parameters update_method and update_interval to the constructor.

When new data arrives, use coordinator.async_set_updated_data(data) to pass the data to the entities. If this method is used on a coordinator that polls, it will reset the time until the next time it will poll for data.

Request parallelism
info
This is an advanced topic.

Home Assistant has built-in logic to make sure that integrations do not hammer APIs and consume all available resources in Home Assistant. This logic is built around limiting the number of parallel requests. This logic is automatically used during service action calls and entity updates.

Home Assistant controls the number of parallel updates (calls to update()) by maintaining a semaphore per integration. For example, if the semaphore allows 1 parallel connection, updates and service action calls will wait if one is in progress. If the value is 0, the integration is itself responsible for limiting the number of parallel requests if necessary.

The default value for parallel requests for a platform is decided based on the first entity that is added to Home Assistant. It's 0 if the entity defines the async_update method, else it's 1. (this is a legacy decision)

Platforms can override the default by defining the PARALLEL_UPDATES constant in their platform (ie rflink/light.py).




Handling setup failures
Your integration may not be able to be set up for a variety of reasons. The most common cases are because the device or service is offline or the credentials are no longer valid. Your integration must retry setup so it can recover as soon as reasonably possible when the device or service is back online without the user having to restart Home Assistant.

Handling offline or unavailable devices and services
Integrations using async_setup_entry
Raise the ConfigEntryNotReady exception from async_setup_entry in the integration's __init__.py, and Home Assistant will automatically take care of retrying set up later. To avoid doubt, raising ConfigEntryNotReady in a platform's async_setup_entry is ineffective because it is too late to be caught by the config entry setup.

Example
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the config entry for my device."""
    device = MyDevice(entry.data[CONF_HOST])
    try:
        await device.async_setup()
    except (asyncio.TimeoutError, TimeoutException) as ex:
        raise ConfigEntryNotReady(f"Timeout while connecting to {device.ipaddr}") from ex


If you are using a DataUpdateCoordinator, calling await coordinator.async_config_entry_first_refresh() will also trigger this exception automatically if the first refresh failed.

If your integration supports discovery, Home Assistant will automatically retry as soon as your device or service gets discovered.

Handling logging of a retry
Pass the error message to ConfigEntryNotReady as the first argument. Home Assistant will log at debug level. The error message will also be propagated to the UI and shown on the integrations page. Suppose you do not set a message when raising ConfigEntryNotReady; in that case, Home Assistant will try to extract the reason from the exception that is the cause of ConfigEntryNotReady if it was propagated from another exception.

The integration should not log any non-debug messages about the retry, and should instead rely on the logic built-in to ConfigEntryNotReady to avoid spamming the logs.

Integrations using async_setup_platform
Raise the PlatformNotReady exception from async_setup_platform, and Home Assistant will automatically take care of retrying set up later.

Example
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the platform."""
    device = MyDevice(conf[CONF_HOST])
    try:
        await device.async_setup()
    except ConnectionError as ex:
        raise PlatformNotReady(f"Connection error while connecting to {device.ipaddr}: {ex}") from ex


Handling logging of a retry
Pass the error message to PlatformNotReady as the first argument. Home Assistant will log the retry once with a log level of warning, and subsequent retries will be logged at debug level. Suppose you do not set a message when raising ConfigEntryNotReady; in that case, Home Assistant will try to extract the reason from the exception that is the cause of ConfigEntryNotReady if it was propagated from another exception.

The integration should not log any non-debug messages about the retry, and should instead rely on the logic built-in to PlatformNotReady to avoid spamming the logs.

Handling expired credentials
Raise the ConfigEntryAuthFailed exception, and Home Assistant will automatically put the config entry in a failure state and start a reauth flow. The exception must be raised from async_setup_entry in __init__.py or from the DataUpdateCoordinator or the exception will not be effective at triggering the reauth flow. If your integration does not use a DataUpdateCoordinator, calling entry.async_start_reauth() can be used as an alternative to starting a reauth flow.

The reauth flow will be started with the following context variables, which are available in the async_step_reauth step:

source: This will always be "SOURCE_REAUTH"
entry_id: The entry_id of the config entry that needs reauthentication
unique_id: The unique_id of the config entry that needs reauthentication
Example
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the config entry for my device."""
    device = MyDevice(entry.data[CONF_HOST])
    try:
        await device.async_setup()
    except AuthFailed as ex:
        raise ConfigEntryAuthFailed(f"Credentials expired for {device.name}") from ex
    except (asyncio.TimeoutError, TimeoutException) as ex:
        raise ConfigEntryNotReady(f"Timed out while connecting to {device.ipaddr}") from ex


Firing events
Some integrations represent devices or services that have events, like when motion is detected or a momentary button is pushed. An integration can make these available to users by firing them as events in Home Assistant.

Your integration should fire events of type <domain>_event. For example, the ZHA integration fires zha_event events.

If the event is related to a specific device/service, it should be correctly attributed. Do this by adding a device_id attribute to the event data that contains the device identifier from the device registry.

event_data = {
    "device_id": "my-device-id",
    "type": "motion_detected",
}
hass.bus.async_fire("mydomain_event", event_data)

If a device or service only fires events, you need to manually register it in the device registry.

Making events accessible to users
A Device trigger can be attached to a specific event based on the payload, and will make the event accessible to users. With a device trigger a user will be able to see all available events for the device and use it in their automations.

What not to do
Event related code should not be part of the entity logic of your integration. You want to enable the logic of converting your integration events to Home Assistant events from inside async_setup_entry inside __init__.py.

Entity state should not represent events. For example, you don't want to have a binary sensor that is on for 30 seconds when an event happens.

Listening for events
Your integration may need to take action when a specific event happens inside Home Assistant. Home Assistant provides event helpers to listen for particular event types and direct access to the event bus. The helpers are highly optimized to minimize the number of callbacks. If there is already a helper for the specific event you need to listen for, it is preferable to use the helper over listening to the event bus directly.

Available event helpers
Event helpers are available in the homeassistant.helpers.event namespace. These functions return a callable that cancels the listener.

Sync versions of the below functions are also available without the async_ prefix.

Example
unsub = async_track_state_change_event(hass, entity_ids, state_automation_listener)
unsub()


Tracking entity state changes
Function	Use case
async_track_state_change	Track specific state changes
async_track_state_change_event	Track specific state change events indexed by entity_id
async_track_state_added_domain	Track state change events when an entity is added to domains
async_track_state_removed_domain	Track state change events when an entity is removed from domains
async_track_state_change_filtered	Track state changes with a TrackStates filter that can be updated
async_track_same_state	Track the state of entities for a period and run an action
Tracking template changes
Function	Use case
async_track_template	Add a listener that fires when a template evaluates to 'true'
async_track_template_result	Add a listener that fires when the result of a template changes
Tracking entity registry changes
Function	Use case
async_track_entity_registry_updated_event	Track specific entity registry updated events indexed by entity_id
Tracking time changes
Function	Use case
async_track_point_in_time	Add a listener that fires once after a specific point in time
async_track_point_in_utc_time	Add a listener that fires once after a specific point in UTC time
async_call_later	Add a listener that is called with a delay
async_track_time_interval	Add a listener that fires repetitively at every timedelta interval
async_track_utc_time_change	Add a listener that will fire if time matches a pattern
async_track_time_change	Add a listener that will fire if local time matches a pattern
Tracking the sun
Function	Use case
async_track_sunrise	Add a listener that will fire a specified offset from sunrise daily
async_track_sunset	Add a listener that will fire a specified offset from sunset daily
Listening to the event bus directly
There are two functions available to create listeners. Both functions return a callable that cancels the listener.

async_listen_once - Listen once for the event and never fire again
async_listen - Listen until canceled
It's a rare case that async_listen is used since EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STARTED, and EVENT_HOMEASSISTANT_STOP are only ever fired once per run.

Async context
cancel = hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, disconnect_service)
cancel()


cancel = hass.bus.async_listen(EVENT_STATE_CHANGED, forward_event)
cancel()

Sync context
cancel = hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, disconnect_service)
cancel()


cancel = hass.bus.listen(EVENT_STATE_CHANGED, forward_event)
cancel()

Common events
The below events are commonly listened to directly.

Event Name	Description
EVENT_HOMEASSISTANT_START	Completed the setup and entered the start phase
EVENT_HOMEASSISTANT_STARTED	Completed the start phase, and all integrations have had a chance to load; Mostly used by voice assistants and integrations that export states to external services
EVENT_HOMEASSISTANT_STOP	Entered the stop phase
Other events
These events are rarely listened to directly unless the integration is part of the core. Often there is a helper available that consumes these events, and in that case, they should not be listened for directly.

Event Name	Description	Preferred helper
EVENT_HOMEASSISTANT_FINAL_WRITE	The last opportunity to write data to disk	
EVENT_HOMEASSISTANT_CLOSE	Teardown	
EVENT_COMPONENT_LOADED	An integration has completed loading	homeassistant.helpers.start.async_at_start
EVENT_SERVICE_REGISTERED	A new service has been registered	
EVENT_SERVICE_REMOVED	A service has been removed	
EVENT_CALL_SERVICE	A service has been called	
EVENT_STATE_CHANGED	The state of an entity has changed	Tracking entity state changes
EVENT_THEMES_UPDATED	Themes have been updated	
EVENT_CORE_CONFIG_UPDATE	Core configuration has been updated	
EVENT_ENTITY_REGISTRY_UPDATED	The entity registry has been updated	Tracking entity registry changes


Networking and discovery
Some integrations may need to discover devices on the network via mDNS/Zeroconf, SSDP, or another method once they have been enabled. The primary use case is to find devices that do not have a known fixed IP Address or for integrations that can dynamically add and remove any number of compatible discoverable devices.

Home Assistant has built-in helpers to support mDNS/Zeroconf and SSDP. If your integration uses another discovery method that needs to determine which network interfaces to use to broadcast traffic, the Network integration provides a helper API to access the user's interface preferences.

mDNS/Zeroconf
Home Assistant uses the python-zeroconf package for mDNS support. As running multiple mDNS implementations on a single host is not recommended, Home Assistant provides internal helper APIs to access the running Zeroconf and AsyncZeroconf instances.

Before using these helpers, be sure to add zeroconf to dependencies in your integration's manifest.json

Obtaining the AsyncZeroconf object
from homeassistant.components import zeroconf

...
aiozc = await zeroconf.async_get_async_instance(hass)


Obtaining the Zeroconf object
from homeassistant.components import zeroconf

...
zc = await zeroconf.async_get_instance(hass)


Using the AsyncZeroconf and Zeroconf objects
python-zeroconf provides examples on how to use both objects examples.

SSDP
Home Assistant provides built-in discovery via SSDP.

Before using these helpers, be sure to add ssdp to dependencies in your integration's manifest.json

Obtaining the list of discovered devices
The list of discovered SSDP devices can be obtained using the following built-in helper APIs. The SSDP integration provides the following helper APIs to lookup existing SSDP discoveries from the cache: ssdp.async_get_discovery_info_by_udn_st, ssdp.async_get_discovery_info_by_st, ssdp.async_get_discovery_info_by_udn

Looking up a specific device
The ssdp.async_get_discovery_info_by_udn_st API returns a single discovery_info or None when provided an SSDP, UDN and ST.

from homeassistant.components import ssdp

...

discovery_info = await ssdp.async_get_discovery_info_by_udn_st(hass, udn, st)


Looking up devices by ST
If you want to look for a specific type of discovered devices, calling ssdp.async_get_discovery_info_by_st will return a list of all discovered devices that match the SSDP ST. The below example returns a list of discovery info for every Sonos player discovered on the network.

from homeassistant.components import ssdp

...

discovery_infos = await ssdp.async_get_discovery_info_by_st(hass, "urn:schemas-upnp-org:device:ZonePlayer:1")
for discovery_info in discovery_infos:
  ...



Looking up devices by UDN
If you want to see a list of the services provided by a specific UDN, calling ssdp.async_get_discovery_info_by_udn will return a list of all discovered devices that match the UPNP UDN.

from homeassistant.components import ssdp

...

discovery_infos = await ssdp.async_get_discovery_info_by_udn(hass, udn)
for discovery_info in discovery_infos:
  ...



Subscribing to SSDP discoveries
Some integrations may need to know when a device is discovered right away. The SSDP integration provides a registration API to receive callbacks when a new device is discovered that matches specific key values. The same format for ssdp in manifest.json is used for matching.

The function ssdp.async_register_callback is provided to enable this ability. The function returns a callback that will cancel the registration when called.

The below example shows registering to get callbacks when a Sonos player is seen on the network.

from homeassistant.components import ssdp

...

entry.async_on_unload(
    ssdp.async_register_callback(
        hass, _async_discovered_player, {"st": "urn:schemas-upnp-org:device:ZonePlayer:1"}
    )
)


The below example shows registering to get callbacks when the x-rincon-bootseq header is present.

from homeassistant.components import ssdp
from homeassistant.const import MATCH_ALL

...

entry.async_on_unload(
    ssdp.async_register_callback(
        hass, _async_discovered_player, {"x-rincon-bootseq": MATCH_ALL}
    )
)


Network
For integrations that use a discovery method that is not built-in and need to access the user's network adapter configuration, the following helper API should be used.

from homeassistant.components import network

...
adapters = await network.async_get_adapters(hass)

Example async_get_adapters data structure
[
    {   
        "auto": True,
        "default": False,
        "enabled": True,
        "ipv4": [],
        "ipv6": [
            {   
                "address": "2001:db8::",
                "network_prefix": 8,
                "flowinfo": 1,
                "scope_id": 1,
            }
        ],
        "name": "eth0",
    },
    {
        "auto": True,
        "default": False,
        "enabled": True,
        "ipv4": [{"address": "192.168.1.5", "network_prefix": 23}],
        "ipv6": [],
        "name": "eth1",
    },
    {
        "auto": False,
        "default": False,
        "enabled": False,
        "ipv4": [{"address": "169.254.3.2", "network_prefix": 16}],
        "ipv6": [],
        "name": "vtun0",
    },
]

Obtaining the IP Network from an adapter
from ipaddress import ip_network
from homeassistant.components import network

...

adapters = await network.async_get_adapters(hass)

for adapter in adapters:
    for ip_info in adapter["ipv4"]:
        local_ip = ip_info["address"]
        network_prefix = ip_info["network_prefix"]
        ip_net = ip_network(f"{local_ip}/{network_prefix}", False)

USB
The USB integration discovers new USB devices at startup, when the integrations page is accessed, and when they are plugged in if the underlying system has support for pyudev.

Checking if a specific adapter is plugged in
Call the async_is_plugged_in API to check if a specific adapter is on the system.

from homeassistant.components import usb

...

if not usb.async_is_plugged_in(hass, {"serial_number": "A1234", "manufacturer": "xtech"}):
   raise ConfigEntryNotReady("The USB device is missing")



Knowing when to look for new compatible USB devices
Call the async_register_scan_request_callback API to request a callback when new compatible USB devices may be available.

from homeassistant.components import usb
from homeassistant.core import callback

...

@callback
def _async_check_for_usb() -> None:
    """Check for new compatible bluetooth USB adapters."""

entry.async_on_unload(
    bluetooth.async_register_scan_request_callback(hass, _async_check_for_usb)
)


Development checklist
Before you commit any changes, check your work against these requirements:

All communication to external devices or services must be wrapped in an external Python library hosted on pypi.
The library must have source distribution packages available; it's not allowed to rely on packages that only have binary distribution packages.
Issue trackers must be enabled for external Python libraries that communicate with external devices or services.
If the library is mainly used for Home Assistant and you are a code owner of the integration, it is encouraged to use an issue template picker with links to Home Assistant Core Issues. For example: zwave-js-server-python - New Issue
New dependencies are added to requirements_all.txt (if applicable), using python3 -m script.gen_requirements_all
New codeowners are added to CODEOWNERS (if applicable), using python3 -m script.hassfest
The .strict-typing file is updated to include your code if it provides a fully type hinted source.
The code is formatted using Ruff (ruff format).
Documentation is developed for home-assistant.io
Visit the website documentation for more information about contributing to home-assistant.io.

Checklist for creating a component
A checklist of things to do when you're adding a new component.

info
Not all existing code follows the requirements in this checklist. This cannot be used as a reason to not follow them!

0. Common
Follow our Style guidelines
Use existing constants from const.py
Only add new constants to const.py if they are widely used. Otherwise keep them on components level
1. External requirements
Requirements have been added to manifest.json. The REQUIREMENTS constant is deprecated.
Requirement version must be pinned: "requirements": ['phue==0.8.1']
Each requirement meets the library requirements.
2. Configuration
Voluptuous schema present for configuration validation
Default parameters specified in voluptuous schema, not in setup(…)
Schema using as many generic config keys as possible from homeassistant.const
If your component has platforms, define a PLATFORM_SCHEMA instead of a CONFIG_SCHEMA.
If using a PLATFORM_SCHEMA to be used with EntityComponent, import base from homeassistant.helpers.config_validation
Never depend on users adding things to customize to configure behavior inside your component.
3. Component/platform communication
You can share data with your platforms by leveraging hass.data[DOMAIN].
If the component fetches data that causes its related platform entities to update, you can notify them using the dispatcher code in homeassistant.helpers.dispatcher.
4. Communication with devices/services
All API specific code has to be part of a third party library hosted on PyPi. Home Assistant should only interact with objects and not make direct calls to the API.

# bad
status = requests.get(url("/status"))
# good
from phue import Bridge

bridge = Bridge(...)
status = bridge.status()

Tutorial on publishing your own PyPI package

Other noteworthy resources for publishing python packages:
Cookiecutter Project
flit
Poetry

5. Make your pull request as small as possible
Keep a new integration to the minimum functionality needed for someone to get value out of the integration. This allows reviewers to sign off on smaller chunks of code one at a time, and lets us get your new integration/features in sooner. Pull requests containing large code dumps will not be a priority for review and may be closed.

Limit to a single platform
Do not add features not needed to directly support the single platform (such as custom service actions)
Do not mix clean-ups and new features in a single pull request.
Do not solve several issues in a single pull request.
Do not submit pull requests that depend on other work which is still unmerged.
It may be tempting to open a large PR when "modernizing" an integration that hasn't been touched in a while to take advantage of all the latest features available. The right approach is to break the features down into independent functional changes as best you can and to submit the PRs sequentially.

One strategy for handling sequential PRs is to create a branch for the next PR off the current PR's branch, which you can then start writing code against. This strategy is advantageous if you have split up the PRs such that one is dependent on the previous one since you are working off of the code that will be in dev once the PR is merged. If you add additional commits to the current PR because of changes/review feedback, you can rebase your next PR's branch and more easily incorporate any merge conflicts. Once your current PR has been merged, squash the commits from the current PR branch in the next PR branch and then rebase on dev. Then you can submit your next PR branch for review and rinse and repeat as needed.

6. Event names
Prefix component event names with the domain name. For example, use netatmo_person instead of person for the netatmo component. Please be mindful of the data structure as documented on our Data Science portal.

7. Tests
Strongly consider adding tests for your component to minimize future regressions.

Checklist for creating a platform
A checklist of things to do when you're adding a new platform.

info
Not all existing platforms follow the requirements in this checklist. This cannot be used as a reason to not follow them!

0. Common
Follow our Style guidelines
Use existing constants from const.py
Only add new constants to const.py if they are widely used. Otherwise keep them on platform level
Use CONF_MONITORED_CONDITIONS instead of CONF_MONITORED_VARIABLES
1. External requirements
Requirements have been added to manifest.json. The REQUIREMENTS constant is deprecated.
Requirement version should be pinned: "requirements": ['phue==0.8.1']
We no longer want requirements hosted on GitHub. Please upload to PyPi.
Each requirement meets the library requirements.
2. Configuration
If the platform can be set up directly, add a voluptuous schema for configuration validation
Voluptuous schema extends schema from component
(e.g., hue.light.PLATFORM_SCHEMA extends light.PLATFORM_SCHEMA)
Default parameters specified in voluptuous schema, not in setup_platform(...)
Your PLATFORM_SCHEMA should use as many generic config keys as possible from homeassistant.const
Never depend on users adding things to customize to configure behavior inside your platform.
import voluptuous as vol

from homeassistant.const import CONF_FILENAME, CONF_HOST
from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

CONF_ALLOW_UNREACHABLE = "allow_unreachable"
DEFAULT_UNREACHABLE = False

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_ALLOW_UNREACHABLE, default=DEFAULT_UNREACHABLE): cv.boolean,
        vol.Optional(CONF_FILENAME): cv.string,
    }
)


3. Setup platform
Verify that the passed in configuration (user/pass/host etc.) works.
Group your calls to `add_entities if possible.
If the platform adds extra actions, the format should be <domain of your integration>.<service action name>. So if your integration's domain is "awesome_sauce" and you are making a light platform, you would register service actions under the awesome_sauce domain. Make sure that your service actions verify permissions.
4. Entity
Extend the entity from the integration you're building a platform for.

from homeassistant.components.light import Light


class HueLight(Light):
    """Hue light component."""

Avoid passing in hass as a parameter to the entity. hass will be set on the entity when the entity is added to Home Assistant. This means you can access hass as self.hass inside the entity.

Do not call update() in constructor, use add_entities(devices, update_before_add=True) instead.

Do not do any I/O inside properties. Cache values inside update() instead.

When dealing with time, state and/or attributes should not contain relative time since something happened. Instead, it should store UTC timestamps.

Leverage the entity lifecycle callbacks to attach event listeners or clean up connections.

5. Communication with devices/services
All API specific code has to be part of a third party library hosted on PyPi. Home Assistant should only interact with objects and not make direct calls to the API.

# bad
status = requests.get(url("/status"))
# good
from phue import Bridge

bridge = Bridge(...)
status = bridge.status()

Tutorial on publishing your own PyPI package

Other noteworthy resources for publishing python packages:
Cookiecutter Project
flit
Poetry

Integration quality scale
The integration quality scale is a framework for Home Assistant to grade integrations based on user experience, features, code quality and developer experience. To grade this, the project has come up with a set of tiers, which all have their own meaning.

Scaled tiers
There are 4 scaled tiers, bronze, silver, gold, and platinum. To reach a tier, the integration must fulfill all rules of that tier and the tiers below.

These tiers are defined as follows.

🥉 Bronze
The bronze tier is the baseline standard and requirement for all new integrations. It meets the minimum requirements in code quality, functionality, and user experience. It complies with the fundamental expectations and provides a reliable foundation for users to interact with their devices and services.

The documentation provides guidelines for setting up the integration directly from the Home Assistant user interface.

From a technical perspective, this integration has been reviewed to comply with all baseline standards, which we require for all new integrations, including automated tests for setting up the integration.

The bronze tier has the following characteristics:

Can be easily set up through the UI.
The source code adheres to basic coding standards and development guidelines.
Automated tests that guard this integration can be configured correctly.
Offers basic end-user documentation that is enough to get users started step-by-step easily.
🥈 Silver
The silver tier builds upon the “Bronze” level by improving the reliability and robustness of integrations, ensuring a solid runtime experience. It ensures an integration handles errors properly, such as when authentication to a device or service fails, handles offline devices, and other errors.

The documentation for these integrations provides information on what is available in Home Assistant when this integration is used, as well as troubleshooting information when issues occur.

This integration has one or more active code owners who help maintain it to ensure the experience on this level lasts now and in the future.

The silver tier has the following characteristics:

Provides everything “Bronze” has.
Provides a stable user experience under various conditions.
Has one or more active code owners who help maintain the integration.
Correctly and automatically recover from connection errors or offline devices, without filling log files and without unnecessary messages.
Automatically triggers re-authentication if authentication with the device or service fails.
Offers detailed documentation of what the integration provides and instructions for troubleshooting issues.
🥇 Gold
The gold standard in integration user experience, providing extensive and comprehensive support for the integrated devices & services. A gold-tier integration aims to be user-friendly, fully featured, and accessible to a wider audience.

When possible, devices are automatically discovered for an easy and seamless setup, and their firmware/software can be directly updated from Home Assistant.

All provided devices and entities are named logically and fully translatable, and they have been properly categorized and enabled for long-term statistical use.

The documentation for these integrations is extensive, and primarily aimed toward end-users and understandable by non-technical consumers. Besides providing general information on the integration, the documentation provides possible example use cases, a list of compatible devices, a list of described entities the integration provides, and extensive descriptions and usage examples of available actions provided by the integration. The use of example automations, dashboards, available Blueprints, and links to additional external resources, is highly encouraged as well.

The integration provides means for debugging issues, including downloading diagnostic information and documenting troubleshooting instructions. If needed, the integration can be reconfigured via the UI.

From a technical perspective, the integration needs to have full automated test coverage of its codebase to ensure the set integration quality is maintained now and in the future.

All integrations that have devices in the Works with Home Assistant program are at least required to have this tier.

The gold tier has the following characteristics:

Provides everything “Silver” has.
Has the best end-user experience an integration can offer; streamlined and intuitive.
Can be automatically discovered, simplifying the integration setup.
Integration can be reconfigured and adjusted.
Supports translations.
Extensive documentation, aimed at non-technical users.
It supports updating the software/firmware of devices through Home Assistant when possible.
The integration has automated tests covering the entire integration.
Required level for integrations providing devices in the Works with Home Assistant program.
🏆 Platinum
Platinum is the highest tier an integration can reach, the epitome of quality within Home Assistant. It not only provides the best user experience but also achieves technical excellence by adhering to the highest standards, supreme code quality, and well-optimized performance and efficiency.

The platinum tier has the following characteristics:

Provides everything “Gold” has.
All source code follows all coding and Home Assistant integration standards and best practices and is fully typed with type annotations and clear code comments for better code clarity and maintenance.
A fully asynchronous integration code base ensures efficient operation.
Implements efficient data handling, reducing network and CPU usage.
Keeping track of the implemented rules
Integrations that are working towards a higher tier or have a tier, must add a quality_scale.yaml file to their integration. The purpose of this file is to keep track of the progress of the rules that have been implemented and to keep track of exempted rules and the reason for the exemption. An example of this file looks like this:

rules:
  config_flow: done
  docs_high_level_description:
    status: exempt
    comment: This integration does not connect to any device or service.


Adjusting the tier of an integration
Home Assistant encourages our contributors to get their integrations to the highest possible tier, to provide an excellent coding experience for our contributors and the best experience for our users.

When an integration reaches the minimum requirements for a certain tier, a contributor can open a pull request to adjust the scale for the integration. This request needs to be accompanied by the full checklist for each rule of scale (including all rules of lower tiers), demonstrating that it has met those requirements. The checklist can be found here.

Once the Home Assistant core team reviews and approves it, the integration will display the new tier as of the next major release of Home Assistant.

Besides upgrading an integration to a higher tier on the scale, it is also possible for an integration to be downgraded to a lower tier. This can, for example, happen when there is no longer an active integration code owner. In this specific example, the integration will be downgraded to “Bronze”, even if it otherwise fully complies with the “Platinum” tier.

Adjustments to rules contained in each tier
The world of IoT and all technologies used by Home Assistant are changing at a fast pace; not just in terms of what Home Assistant can support or do, but also in terms of the software on which Home Assistant is built. Home Assistant is pioneering the technology in the industry at a fast pace.

This also means that new insights and newly developed and adopted best practices will occur over time, resulting in new additions and improvements to the individual integration quality scale rules.

If a tier is adjusted, all integrations in that tier need to be re-evaluated and adjusted accordingly.

info
One exception to this is integrations that have devices that are part of the Works with Home Assistant program. Those integrations will be flagged as grandfathered into their existing tier.

Special tiers
There are also 4 special tiers that are used to integration that don't have a place on the scaled tier list. This is because they are either an internal part of core, they are not in core at all, or they don't meet the minimum requirements to be graded against the scaled tiers.

The special tiers are defined as follows.

❓ No score
These integrations can be set up through the Home Assistant user interface. The “No score” designation doesn’t imply that they are bad or buggy, instead, it indicates that they haven’t been assessed according to the quality scale or that they need some maintenance to reach the now-considered minimum “Bronze” standard.

The “No score” tier cannot be assigned to new integrations, as they are required to have at least a “Bronze” level when introduced. The Home Assistant project encourages the community to help update these integrations without a score to meet at least the “Bronze” level requirements.

Characteristics:

Not yet scored or lacks sufficient information for scoring.
Can be set up via the UI, but may need enhancements for a better experience.
May function correctly, but hasn’t been verified against current standards.
Documentation most often provides only basic setup steps.
🏠 Internal
This tier is assigned to integrations used internally by Home Assistant. These integrations provide basic components and building blocks for Home Assistant's core program or for other integrations to build on top of it.

Internal integrations are maintained by the Home Assistant project and subjected to strict architectural design procedures.

Characteristics:

Internal, built-in building blocks of the Home Assistant core program.
Provides building blocks for other integrations to use and build on top of.
Maintained by the Home Assistant project.
💾 Legacy
Legacy integrations are older integrations that have been part of Home Assistant for many years, possibly since its inception. They can only be configured through YAML files and often lack active maintainers (code owners). These integrations might be complex to set up and do not adhere to current/modern end-user expectations in their use and features.

The Home Assistant project encourages the community to help migrate these integrations to the UI and update them to meet modern standards, making these integrations accessible to everyone.

Characteristics:

Complex setup process; only configurable via YAML, without UI-based setup.
May lack active code ownership and maintenance.
Could be missing recent updates or bug fixes.
Documentation may still be aimed at developers.
📦 Custom
Custom integrations are developed and distributed by the community, and offer additional functionalities and support for devices and services to Home Assistant. These integrations are not included in the official Home Assistant releases and can be installed manually or via third-party tools like HACS (Home Assistant Community Store).

The Home Assistant project does not review, security audit, maintain, or support third-party custom integrations. Users are encouraged to exercise caution and review the custom integration’s source and community feedback before installation.

Developers are encouraged and invited to contribute their custom integration to the Home Assistant project by aligning them with the integration quality scale and submitting them for inclusion.

Characteristics:

Not included in the official Home Assistant releases.
Manually installable or installable via community tools, like HACS.
Maintained by individual developers or community members.
User experience may vary widely.
Functionality, security, and stability can vary widely.
Documentation may be limited.

Checklist
When changing the quality scale of an integration, make sure you have completed the rules before opening the PR to change the quality scale. In the PR description, please deliver a copy of this checklist and mark the rules that have been completed. Make sure you add links to the relevant code to help a speedy grading process.

## Bronze
- [ ] `action-setup` - Service actions are registered in async_setup
- [ ] `appropriate-polling` - If it's a polling integration, set an appropriate polling interval
- [ ] `brands` - Has branding assets available for the integration
- [ ] `common-modules` - Place common patterns in common modules
- [ ] `config-flow-test-coverage` - Full test coverage for the config flow
- [ ] `config-flow` - Integration needs to be able to be set up via the UI
    - [ ] Uses `data_description` to give context to fields
    - [ ] Uses `ConfigEntry.data` and `ConfigEntry.options` correctly
- [ ] `dependency-transparency` - Dependency transparency
- [ ] `docs-actions` - The documentation describes the provided service actions that can be used
- [ ] `docs-high-level-description` - The documentation includes a high-level description of the integration brand, product, or service
- [ ] `docs-installation-instructions` - The documentation provides step-by-step installation instructions for the integration, including, if needed, prerequisites
- [ ] `docs-removal-instructions` - The documentation provides removal instructions
- [ ] `entity-event-setup` - Entity events are subscribed in the correct lifecycle methods
- [ ] `entity-unique-id` - Entities have a unique ID
- [ ] `has-entity-name` - Entities use has_entity_name = True
- [ ] `runtime-data` - Use ConfigEntry.runtime_data to store runtime data
- [ ] `test-before-configure` - Test a connection in the config flow
- [ ] `test-before-setup` - Check during integration initialization if we are able to set it up correctly
- [ ] `unique-config-entry` - Don't allow the same device or service to be able to be set up twice

## Silver
- [ ] `action-exceptions` - Service actions raise exceptions when encountering failures
- [ ] `config-entry-unloading` - Support config entry unloading
- [ ] `docs-configuration-parameters` - The documentation describes all integration configuration options
- [ ] `docs-installation-parameters` - The documentation describes all integration installation parameters
- [ ] `entity-unavailable` - Mark entity unavailable if appropriate
- [ ] `integration-owner` - Has an integration owner
- [ ] `log-when-unavailable` - If internet/device/service is unavailable, log once when unavailable and once when back connected
- [ ] `parallel-updates` - Number of parallel updates is specified
- [ ] `reauthentication-flow` - Reauthentication needs to be available via the UI
- [ ] `test-coverage` - Above 95% test coverage for all integration modules

## Gold
- [ ] `devices` - The integration creates devices
- [ ] `diagnostics` - Implements diagnostics
- [ ] `discovery-update-info` - Integration uses discovery info to update network information
- [ ] `discovery` - Devices can be discovered
- [ ] `docs-data-update` - The documentation describes how data is updated
- [ ] `docs-examples` - The documentation provides automation examples the user can use.
- [ ] `docs-known-limitations` - The documentation describes known limitations of the integration (not to be confused with bugs)
- [ ] `docs-supported-devices` - The documentation describes known supported / unsupported devices
- [ ] `docs-supported-functions` - The documentation describes the supported functionality, including entities, and platforms
- [ ] `docs-troubleshooting` - The documentation provides troubleshooting information
- [ ] `docs-use-cases` - The documentation describes use cases to illustrate how this integration can be used
- [ ] `dynamic-devices` - Devices added after integration setup
- [ ] `entity-category` - Entities are assigned an appropriate EntityCategory
- [ ] `entity-device-class` - Entities use device classes where possible
- [ ] `entity-disabled-by-default` - Integration disables less popular (or noisy) entities
- [ ] `entity-translations` - Entities have translated names
- [ ] `exception-translations` - Exception messages are translatable
- [ ] `icon-translations` - Entities implement icon translations
- [ ] `reconfiguration-flow` - Integrations should have a reconfigure flow
- [ ] `repair-issues` - Repair issues and repair flows are used when user intervention is needed
- [ ] `stale-devices` - Stale devices are removed

## Platinum
- [ ] `async-dependency` - Dependency is async
- [ ] `inject-websession` - The integration dependency supports passing in a websession
- [ ] `strict-typing` - Strict typing

Integration quality scale rules
The rules for each tier are defined down below and come with its own page with examples and more information.

🥉 Bronze
action-setup - Service actions are registered in async_setup
appropriate-polling - If it's a polling integration, set an appropriate polling interval
brands - Has branding assets available for the integration
common-modules - Place common patterns in common modules
config-flow-test-coverage - Full test coverage for the config flow
config-flow - Integration needs to be able to be set up via the UI
dependency-transparency - Dependency transparency
docs-actions - The documentation describes the provided service actions that can be used
docs-high-level-description - The documentation includes a high-level description of the integration brand, product, or service
docs-installation-instructions - The documentation provides step-by-step installation instructions for the integration, including, if needed, prerequisites
docs-removal-instructions - The documentation provides removal instructions
entity-event-setup - Entity events are subscribed in the correct lifecycle methods
entity-unique-id - Entities have a unique ID
has-entity-name - Entities use has_entity_name = True
runtime-data - Use ConfigEntry.runtime_data to store runtime data
test-before-configure - Test a connection in the config flow
test-before-setup - Check during integration initialization if we are able to set it up correctly
unique-config-entry - Don't allow the same device or service to be able to be set up twice
🥈 Silver
action-exceptions - Service actions raise exceptions when encountering failures
config-entry-unloading - Support config entry unloading
docs-configuration-parameters - The documentation describes all integration configuration options
docs-installation-parameters - The documentation describes all integration installation parameters
entity-unavailable - Mark entity unavailable if appropriate
integration-owner - Has an integration owner
log-when-unavailable - If internet/device/service is unavailable, log once when unavailable and once when back connected
parallel-updates - Number of parallel updates is specified
reauthentication-flow - Reauthentication needs to be available via the UI
test-coverage - Above 95% test coverage for all integration modules
🥇 Gold
devices - The integration creates devices
diagnostics - Implements diagnostics
discovery-update-info - Integration uses discovery info to update network information
discovery - Devices can be discovered
docs-data-update - The documentation describes how data is updated
docs-examples - The documentation provides automation examples the user can use.
docs-known-limitations - The documentation describes known limitations of the integration (not to be confused with bugs)
docs-supported-devices - The documentation describes known supported / unsupported devices
docs-supported-functions - The documentation describes the supported functionality, including entities, and platforms
docs-troubleshooting - The documentation provides troubleshooting information
docs-use-cases - The documentation describes use cases to illustrate how this integration can be used
dynamic-devices - Devices added after integration setup
entity-category - Entities are assigned an appropriate EntityCategory
entity-device-class - Entities use device classes where possible
entity-disabled-by-default - Integration disables less popular (or noisy) entities
entity-translations - Entities have translated names
exception-translations - Exception messages are translatable
icon-translations - Entities implement icon translations
reconfiguration-flow - Integrations should have a reconfigure flow
repair-issues - Repair issues and repair flows are used when user intervention is needed
stale-devices - Stale devices are removed
🏆 Platinum
async-dependency - Dependency is async
inject-websession - The integration dependency supports passing in a websession
strict-typing - Strict typing

Hass object
While developing Home Assistant you will see a variable that is everywhere: hass. This is the Home Assistant instance that will give you access to all the various parts of the system.

The hass object
The Home Assistant instance contains four objects to help you interact with the system.

Object	Description
hass	This is the instance of Home Assistant. Allows starting, stopping and enqueuing new jobs.
hass.config	This is the core configuration of Home Assistant exposing location, temperature preferences and config directory path.
hass.states	This is the StateMachine. It allows you to set states and track when they are changed. See available methods.
hass.bus	This is the EventBus. It allows you to trigger and listen for events. See available methods.
hass.services	This is the ServiceRegistry. It allows you to register service actions. See available methods.
Overview of the Home Assistant core architecture
Where to find hass
Depending on what you're writing, there are different ways the hass object is made available.

Component Passed into setup(hass, config) or async_setup(hass, config).

Platform Passed into setup_platform(hass, config, add_entities, discovery_info=None) or async_setup_platform(hass, config, async_add_entities, discovery_info=None).

Entity Available as self.hass once the entity has been added via the add_entities callback inside a platform.

Events
The core of Home Assistant is driven by events. That means that if you want to respond to something happening, you'll have to respond to events. Most of the times you won't interact directly with the event system but use one of the event listener helpers.

The event system is very flexible. There are no limitations on the event type, as long as it's a string. Each event can contain data. The data is a dictionary that can contain any data as long as it's JSON serializable. This means that you can use number, string, dictionary and list.

List of events that Home Assistant fires.

Firing events
To fire an event, you have to interact with the event bus. The event bus is available on the Home Assistant instance as hass.bus. Please be mindful of the data structure as documented on our Data Science portal.

Example component that will fire an event when loaded. Note that custom event names are prefixed with the component name.

DOMAIN = "example_component"


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    # Fire event example_component_my_cool_event with event data answer=42
    hass.bus.fire("example_component_my_cool_event", {"answer": 42})

    # Return successful setup
    return True


Listening to events
Most of the times you'll not be firing events but instead listen to events. For example, the state change of an entity is broadcasted as an event.

DOMAIN = "example_component"


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    count = 0

    # Listener to handle fired events
    def handle_event(event):
        nonlocal count
        count += 1
        print(f"Answer {count} is: {event.data.get('answer')}")

    # Listen for when example_component_my_cool_event is fired
    hass.bus.listen("example_component_my_cool_event", handle_event)

    # Return successful setup
    return True


Helpers
Home Assistant comes with a lot of bundled helpers to listen to specific types of event. There are helpers to track a point in time, to track a time interval, a state change or the sun set. See available methods.

States
Home Assistant keeps track of the states of entities in a state machine. The state machine has very few requirements:

Each state is related to an entity identified by an entity id. This id is made up of a domain and an object id. For example light.kitchen_ceiling. You can make up any combination of domain and object id, even overwriting existing states.
Each state has a primary attribute that describes the state of the entity. In the case of a light this could be for example "on" and "off". You can store anything you want in the state, as long as it's a string (will be converted if it's not).
You can store more information about an entity by setting attributes. Attributes is a dictionary that can contain any data that you want. The only requirement is that it's JSON serializable, so you're limited to numbers, strings, dictionaries and lists.
Description of the state object.

Using states in your component
This is a simple tutorial/example on how to create and set states. We will do our work in a component called "hello_state". The purpose of this component is to display a given text in the frontend.

To get started, create the file <config dir>/custom_components/hello_state.py and copy the below example code.

"""
Support for showing text in the frontend.

For more details about this component, please refer to the documentation at
https://developers.home-assistant.io/docs/dev_101_states
"""
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "hello_state"


def setup(hass, config):
    """Setup the Hello State component. """
    _LOGGER.info("The 'hello state' component is ready!")

    return True


In the file header we decided to add some details: A short description and the link to the documentation.

We want to do some logging. This means that we import the Python logging module and create an alias.

The component name is equal to the domain name.

The setup function will take care of the initialization of our component. The component will only write a log message. Keep in mind for later that you have several options for the severity:

_LOGGER.info(msg)
_LOGGER.warning(msg)
_LOGGER.error(msg)
_LOGGER.critical(msg)
_LOGGER.exception(msg)
We return True if everything is ok.

Add the component to your configuration.yaml file.

hello_state:

After a start or a restart of Home Assistant the component will create an entry in the log.

16-03-12 14:16:42 INFO (MainThread) [custom_components.hello_state] The 'hello state' component is ready!


The next step is the introduction of configuration options. A user can pass configuration options to our component via configuration.yaml. To use them we'll use the passed in config variable to our setup method.

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "hello_state"

CONF_TEXT = "text"
DEFAULT_TEXT = "No text!"


def setup(hass, config):
    """Set up the Hello State component. """
    # Get the text from the configuration. Use DEFAULT_TEXT if no name is provided.
    text = config[DOMAIN].get(CONF_TEXT, DEFAULT_TEXT)

    # States are in the format DOMAIN.OBJECT_ID
    hass.states.set("hello_state.Hello_State", text)

    return True


To use the latest feature of our component, update the entry in your configuration.yaml file.

hello_state:
  text: 'Hello, World!'

Thanks to DEFAULT_TEXT variable the component will launch even if no text: field is used in the configuration.yaml file. Quite often there are variables which are required. It's important to check if all mandatory configuration variables are provided. If not, the setup should fail. We will use voluptuous as a helper to achieve this. The next listing shows the essential parts.

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Required(CONF_TEXT): cv.string,})}, extra=vol.ALLOW_EXTRA
)


Now, when text: is missing from the config, Home Assistant will alert the user and not setup your component.

After a start or a restart of Home Assistant the component will be visible in the frontend if the configuration.yaml file is up-to-date.



In order to expose attributes for a platform, you will need to define a property called extra_state_attributes on the entity class, which will return a dictionary of attributes:

@property
def extra_state_attributes(self):
    """Return entity specific state attributes."""
    return self._attributes

tip
Entities also have a similar property state_attributes, which should not be overridden by integrations. This property is used by base entity components to add standard sets of attributes to a state. Example: The light component uses state_attributes to add brightness to the state dictionary. If you are designing a new integration, you should define extra_state_attributes instead.

To get your integration included in the Home Assistant releases, follow the steps described in the Submit your work section. Basically you only need to move your integration into the homeassistant/component/ directory of your fork and create a Pull Request.

Config
On the hass object there is an instance of the Config class. The Config class contains the users preferred units, the path to the config directory and which components are loaded.

Name	Type	Description
latitude	float	Latitude of the instance location
longitude	float	Longitude of the instance location
elevation	int	Elevation of the instance
location_name	str	Name of the instance
time_zone	str	Timezone
units	UnitSystem	Unit system
internal_url	str	URL the instance can be reached on internally
external_url	str	URL the instance can be reached on externally
currency	str	Preferred currency
country	str	Country the instance is in
language	str	Preferred language
config_source	ConfigSource	If the configuration was set via the UI or stored in YAML
skip_pip	bool	If True, pip install is skipped for requirements on startup
skip_pip_packages	list[str]	List of packages to skip when installing requirements on startup
components	set[str]	List of loaded components
api	ApiConfig	API (HTTP) server configuration
config_dir	str	Directory that holds the configuration
allowlist_external_dirs	set[str]	List of allowed external dirs to access
allowlist_external_urls	set[str]	List of allowed external URLs that integrations may use
media_dirs	dict[str, str]	Dictionary of Media folders that integrations may use
safe_mode	bool	If Home Assistant is running in safe mode
legacy_templates	bool	Use legacy template behavior
It also provides some helper methods.

Entity
For a generic introduction of entities, see entities architecture.

Basic implementation
Below is an example switch entity that keeps track of its state in memory. In addition, the switch in the example represents the main feature of a device, meaning the entity has the same name as its device.

Please refer to Entity naming for how to give an entity its own name.

from homeassistant.components.switch import SwitchEntity


class MySwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self):
        self._is_on = False
        self._attr_device_info = ...  # For automatic device registration
        self._attr_unique_id = ...

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False


That's all there is to it to build a switch entity! Continue reading to learn more or check out the video tutorial.

Updating the entity
An entity represents a device. There are various strategies to keep your entity in sync with the state of the device, the most popular one being polling.

Polling
With polling, Home Assistant will ask the entity from time to time (depending on the update interval of the component) to fetch the latest state. Home Assistant will poll an entity when the should_poll property returns True (the default value). You can either implement your update logic using update() or the async method async_update(). This method should fetch the latest state from the device and store it in an instance variable for the properties to return it.

Subscribing to updates
When you subscribe to updates, your code is responsible for letting Home Assistant know that an update is available. Make sure you have the should_poll property return False.

Whenever you receive a new state from your subscription, you can tell Home Assistant that an update is available by calling schedule_update_ha_state() or async callback async_schedule_update_ha_state(). Pass in the boolean True to the method if you want Home Assistant to call your update method before writing the update to Home Assistant.

Generic properties
The entity base class has a few properties common among all Home Assistant entities. These properties can be added to any entity regardless of the type. All these properties are optional and don't need to be implemented.

These properties are always called when the state is written to the state machine.

tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Because these properties are always called when the state is written to the state machine, it is important to do as little work as possible in the property.

To avoid calculations in a property method, set the corresponding entity class or instance attribute, or if the values never change, use entity descriptions.

Name	Type	Default	Description
assumed_state	bool	False	Return True if the state is based on our assumption instead of reading it from the device.
attribution	str | None	None	The branding text required by the API provider.
available	bool	True	Indicate if Home Assistant is able to read the state and control the underlying device.
device_class	str | None	None	Extra classification of what the device is. Each domain specifies their own. Device classes can come with extra requirements for unit of measurement and supported features.
entity_picture	str | None	None	Url of a picture to show for the entity.
extra_state_attributes	dict | None	None	Extra information to store in the state machine. It needs to be information that further explains the state, it should not be static information like firmware version.
has_entity_name	bool	False	Return True if the entity's name property represents the entity itself (required for new integrations). This is explained in more detail below.
name	str | None	None	Name of the entity. Avoid hard coding a natural language name, use a translated name instead.
should_poll	bool	True	Should Home Assistant check with the entity for an updated state. If set to False, entity will need to notify Home Assistant of new updates by calling one of the schedule update methods.
state	str | int | float | None	None	The state of the entity. In most cases this is implemented by the domain base entity and should not be implemented by integrations.
supported_features	int | None	None	Flag features supported by the entity. Domains specify their own.
translation_key	str | None	None	A key for looking up translations of the entity's state in entity section of the integration's strings.json and for translating the state into a matching icon.
translation_placeholders	dict | None	None	Placeholder definitions for translated entity name.
warning
It's allowed to change device_class, supported_features or any property included in a domain's capability_attributes. However, since these entity properties often are not expected to change at all and some entity consumers may not be able to update them at a free rate, we recommend only changing them when absolutely required and at a modest interval.

As an example, such changes will cause voice assistant integrations to resynchronize with the supporting cloud service.

warning
Entities that generate a significant amount of state changes can quickly increase the size of the database when the extra_state_attributes also change frequently. Minimize the number of extra_state_attributes for these entities by removing non-critical attributes or creating additional sensor entities.

Registry properties
The following properties are used to populate the entity and device registries. They are read each time the entity is added to Home Assistant. These properties only have an effect if unique_id is not None.

Name	Type	Default	Description
device_info	DeviceInfo | None	None	Device registry descriptor for automatic device registration.
entity_category	EntityCategory | None	None	Classification of a non-primary entity. Set to EntityCategory.CONFIG for an entity that allows changing the configuration of a device, for example, a switch entity, making it possible to turn the background illumination of a switch on and off. Set to EntityCategory.DIAGNOSTIC for an entity exposing some configuration parameter or diagnostics of a device but does not allow changing it, for example, a sensor showing RSSI or MAC address.
entity_registry_enabled_default	bool	True	Indicate if the entity should be enabled or disabled when first added to the entity registry. This includes fast-changing diagnostic entities or, assumingly less commonly used entities. For example, a sensor exposing RSSI or battery voltage should typically be set to False; to prevent unneeded (recorded) state changes or UI clutter by these entities.
entity_registry_visible_default	bool	True	Indicate if the entity should be hidden or visible when first added to the entity registry.
unique_id	str | None	None	A unique identifier for this entity. It must be unique within a platform (like light.hue). It should not be configurable or changeable by the user. Learn more.
Advanced properties
The following properties are also available on entities. However, they are for advanced use only and should be used with caution. These properties are always called when the state is written to the state machine.

Name	Type	Default	Description
capability_attributes	dict | None	None	State attributes which are stored in the entity registry. This property is implemented by the domain base entity and should not be implemented by integrations.
force_update	bool	False	Write each update to the state machine, even if the data is the same. Example use: when you are directly reading the value from a connected sensor instead of a cache. Use with caution, will spam the state machine.
icon	str | None	None	Icon to use in the frontend. Using this property is not recommended. More information about using icons.
state_attributes	dict | None	None	State attributes of a base domain. This property is implemented by the domain base entity and should not be implemented by integrations.
unit_of_measurement	str | None	The unit of measurement that the entity's state is expressed in. In most cases, for example for the number and sensor domains, this is implemented by the domain base entity and should not be implemented by integrations.	
System properties
The following properties are used and controlled by Home Assistant, and should not be overridden by integrations.

Name	Type	Default	Description
enabled	bool	True	Indicate if entity is enabled in the entity registry. It also returns True if the platform doesn't support the entity registry. Disabled entities will not be added to Home Assistant.
Entity naming
Avoid setting an entity's name to a hard coded English string, instead, the name should be translated. Examples of when the name should not be translated are proper nouns, model names, and name provided by a 3rd-party library.

Some entities are automatically named after their device class, this includes binary_sensor, button, number and sensor entities and in many cases don't need to be named. For example, an unnamed sensor which has its device class set to temperature will be named "Temperature".

has_entity_name True (Mandatory for new integrations)
The entity's name property only identifies the data point represented by the entity, and should not include the name of the device or the type of the entity. So for a sensor that represents the power usage of its device, this would be “Power usage”.

If the entity represents a single main feature of a device the entity should typically have its name property return None. The "main feature" of a device would for example be the LightEntity of a smart light bulb.

The friendly_name state attribute is generated by combining then entity name with the device name as follows:

The entity is not a member of a device: friendly_name = entity.name
The entity is a member of a device and entity.name is not None: friendly_name = f"{device.name} {entity.name}"
The entity is a member of a device and entity.name is None: friendly_name = f"{device.name}"
Entity names should start with a capital letter, the rest of the words are lower case (unless it's a proper noun or a capitalized abbreviation of course).

Example of a switch entity which is the main feature of a device
Note: The example is using class attributes to implement properties, for other ways to implement properties see Property implementation. *Note: The example is incomplete, the unique_id property must be implemented, and the entity must be registered with a device.

from homeassistant.components.switch import SwitchEntity


class MySwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = None


Example of a switch entity which is either not the main feature of a device, or is not part of a device:
Note: The example is using class attributes to implement properties, for other ways to implement properties see Property implementation. *Note: If the entity is part of a device, the unique_id property must be implemented, and the entity must be registered with a device.

from homeassistant.components.switch import SwitchEntity


class MySwitch(SwitchEntity):
    _attr_has_entity_name = True

    @property
    def translation_key(self):
        """Return the translation key to translate the entity's name and states."""
        return my_switch


Example of an untranslated switch entity which is either not the main feature of a device, or is not part of a device:
from homeassistant.components.switch import SwitchEntity


class MySwitch(SwitchEntity):
    _attr_has_entity_name = True

    @property
    def name(self):
        """Name of the entity."""
        return "Model X"

has_entity_name not implemented or False (Deprecated)
The entity's name property may be a combination of the device name and the data point represented by the entity.

Property implementation
Property function
Writing property methods for each property is just a couple of lines of code, for example

class MySwitch(SwitchEntity):

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:door"

    ...

Entity class or instance attributes
Alternatively, a shorter form is to set Entity class or instance attributes according to either of the following patterns:

class MySwitch(SwitchEntity):

    _attr_icon = "mdi:door"

    ...

class MySwitch(SwitchEntity):

    def __init__(self, icon: str) -> None:
        self._attr_icon = icon

    ...

This does exactly the same as the first example but relies on a default implementation of the property in the base class. The name of the attribute starts with _attr_ followed by the property name. For example, the default device_class property returns the _attr_device_class class attribute.

Not all entity classes support the _attr_ attributes for their entity specific properties, please refer to the documentation for the respective entity class for details.

tip
If an integration needs to access its own properties it should access the property (self.name), not the class or instance attribute (self._attr_name).

Entity description
The third way of setting entity properties is to use an entity description. To do this set an attribute named entity_description on the Entity instance with an EntityDescription instance. The entity description is a dataclass with attributes corresponding to most of the available Entity properties. Each entity integration that supports an entity platform, eg the switch integration, will define their own EntityDescription subclass that should be used by implementing platforms that want to use entity descriptions.

By default the EntityDescription instance has one required attribute named key. This is a string which is meant to be unique for all the entity descriptions of an implementing platform. A common use case for this attribute is to include it in the unique_id of the described entity.

The main benefit of using entity descriptions is that it defines the different entity types of a platform in a declarative manner, making the code much easier to read when there are many different entity types.

Example
The below code snippet gives an example of best practices for when to implement property functions, when to use class or instance attributes and when to use entity descriptions.

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from example import ExampleDevice, ExampleException

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, LOGGER


@dataclass(kw_only=True)
class ExampleSensorEntityDescription(SensorEntityDescription):
    """Describes Example sensor entity."""

    exists_fn: Callable[[ExampleDevice], bool] = lambda _: True
    value_fn: Callable[[ExampleDevice], StateType]


SENSORS: tuple[ExampleSensorEntityDescription, ...] = (
    ExampleSensorEntityDescription(
        key="estimated_current",
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.power,
        exists_fn=lambda device: bool(device.max_power),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Example sensor based on a config entry."""
    device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ExampleSensorEntity(device, description)
        for description in SENSORS
        if description.exists_fn(device)
    )


class ExampleSensorEntity(SensorEntity):
    """Represent an Example sensor."""

    entity_description: ExampleSensorEntityDescription
    _attr_entity_category = (
        EntityCategory.DIAGNOSTIC
    )  # This will be common to all instances of ExampleSensorEntity

    def __init__(
        self, device: ExampleDevice, entity_description: ExampleSensorEntityDescription
    ) -> None:
        """Set up the instance."""
        self._device = device
        self.entity_description = entity_description
        self._attr_available = False  # This overrides the default
        self._attr_unique_id = f"{device.serial}_{entity_description.key}"

    def update(self) -> None:
        """Update entity state."""
        try:
            self._device.update()
        except ExampleException:
            if self.available:  # Read current state, no need to prefix with _attr_
                LOGGER.warning("Update failed for %s", self.entity_id)
            self._attr_available = False  # Set property value
            return

        self._attr_available = True
        # We don't need to check if device available here
        self._attr_native_value = self.entity_description.value_fn(
            self._device
        )  # Update "native_value" property


Lifecycle hooks
Use these lifecycle hooks to execute code when certain events happen to the entity. All lifecycle hooks are async methods.

async_added_to_hass()
Called when an entity has their entity_id and hass object assigned, before it is written to the state machine for the first time. Example uses: restore the state, subscribe to updates or set callback/dispatch function/listener.

async_will_remove_from_hass()
Called when an entity is about to be removed from Home Assistant. Example use: disconnect from the server or unsubscribe from updates.

Icons
Every entity in Home Assistant has an icon, which is used as a visual indicator to identify the entity more easily in the frontend. Home Assistant uses the Material Design Icons icon set.

In most cases, Home Assistant will pick an icon automatically based on the entity's domain, device_class, and state. It is preferred to use the default icon if possible, to provide a consistent experience and to avoid confusion for the user. However, it is possible to override the default and provide a custom icon for an entity.

Regardless of the provided icon, it is always possible for the user to customize the icon to their liking in the frontend.

There are two ways to provide a custom icon for an entity, either by providing icon translations or by providing an icon identifier.

Icon translations
This is the preferred way to provide a custom icon for an entity. Icon translations work similarly to our regular translations, but instead of translating the state of an entity, they translate the states of an entity to icons.

The translation_key property of an entity defines the icon translation to use. This property is used to look up the translation in the entity section of the integration's icons.json file.

To differentiate entities and their translations, provide different translation keys. The following example shows icons.json for a Moon domain sensor entity with its translation_key property set to phase:

{
  "entity": {
    "sensor": {
      "phase": {
        "default": "mdi:moon",
        "state": {
          "new_moon": "mdi:moon-new",
          "first_quarter": "mdi:moon-first-quarter",
          "full_moon": "mdi:moon-full",
          "last_quarter": "mdi:moon-last-quarter"
        }
      }
    }
  }
}

Notice that icons start with mdi: plus an identifier. The default icon is used when the entity's state is not in the state section. The state section is optional, and if not provided, the default icon will be used for all states.

Icons for entity state attributes can also be provided in cases where the frontend shows icons for the state attributes. Examples include climate presets and fan modes. It's not possible to provide icons for other state attributes. The following example provides icons for a climate entity with its translation_key property set to ubercool. This entity has a preset_mode state attribute, which can be set to vacation or night. The frontend will use these in, for example, the climate card.

{
  "entity": {
    "climate": {
      "ubercool": {
        "state_attributes": {
          "preset_mode": {
            "default": "mdi:confused",
            "state": {
              "vacation": "mdi:umbrella-beach",
              "night": "mdi:weather-night"
            }
          }
        }
      }
    }
  }
}

Icon property
Another way to provide an icon for an entity is by setting the icon property of an entity, which returns a string referencing the mdi icon. As this property is a method, it is possible to return different icons based on custom logic unlike with icon translations. For example, it's possible to calculate the icon based on the state as in the example below, or return different icons based on something that is not part of the entity's state.

class MySwitch(SwitchEntity):

    @property
    def icon(self) -> str | None:
        """Icon of the entity, based on time."""
        if now().hour < 12:
            return "mdi:weather-night"
        return "mdi:weather-sunny"

    ...

It is not possible to provide icons for state attributes using the icon property. Please note that using the icon property is discouraged; using the above-mentioned icon translations is preferred.

Excluding state attributes from recorder history
State attributes which are not suitable for state history recording should be excluded from state history recording by including them in either of _entity_component_unrecorded_attributes or _unrecorded_attributes.

_entity_component_unrecorded_attributes: frozenset[str] may be set in a base component class, e.g. in light.LightEntity
_unrecorded_attributes: frozenset[str] may be set in an integration's platform e.g. in an entity class defined in platform hue.light.
The MATCH_ALL constant can be used to exclude all attributes instead of typing them separately. This can be useful for integrations providing unknown attributes or when you simply want to exclude all without typing them separately.

Using the MATCH_ALL constant does not stop recording for device_class, state_class, unit_of_measurement, and friendly_name as they might also serve other purposes and, therefore, should not be excluded from recording.

Examples of platform state attributes which are exluded from recording include the entity_picture attribute of image entities which will not be valid after some time, the preset_modes attribute of fan entities which is not likely to change. Examples of integration specific state attributes which are excluded from recording include description and location state attributes in platform trafikverket.camera which do not change.

tip
The _entity_component_unrecorded_attributes and _unrecorded_attributes must be declared as class attributes; instance attributes will be ignored.

Changing the entity model
If you want to add a new feature to an entity or any of its subtypes (light, switch, etc), you will need to propose it first in our architecture repo. Only additions will be considered that are common features among various vendors.

Binary sensor entity
A binary sensor is a sensor that can only have two states. Derive entity platforms from homeassistant.components.binary_sensor.BinarySensorEntity

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
is_on	bool | None	None	Required. If the binary sensor is currently on or off.
device_class	BinarySensorDeviceClass | None	None	Type of binary sensor.
Available device classes
Constant	Description
BinarySensorDeviceClass.BATTERY	On means low, Off means normal.
BinarySensorDeviceClass.BATTERY_CHARGING	On means charging, Off means not charging.
BinarySensorDeviceClass.CO	On means carbon monoxide detected, Off means no carbon monoxide (clear).
BinarySensorDeviceClass.COLD	On means cold, Off means normal.
BinarySensorDeviceClass.CONNECTIVITY	On means connected, Off means disconnected.
BinarySensorDeviceClass.DOOR	On means open, Off means closed.
BinarySensorDeviceClass.GARAGE_DOOR	On means open, Off means closed.
BinarySensorDeviceClass.GAS	On means gas detected, Off means no gas (clear).
BinarySensorDeviceClass.HEAT	On means hot, Off means normal.
BinarySensorDeviceClass.LIGHT	On means light detected, Off means no light.
BinarySensorDeviceClass.LOCK	On means open (unlocked), Off means closed (locked).
BinarySensorDeviceClass.MOISTURE	On means wet, Off means dry.
BinarySensorDeviceClass.MOTION	On means motion detected, Off means no motion (clear).
BinarySensorDeviceClass.MOVING	On means moving, Off means not moving (stopped).
BinarySensorDeviceClass.OCCUPANCY	On means occupied, Off means not occupied (clear).
BinarySensorDeviceClass.OPENING	On means open, Off means closed.
BinarySensorDeviceClass.PLUG	On means plugged in, Off means unplugged.
BinarySensorDeviceClass.POWER	On means power detected, Off means no power.
BinarySensorDeviceClass.PRESENCE	On means home, Off means away.
BinarySensorDeviceClass.PROBLEM	On means problem detected, Off means no problem (OK).
BinarySensorDeviceClass.RUNNING	On means running, Off means not running.
BinarySensorDeviceClass.SAFETY	On means unsafe, Off means safe.
BinarySensorDeviceClass.SMOKE	On means smoke detected, Off means no smoke (clear).
BinarySensorDeviceClass.SOUND	On means sound detected, Off means no sound (clear).
BinarySensorDeviceClass.TAMPER	On means tampering detected, Off means no tampering (clear)
BinarySensorDeviceClass.UPDATE	On means update available, Off means up-to-date. The use of this device class should be avoided, please consider using the update entity instead.
BinarySensorDeviceClass.VIBRATION	On means vibration detected, Off means no vibration.
BinarySensorDeviceClass.WINDOW	On means open, Off means closed.

Device tracker entity
A device tracker is a read-only entity that provides presence information. There are two types of device tracker entities, a ScannerEntity and a TrackerEntity.

ScannerEntity
A ScannerEntity reports the connected state of a device on the local network. If the device is connected the ScannerEntity will have state home and if the device is not connected the state will be not_home.

Derive a platform entity from homeassistant.components.device_tracker.config_entry.ScannerEntity

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
battery_level	int | None	None	The battery level of the device.
hostname	str | None	None	The hostname of the device.
ip_address	str | None	None	The IP address of the device.
is_connected	bool	Required	The connection state of the device.
mac_address	str | None	None	The MAC address of the device.
source_type	SourceType	SourceType.ROUTER	The source type of the device.
DHCP discovery
If the device tracker source_type is router and the ip_address, mac_address, and hostname properties have been set, the data will speed up DHCP discovery as the system will not have to wait for DHCP discover packets to find existing devices.

TrackerEntity
A TrackerEntity tracks the location of a device and reports it either as a location name, a zone name or home or not_home states. A TrackerEntity normally receives GPS coordinates to determine its state. Either location_name or latitude and longitude should be set to report state.

Derive a platform entity from homeassistant.components.device_tracker.config_entry.TrackerEntity

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
battery_level	int | None	None	The battery level of the device.
latitude	float | None	None	The latitude coordinate of the device.
location_accuracy	float	0	The location accuracy (m) of the device.
location_name	str | None	None	The location name of the device.
longitude	float | None	None	The longitude coordinate of the device.
source_type	SourceType	SourceType.GPS	The source type of the device.


Event entity
Events are signals that are emitted when something happens, for example, when a user presses a physical button like a doorbell or when a button on a remote control is pressed. The event entity captures these events in the physical world and makes them available in Home Assistant as an entity.

An event entity is derived from the homeassistant.components.event.EventEntity.

States
The event entity is stateless, meaning you don't have to maintain a state. Instead, you can trigger an event when something in the physical world happens. Home Assistant will keep track of the last event that was emitted and will show that as the current state of the entity.

The main state of the entity is the timestamp of when the last event was emitted, additionally the type of the event and optionally extra state data that was provided with the event are also kept track of.

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
event_types	list[str]	Required	A list of possible event types this entity can fire.
Other properties that are common to all entities such as device_class, icon, name etc are also applicable.

Firing events
The event entity is a little different compared to other entities. Home Assistant manages the state, but the integration is responsible for firing the events. This is done by calling the _trigger_event method on the event entity.

This method takes the event type as the first argument and optionally extra state data as the second argument.

class MyEvent(EventEntity):

    _attr_device_class = EventDeviceClass.BUTTON
    _attr_event_types = ["single_press", "double_press"]

    @callback
    def _async_handle_event(self, event: str) -> None:
        """Handle the demo button event."""
        self._trigger_event(event, {"extra_data": 123})
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register callbacks with your device API/library."""
        my_device_api.listen(self._async_handle_event)

Only event types that are defined in the event_types property can be fired. If an event type is fired that is not defined in the event_types property, a ValueError will be raised.

tip
Be sure to deregister any callbacks when the entity is removed from Home Assistant.

Available device classes
Optionally specifies what type of entity it is.

Constant	Description
EventDeviceClass.BUTTON	A button of a remote control has been pressed.
EventDeviceClass.DOORBELL	Specifically for buttons that are used as a doorbell.
EventDeviceClass.MOTION	For motion events detected by a motion sensor.

Notify entity
A notify entity is an entity that can send a message towards a device or service but remains stateless from the Home Assistant perspective.

A notify entity is derived from the homeassistant.components.notify.NotifyEntity, and can be helpful to send notification messages as (but not limited to):

an SMS
an email
a direct message or chat
a screen message on a device's LCD display
States
The state of a notify entity is a timestamp, representing the date and time of the last message sent. Unlike a text entity, the notify entity has no state that can be set.

If you want to represent something that has a text value that can be changed (and thus has an actual state), you should use a text entity instead.

Properties
As this integration is stateless, it doesn't provide any specific properties for itself. Other properties that are common to all entities such as icon and name etc are still applicable.

Methods
Send message
The send message method is used to send a message to a device or service.

class MyNotifier(NotifyEntity):
    # Implement one of these methods.

    def send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""


Select entity
A select is an entity that allows the user to select an option from a list of limited options provided by the integration. Derive entity platforms from homeassistant.components.select.SelectEntity

This entity should only be used in cases there is no better fitting option available. For example, a bulb can have user selectable light effects. While that could be done using this select entity, it should really be part of the light entity, which already supports light effects.

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
current_option	str	None	The current select option
options	list	Required	A list of available options as strings
Other properties that are common to all entities such as icon, unit_of_measurement, name etc are also applicable.

Methods
Select option
Called when the user or automation wants to change the current selected option.

class MySelect(SelectEntity):
    # Implement one of these methods.

    def select_option(self, option: str) -> None:
        """Change the selected option."""

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""


Sensor entity
A sensor is a read-only entity that provides some information. Information has a value and optionally, a unit of measurement. Derive entity platforms from homeassistant.components.sensor.SensorEntity

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
device_class	SensorDeviceClass | None	None	Type of sensor.
last_reset	datetime.datetime | None	None	The time when an accumulating sensor such as an electricity usage meter, gas meter, water meter etc. was initialized. If the time of initialization is unknown, set it to None. Note that the datetime.datetime returned by the last_reset property will be converted to an ISO 8601-formatted string when the entity's state attributes are updated. When changing last_reset, the state must be a valid number.
native_unit_of_measurement	str | None	None	The unit of measurement that the sensor's value is expressed in. If the native_unit_of_measurement is °C or °F, and its device_class is temperature, the sensor's unit_of_measurement will be the preferred temperature unit configured by the user and the sensor's state will be the native_value after an optional unit conversion. If a unit translation is provided, native_unit_of_measurement should not be defined.
native_value	str | int | float | date | datetime | Decimal | None	Required	The value of the sensor in the sensor's native_unit_of_measurement. Using a device_class may restrict the types that can be returned by this property.
options	list[str] | None	None	In case this sensor provides a textual state, this property can be used to provide a list of possible states. Requires the enum device class to be set. Cannot be combined with state_class or native_unit_of_measurement.
state_class	SensorStateClass | str | None	None	Type of state. If not None, the sensor is assumed to be numerical and will be displayed as a line-chart in the frontend instead of as discrete values.
suggested_display_precision	int | None	None	The number of decimals which should be used in the sensor's state when it's displayed.
suggested_unit_of_measurement	str | None	None	The unit of measurement to be used for the sensor's state. For sensors with a unique_id, this will be used as the initial unit of measurement, which users can then override. For sensors without a unique_id, this will be the unit of measurement for the sensor's state. This property is intended to be used by integrations to override automatic unit conversion rules, for example, to make a temperature sensor always display in °C regardless of whether the configured unit system prefers °C or °F, or to make a distance sensor always display in miles even if the configured unit system is metric.
tip
Instead of adding extra_state_attributes for a sensor entity, create an additional sensor entity. Attributes that do not change are only saved in the database once. If extra_state_attributes and the sensor value both frequently change, this can quickly increase the size of the database.

Available device classes
If specifying a device class, your sensor entity will need to also return the correct unit of measurement.

Constant	Supported units	Description
SensorDeviceClass.APPARENT_POWER	VA	Apparent power
SensorDeviceClass.AQI	None	Air Quality Index
SensorDeviceClass.AREA	m², cm², km², mm², in², ft², yd², mi², ac, ha	Area
SensorDeviceClass.ATMOSPHERIC_PRESSURE	cbar, bar, hPa, mmHG, inHg, kPa, mbar, Pa, psi	Atmospheric pressure
SensorDeviceClass.BATTERY	%	Percentage of battery that is left
SensorDeviceClass.BLOOD_GLUCOSE_CONCENTRATION	mg/dL, mmol/L	Blood glucose concentration
SensorDeviceClass.CO2	ppm	Concentration of carbon dioxide.
SensorDeviceClass.CO	ppm	Concentration of carbon monoxide.
SensorDeviceClass.CONDUCTIVITY	S/cm, mS/cm, µS/cm	Conductivity
SensorDeviceClass.CURRENT	A, mA	Current
SensorDeviceClass.DATA_RATE	bit/s, kbit/s, Mbit/s, Gbit/s, B/s, kB/s, MB/s, GB/s, KiB/s, MiB/s, GiB/s	Data rate
SensorDeviceClass.DATA_SIZE	bit, kbit, Mbit, Gbit, B, kB, MB, GB, TB, PB, EB, ZB, YB, KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB	Data size
SensorDeviceClass.DATE		Date. Requires native_value to be a Python datetime.date object, or None.
SensorDeviceClass.DISTANCE	km, m, cm, mm, mi, nmi, yd, in	Generic distance
SensorDeviceClass.DURATION	d, h, min, s, ms, µs	Time period. Should not update only due to time passing. The device or service needs to give a new data point to update.
SensorDeviceClass.ENERGY	J, kJ, MJ, GJ, mWh, Wh, kWh, MWh, GWh, TWh, cal, kcal, Mcal, Gcal	Energy, this device class should be used for sensors representing energy consumption, for example an electricity meter. Represents power over time. Not to be confused with power.
SensorDeviceClass.ENERGY_DISTANCE	kWh/100km, Wh/km, mi/kWh, km/kWh	Energy per distance, this device class should be used to represent energy consumption by distance, for example the amount of electric energy consumed by an electric car.
SensorDeviceClass.ENERGY_STORAGE	J, kJ, MJ, GJ, mWh, Wh, kWh, MWh, GWh, TWh, cal, kcal, Mcal, Gcal	Stored energy, this device class should be used for sensors representing stored energy, for example the amount of electric energy currently stored in a battery or the capacity of a battery. Represents power over time. Not to be confused with power.
SensorDeviceClass.ENUM		The sensor has a limited set of (non-numeric) states. The options property must be set to a list of possible states when using this device class.
SensorDeviceClass.FREQUENCY	Hz, kHz, MHz, GHz	Frequency
SensorDeviceClass.GAS	L, m³, ft³, CCF	Volume of gas. Gas consumption measured as energy in kWh instead of a volume should be classified as energy.
SensorDeviceClass.HUMIDITY	%	Relative humidity
SensorDeviceClass.ILLUMINANCE	lx	Light level
SensorDeviceClass.IRRADIANCE	W/m², BTU/(h⋅ft²)	Irradiance
SensorDeviceClass.MOISTURE	%	Moisture
SensorDeviceClass.MONETARY	ISO 4217	Monetary value with a currency.
SensorDeviceClass.NITROGEN_DIOXIDE	µg/m³	Concentration of nitrogen dioxide
SensorDeviceClass.NITROGEN_MONOXIDE	µg/m³	Concentration of nitrogen monoxide
SensorDeviceClass.NITROUS_OXIDE	µg/m³	Concentration of nitrous oxide
SensorDeviceClass.OZONE	µg/m³	Concentration of ozone
SensorDeviceClass.PH	None	Potential hydrogen (pH) of an aqueous solution
SensorDeviceClass.PM1	µg/m³	Concentration of particulate matter less than 1 micrometer
SensorDeviceClass.PM25	µg/m³	Concentration of particulate matter less than 2.5 micrometers
SensorDeviceClass.PM10	µg/m³	Concentration of particulate matter less than 10 micrometers
SensorDeviceClass.POWER	mW, W, kW, MW, GW, TW	Power.
SensorDeviceClass.POWER_FACTOR	%, None	Power Factor
SensorDeviceClass.PRECIPITATION	cm, in, mm	Accumulated precipitation
SensorDeviceClass.PRECIPITATION_INTENSITY	in/d, in/h, mm/d, mm/h	Precipitation intensity
SensorDeviceClass.PRESSURE	cbar, bar, hPa, mmHg, inHg, kPa, mbar, Pa, psi	Pressure.
SensorDeviceClass.REACTIVE_ENERGY	varh, kvarh	Reactive energy
SensorDeviceClass.REACTIVE_POWER	var, kvar	Reactive power
SensorDeviceClass.SIGNAL_STRENGTH	dB, dBm	Signal strength
SensorDeviceClass.SOUND_PRESSURE	dB, dBA	Sound pressure
SensorDeviceClass.SPEED	ft/s, in/d, in/h, in/s, km/h, kn, m/s, mph, mm/d, mm/s	Generic speed
SensorDeviceClass.SULPHUR_DIOXIDE	µg/m³	Concentration of sulphure dioxide
SensorDeviceClass.TEMPERATURE	°C, °F, K	Temperature.
SensorDeviceClass.TIMESTAMP		Timestamp. Requires native_value to return a Python datetime.datetime object, with time zone information, or None.
SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS	µg/m³, mg/m³	Concentration of volatile organic compounds
SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS	ppm, ppb	Ratio of volatile organic compounds
SensorDeviceClass.VOLTAGE	V, mV, µV, kV, MV	Voltage
SensorDeviceClass.VOLUME	L, mL, gal, fl. oz., m³, ft³, CCF	Generic volume, this device class should be used for sensors representing a consumption, for example the amount of fuel consumed by a vehicle.
SensorDeviceClass.VOLUME_FLOW_RATE	m³/h, m³/s, ft³/min, L/h, L/min, L/s, gal/min, mL/s	Volume flow rate, this device class should be used for sensors representing a flow of some volume, for example the amount of water consumed momentarily.
SensorDeviceClass.VOLUME_STORAGE	L, mL, gal, fl. oz., m³, ft³, CCF	Generic stored volume, this device class should be used for sensors representing a stored volume, for example the amount of fuel in a fuel tank.
SensorDeviceClass.WATER	L, gal, m³, ft³, CCF	Water consumption
SensorDeviceClass.WEIGHT	kg, g, mg, µg, oz, lb, st	Generic mass; weight is used instead of mass to fit with every day language.
SensorDeviceClass.WIND_DIRECTION	°	Wind direction, should be set to None if the wind speed is 0 or too low to accurately measure the wind direction.
SensorDeviceClass.WIND_SPEED	ft/s, km/h, kn, m/s, mph	Wind speed
Available state classes
caution
Choose the state class for a sensor with care. In most cases, state class SensorStateClass.MEASUREMENT or state class SensorStateClass.TOTAL without last_reset should be chosen, this is explained further in How to choose state_class and last_reset below.

Type	Description
SensorStateClass.MEASUREMENT	The state represents a measurement in present time, not a historical aggregation such as statistics or a prediction of the future. Examples of what should be classified SensorStateClass.MEASUREMENT are: current temperature, humidity or electric power. Examples of what should not be classified as SensorStateClass.MEASUREMENT: Forecasted temperature for tomorrow, yesterday's energy consumption or anything else that doesn't include the current measurement. For supported sensors, statistics of hourly min, max and average sensor readings is updated every 5 minutes.
SensorStateClass.MEASUREMENT_ANGLE	Similar to the above SensorStateClass.MEASUREMENT, the state represents a measurement in present time for angles measured in degrees (°). An example of what should be classified SensorStateClass.MEASUREMENT_ANGLE is current wind direction
SensorStateClass.TOTAL	The state represents a total amount that can both increase and decrease, e.g. a net energy meter. Statistics of the accumulated growth or decline of the sensor's value since it was first added is updated every 5 minutes. This state class should not be used for sensors where the absolute value is interesting instead of the accumulated growth or decline, for example remaining battery capacity or CPU load; in such cases state class SensorStateClass.MEASUREMENT should be used instead.
SensorStateClass.TOTAL_INCREASING	Similar to SensorStateClass.TOTAL, with the restriction that the state represents a monotonically increasing positive total which periodically restarts counting from 0, e.g. a daily amount of consumed gas, weekly water consumption or lifetime energy consumption. Statistics of the accumulated growth of the sensor's value since it was first added is updated every 5 minutes. A decreasing value is interpreted as the start of a new meter cycle or the replacement of the meter.
Entity options
Sensors can be configured by the user, this is done by storing sensor entity options in the sensor's entity registry entry.

Option	Description
unit_of_measurement	The sensor's unit of measurement can be overridden for sensors with device class SensorDeviceClass.PRESSURE or SensorDeviceClass.TEMPERATURE.
Restoring sensor states
Sensors which restore the state after restart or reload should not extend RestoreEntity because that does not store the native_value, but instead the state which may have been modified by the sensor base entity. Sensors which restore the state should extend RestoreSensor and call await self.async_get_last_sensor_data from async_added_to_hass to get access to the stored native_value and native_unit_of_measurement.

Long-term Statistics
Home Assistant has support for storing sensors as long-term statistics if the entity has the right properties. To opt-in for statistics, the sensor must have state_class set to one of the valid state classes: SensorStateClass.MEASUREMENT, SensorStateClass.TOTAL or SensorStateClass.TOTAL_INCREASING. For certain device classes, the unit of the statistics is normalized to for example make it possible to plot several sensors in a single graph.

Entities not representing a total amount
Home Assistant tracks the min, max and mean value during the statistics period. The state_class property must be set to SensorStateClass.MEASUREMENT, and the device_class must not be either of SensorDeviceClass.DATE, SensorDeviceClass.ENUM, SensorDeviceClass.ENERGY, SensorDeviceClass.GAS, SensorDeviceClass.MONETARY, SensorDeviceClass.TIMESTAMP, SensorDeviceClass.VOLUME or SensorDeviceClass.WATER.

Entities representing a total amount
Entities tracking a total amount have a value that may optionally reset periodically, like this month's energy consumption, today's energy production, the weight of pellets used to heat the house over the last week or the yearly growth of a stock portfolio. The sensor's value when the first statistics is compiled is used as the initial zero-point.

How to choose state_class and last_reset
It's recommended to use state class SensorStateClass.TOTAL without last_reset whenever possible, state class SensorStateClass.TOTAL_INCREASING or SensorStateClass.TOTAL with last_reset should only be used when state class SensorStateClass.TOTAL without last_reset does not work for the sensor.

Examples:

The sensor's value never resets, e.g. a lifetime total energy consumption or production: state_class SensorStateClass.TOTAL, last_reset not set or set to None
The sensor's value may reset to 0, and its value can only increase: state class SensorStateClass.TOTAL_INCREASING. Examples: energy consumption aligned with a billing cycle, e.g. monthly, an energy meter resetting to 0 every time it's disconnected
The sensor's value may reset to 0, and its value can both increase and decrease: state class SensorStateClass.TOTAL, last_reset updated when the value resets. Examples: net energy consumption aligned with a billing cycle, e.g. monthly.
The sensor's state is reset with every state update, for example a sensor updating every minute with the energy consumption during the past minute: state class SensorStateClass.TOTAL, last_reset updated every state change.
State class SensorStateClass.TOTAL
For sensors with state class SensorStateClass.TOTAL, the last_reset attribute can optionally be set to gain manual control of meter cycles. The sensor's state when it's first added to Home Assistant is used as an initial zero-point. When last_reset changes, the zero-point will be set to 0. If last_reset is not set, the sensor's value when it was first added is used as the zero-point when calculating sum statistics.

To put it in another way: the logic when updating the statistics is to update the sum column with the difference between the current state and the previous state unless last_reset has been changed, in which case don't add anything.

Example of state class SensorStateClass.TOTAL without last_reset:

t	state	sum	sum_increase	sum_decrease
2021-08-01T13:00:00	1000	0	0	0
2021-08-01T14:00:00	1010	10	10	0
2021-08-01T15:00:00	0	-1000	10	1010
2021-08-01T16:00:00	5	-995	15	1010
Example of state class SensorStateClass.TOTAL with last_reset:

t	state	last_reset	sum	sum_increase	sum_decrease
2021-08-01T13:00:00	1000	2021-08-01T13:00:00	0	0	0
2021-08-01T14:00:00	1010	2021-08-01T13:00:00	10	10	0
2021-08-01T15:00:00	1005	2021-08-01T13:00:00	5	10	5
2021-08-01T16:00:00	0	2021-09-01T16:00:00	5	10	5
2021-08-01T17:00:00	5	2021-09-01T16:00:00	10	15	5
Example of state class SensorStateClass.TOTAL where the initial state at the beginning of the new meter cycle is not 0, but 0 is used as zero-point:

t	state	last_reset	sum	sum_increase	sum_decrease
2021-08-01T13:00:00	1000	2021-08-01T13:00:00	0	0	0
2021-08-01T14:00:00	1010	2021-08-01T13:00:00	10	10	0
2021-08-01T15:00:00	1005	2021-08-01T13:00:00	5	10	5
2021-08-01T16:00:00	5	2021-09-01T16:00:00	10	15	5
2021-08-01T17:00:00	10	2021-09-01T16:00:00	15	20	5
State class SensorStateClass.TOTAL_INCREASING
For sensors with state_class SensorStateClass.TOTAL_INCREASING, a decreasing value is interpreted as the start of a new meter cycle or the replacement of the meter. It is important that the integration ensures that the value cannot erroneously decrease in the case of calculating a value from a sensor with measurement noise present. There is some tolerance, a decrease between state changes of < 10% will not trigger a new meter cycle. This state class is useful for gas meters, electricity meters, water meters etc. The value when the sensor reading decreases will not be used as zero-point when calculating sum statistics, instead the zero-point will be set to 0.

To put it in another way: the logic when updating the statistics is to update the sum column with the difference between the current state and the previous state unless the difference is negative, in which case don't add anything.

Example of state class SensorStateClass.TOTAL_INCREASING:

t	state	sum
2021-08-01T13:00:00	1000	0
2021-08-01T14:00:00	1010	10
2021-08-01T15:00:00	0	10
2021-08-01T16:00:00	5	15
Example of state class SensorStateClass.TOTAL_INCREASING where the sensor does not reset to 0:

t	state	sum
2021-08-01T13:00:00	1000	0
2021-08-01T14:00:00	1010	10
2021-08-01T15:00:00	5	15
2021-08-01T16:00:00	10	20

Text entity
A text entity is an entity that allows the user to input a text value to an integration. Derive entity platforms from homeassistant.components.text.TextEntity

Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data or build a mechanism to push state updates to the entity class instance.

Name	Type	Default	Description
mode	string	text	Defines how the text should be displayed in the UI. Can be text or password.
native_max	int	100	The maximum number of characters in the text value (inclusive).
native_min	int	0	The minimum number of characters in the text value (inclusive).
pattern	str	None	A regex pattern that the text value must match to be valid.
native_value	str	Required	The value of the text.
Other properties that are common to all entities such as icon, name etc are also applicable.

Methods
Set value
class MyTextEntity(TextEntity):
    # Implement one of these methods.

    def set_value(self, value: str) -> None:
        """Set the text value."""

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""

Update entity
An update entity is an entity that indicates if an update is available for a device or service. This can be any update, including update of a firmware for a device like a light bulb or router, or software updates for things like add-ons or containers.

It can be used for:

Providing an indicator if an update is available for a device or service.
An install method to allow installing an update or a specific version of the software.
Allow for offering backups before installing a new update.
Properties
tip
Properties should always only return information from memory and not do I/O (like network requests). Implement update() or async_update() to fetch data.

Name	Type	Default	Description
auto_update	bool	False	The device or service that the entity represents has auto update logic. When this is set to True you can not skip updates.
display_precision	int	0	Number of decimal digits for display of update progress.
in_progress	bool	None	Update installation progress. Should return a boolean (True if in progress, False if not).
installed_version	str	None	The currently installed and used version of the software.
latest_version	str	None	The latest version of the software available.
release_summary	str	None	Summary of the release notes or changelog. This is not suitable for long changelogs but merely suitable for a short excerpt update description of max 255 characters.
release_url	str	None	URL to the full release notes of the latest version available.
title	str	None	Title of the software. This helps to differentiate between the device or entity name versus the title of the software installed.
update_percentage	int, float	None	Update installation progress. Can either return a number to indicate the progress from 0 to 100% or None.
Other properties that are common to all entities such as device_class, entity_category, icon, name etc are still applicable.

Supported features
Supported features are defined by using values in the UpdateEntityFeature enum.

Value	Description
'BACKUP'	A backup can be made automatically, before installing an update.
'INSTALL'	The update can be installed from Home Assistant.
'PROGRESS'	This integration is able to provide progress information. If omitted, Home Assistant will try to provide a progress status; although it is better if the progress can be extracted from the device or service API.
'SPECIFIC_VERSION'	A specific version of an update can be installed using the update.install service action.
'RELEASE_NOTES'	The entity provides methods to fetch a complete changelog.
Methods
Compare versions
This method should be implemented when needed to override the default version comparison logic. Here's an example:

def version_is_newer(self, latest_version: str, installed_version: str) -> bool:
    """Return True if latest_version is newer than installed_version."""
    return AwesomeVersion(
        latest_version,
        find_first_match=True,
        ensure_strategy=[AwesomeVersionStrategy.SEMVER],
    ) > AwesomeVersion(
        installed_version,
        find_first_match=True,
        ensure_strategy=[AwesomeVersionStrategy.SEMVER],
    )


It allows developers to specify custom logic for determining if one version is newer than another. First attempt should be based on the strategies provided by the AwesomeVersion library.

Install
This method can be implemented so users can install an offered update directly from within Home Assistant.

This method requires UpdateEntityFeature.INSTALL to be set. Additionally, if this integration supports installing specific version or is capable of backing up before starting the update installation process, UpdateEntityFeature.SPECIFIC_VERSION and UpdateEntityFeature.BACKUP can be set respectively.

class MyUpdate(UpdateEntity):
    # Implement one of these methods.

    def install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update."""

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update.

        Version can be specified to install a specific version. When `None`, the
        latest version needs to be installed.

        The backup parameter indicates a backup should be taken before
        installing the update.
        """


Release notes
This method can be implemented so users can can get the full release notes in the more-info dialog of the Home Assistant Frontend before they install the update.

The returned string can contain markdown, and the frontend will format that correctly.

This method requires UpdateEntityFeature.RELEASE_NOTES to be set.

class MyUpdate(UpdateEntity):
    # Implement one of these methods.

    def release_notes(self) -> str | None:
        """Return the release notes."""
        return "Lorem ipsum"

    async def async_release_notes(self) -> str | None:
        """Return the release notes."""
        return "Lorem ipsum"

Available device classes
Optionally specifies what type of entity it is.

Constant	Description
UpdateDeviceClass.FIRMWARE	The update is a firmware update for a device.

Entities: integrating devices & services
Integrations can represent devices & services in Home Assistant. The data points are represented as entities. Entities are standardized by other integrations like light, switch, etc. Standardized entities come with actions for control, but an integration can also provide their own service actions in case something is not standardized.

An entity abstracts away the internal workings of Home Assistant. As an integrator, you don't have to worry about how service actions or the state machine work. Instead, you extend an entity class and implement the necessary properties and methods for the device type that you're integrating.

Integrating devices & services
Configuration is provided by the user via a Config Entry or in special/legacy cases via configuration.yaml.

The device integration (i.e. hue) will use this configuration to set up a connection with the device/service. It will forward the config entry (legacy uses discovery helper) to set up its entities in their respective integrations (light, switch). The device integration can also register their own service actions for things that are not made standardized. These actions are published under the integration's domain, ie hue.activate_scene.

The entity integration (i.e. light) is responsible for defining the abstract entity class and services to control the entities.

The Entity Component helper is responsible for distributing the configuration to the platforms, forward discovery and collect entities for service calls.

The Entity Platform helper manages all entities for the platform and polls them for updates if necessary. When adding entities, the Entity Platform is responsible for registering the entity with the device and entity registries.

Integration Platform (i.e. hue.light) uses configuration to query the external device/service and create entities to be added. It is also possible for integration platforms to register entity services. These services will work on all entities of the device integration for the entity integration (i.e. all Hue light entities). These services are published under the device integration domain.

Entity interaction with Home Assistant Core
The integration entity class that inherits from the entity base class is responsible for fetching the data and handle the service calls. If polling is disabled, it is also responsible for telling Home Assistant when data is available.

Entities interacting with core
The entity base class (defined by the entity integration) is responsible for formatting the data and writing it to the state machine.

The entity registry will write an unavailable state for any registered entity that is not currently backed by an entity object.

Entity data hierarchy
Entity hierarchy
Delete, disable or re-enable any object and all objects below will be adjusted accordingly.

Entity registry
The entity registry is a registry where Home Assistant keeps track of entities. Any entity that is added to Home Assistant which specifies the unique_id attribute will be registered in the registry.

Being registered has the advantage that the same entity will always get the same entity ID. It will also prevent other entities from using that entity ID.

A user is also able to override the name of an entity in the entity registry. When set, the name in the entity registry is used in favor of the name the device might give itself.

Unique ID
It is important that it is not possible for the user to change the unique ID, because the system would lose all its settings related to the unique ID.

An entity is looked up in the registry based on a combination of the platform type (e.g., light), and the integration name (domain) (e.g. hue) and the unique ID of the entity. Entities should not include the domain (e.g., your_integration) and platform type (e.g., light) in their Unique ID as the system already accounts for these identifiers.

If a device has a single unique id but provides multiple entities, combine the unique id with unique identifiers for the entities. For example, if a device measures both temperature and humidity, you can uniquely identify the entities using {unique_id}-{sensor_type}.

Unique ID requirements
Example acceptable sources for a unique ID
Serial number of a device
MAC address: formatted using homeassistant.helpers.device_registry.format_mac; Only obtain the MAC address from the device API or a discovery handler. Tools that rely on reading the arp cache or local network access such as getmac will not function in all supported network environments and are not acceptable.
Latitude and Longitude or other unique Geo Location
Unique identifier that is physically printed on the device or burned into an EEPROM
Unique ID of last resort
For entities that are setup by a config entry, the Config Entry ID can be used as a last resort if no other Unique ID is available.

Unacceptable sources for a unique ID
IP Address
Device Name
Hostname
URL
Email addresses
Usernames

Entity registry and disabling entities
The entity registry tracks all entities with unique IDs. For each entity, the registry keeps track of options that impact how the entity interacts with the core. One of these options is disabled_by.

When disabled_by is set and not None, the entity will not be added to Home Assistant when the integration passes it to async_add_entities.

Integration architecture
Integrations will need to make sure that they work correctly when their entities get disabled. If your integration is keeping references to the created entity objects, it should register those references only inside the entity's lifecycle method async_added_to_hass. This lifecycle method is only called if the entity is actually added to Home Assistant (and so it's not disabled).

Entity disabling works with entities provided via a config entry or via an entry in configuration.yaml. If your integration is set up via a config entry and supports unloading, Home Assistant will be able to reload your integration after entities have been enabled/disabled to apply the changes without a restart.

Users editing the entity registry
One way an entity can be disabled is by the user editing the entity registry via the UI. In this case, the disabled_by value will be set to RegistryEntryDisabler.USER. This will only work with entities that are already registered.

Integrations setting default value of disabled_by for new entity registry entries
As an integration you can control if your entity is enabled when it is first registered. This is controlled by the entity_registry_enabled_default property. It defaults to True, which means the entity will be enabled.

If the property returns False, the disabled_by value of the newly registered entity will be set to RegistryEntryDisabler.INTEGRATION.

Config entry system options setting default value of disabled_by for new entity registry entries
The user can also control how new entities that are related to a config entry are received by setting the system option disable_new_entities of a config entry to True. This can be done via the UI.

If an entity is getting registered and this system option is set to True, the disabled_by property will be initialized as RegistryEntryDisabler.CONFIG_ENTRY.

If disable_new_entities is set to True and entity_registry_enabled_default returns False, the disabled_by value will be set to RegistryEntryDisabler.INTEGRATION.

Integrations offering options to control disabled_by
Some integrations will want to offer options to the user to control which entities are being added to Home Assistant. For example, the Unifi integration offers options to enable/disable wireless and wired clients.

Integrations can offer options to users either via configuration.yaml or using an Options Flow.

If this option is offered by integrations, you should not leverage the disabled_by property in the entity registry. Instead, if entities are disabled via a config options flow, remove them from the device and entity registry.

Device registry
The device registry is a registry where Home Assistant keeps track of devices. A device is represented in Home Assistant via one or more entities. For example, a battery-powered temperature and humidity sensor might expose entities for temperature, humidity and battery level.

Device registry overview
What is a device?
A device in Home Assistant represents either a physical device that has its own control unit, or a service. The control unit itself does not have to be smart, but it should be in control of what happens. For example, an Ecobee thermostat with 4 room sensors equals 5 devices in Home Assistant, one for the thermostat including all sensors inside it, and one for each room sensor. Each device exists in a specific geographical area, and may have more than one input or output within that area.

If you connect a sensor to another device to read some of its data, it should still be represented as two different devices. The reason for this is that the sensor could be moved to read the data of another device.

A device that offers multiple endpoints, where parts of the device sense or output in different areas, should be split into separate devices and refer back to parent device with the via_device attribute. This allows the separate endpoints to be assigned to different areas in the building.

info
Although not currently available, we could consider offering an option to users to merge devices.

Device properties
Attribute	Description
area_id	The Area which the device is placed in.
config_entries	Config entries that are linked to this device.
configuration_url	A URL on which the device or service can be configured, linking to paths inside the Home Assistant UI can be done by using homeassistant://<path>.
connections	A set of tuples of (connection_type, connection identifier). Connection types are defined in the device registry module. Each item in the set uniquely defines a device entry, meaning another device can't have the same connection.
default_manufacturer	The manufacturer of the device, will be overridden if manufacturer is set. Useful for example for an integration showing all devices on the network.
default_model	The model of the device, will be overridden if model is set. Useful for example for an integration showing all devices on the network.
default_name	Default name of this device, will be overridden if name is set. Useful for example for an integration showing all devices on the network.
entry_type	The type of entry. Possible values are None and DeviceEntryType enum members (only service).
hw_version	The hardware version of the device.
id	Unique ID of device (generated by Home Assistant)
identifiers	Set of (DOMAIN, identifier) tuples. Identifiers identify the device in the outside world. An example is a serial number. Each item in the set uniquely defines a device entry, meaning another device can't have the same identifier.
name	Name of this device
name_by_user	The user configured name of the device.
manufacturer	The manufacturer of the device.
model	The model name of the device.
model_id	The model identifier of the device.
serial_number	The serial number of the device. Unlike a serial number in the identifiers set, this does not need to be unique.
suggested_area	The suggested name for the area where the device is located.
sw_version	The firmware version of the device.
via_device	Identifier of a device that routes messages between this device and Home Assistant. Examples of such devices are hubs, or parent devices of a sub-device. This is used to show device topology in Home Assistant.
Defining devices
Automatic registration through an entity
tip
Entity device info is only read if the entity is loaded via a config entry and the unique_id property is defined.

Each entity is able to define a device via the device_info property. This property is read when an entity is added to Home Assistant via a config entry. A device will be matched up with an existing device via supplied identifiers or connections, like serial numbers or MAC addresses. If identifiers and connections are provided, the device registry will first try to match by identifiers. Each identifier and each connection is matched individually (e.g. only one connection needs to match to be considered the same device).

# Inside a platform
class HueLight(LightEntity):
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (hue.DOMAIN, self.unique_id)
            },
            name=self.name,
            manufacturer=self.light.manufacturername,
            model=self.light.productname,
            model_id=self.light.modelid,
            sw_version=self.light.swversion,
            via_device=(hue.DOMAIN, self.api.bridgeid),
        )


Besides device properties, device_info can also include default_manufacturer, default_model, default_name. These values will be added to the device registry if no other value is defined just yet. This can be used by integrations that know some information but not very specific. For example, a router that identifies devices based on MAC addresses.

Manual registration
Components are also able to register devices in the case that there are no entities representing them. An example is a hub that communicates with the lights.

# Inside a component
from homeassistant.helpers import device_registry as dr

device_registry = dr.async_get(hass)

device_registry.async_get_or_create(
    config_entry_id=entry.entry_id,
    connections={(dr.CONNECTION_NETWORK_MAC, config.mac)},
    identifiers={(DOMAIN, config.bridgeid)},
    manufacturer="Signify",
    suggested_area="Kitchen",
    name=config.name,
    model=config.modelname,
    model_id=config.modelid,
    sw_version=config.swversion,
    hw_version=config.hwversion,
)

Removing devices
Integrations can opt in to allow the user to delete a device from the UI. To do this, integrations should implement the function async_remove_config_entry_device in their __init__.py module.

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""


When the user clicks the delete device button for the device and confirms it, async_remove_config_entry_device will be awaited and if True is returned, the config entry will be removed from the device. If it was the only config entry of the device, the device will be removed from the device registry.

In async_remove_config_entry_device the integration should take the necessary steps to prepare for device removal and return True if successful. The integration may optionally act on EVENT_DEVICE_REGISTRY_UPDATED if that's more convenient than doing the cleanup in async_remove_config_entry_device.

Categorizing to device info
Device info is categorized into Link, Primary and Secondary by finding the first device info type which has all the keys of the device info.

Category	Keys
Link	connections and identifiers
Primary	configuration_url, connections, entry_type, hw_version, identifiers, manufacturer, model, name, suggested_area, sw_version, and via_device
Secondary	connections, default_manufacturer, default_model, default_name, and via_device
This categorization is used in sorting the configuration entries to define the main integration to be used by the frontend.

Mandatorily, the device info must match one of the categories.

Area registry
The area registry is a registry where Home Assistant keeps track of areas. An area represents a physical location for Home Assistant. It can be used to place devices in different areas.

Attribute	Description
id	Unique ID of area (generated by Home Assistant)
name	Name of this area

Config entries
Config entries are configuration data that are persistently stored by Home Assistant. A config entry is created by a user via the UI. The UI flow is powered by a config flow handler as defined by the integration.

Once created, config entries can be removed by the user. Optionally, config entries can be changed by the user via a reconfigure step or options flow handler, also defined by the integration.

Config subentries
Config entries can logically separate the stored configuration data into subentries, which can be added by the user via the UI to an existing config entry. An example of this is an integration providing weather forecasts, where the config entry stores authentication details and each location for which weather forecasts should be provided is stored as a subentry.

Similar to config entries, subentries can optionally support a reconfigure step.

Lifecycle
State	Description
not loaded	The config entry has not been loaded. This is the initial state when a config entry is created or when Home Assistant is restarted.
setup in progress	An intermediate state while attempting to load the config entry.
loaded	The config entry has been loaded.
setup error	An error occurred when trying to set up the config entry.
setup retry	A dependency of the config entry was not ready yet. Home Assistant will automatically retry loading this config entry in the future. Time between attempts will automatically increase.
migration error	The config entry had to be migrated to a newer version, but the migration failed.
unload in progress	An intermediate state while attempting to unload the config entry.
failed unload	The config entry was attempted to be unloaded, but this was either not supported or it raised an exception.
More information about surfacing errors and requesting a retry are in Handling Setup Failures.

Setting up an entry
During startup, Home Assistant first calls the normal integration setup, and then calls the method async_setup_entry(hass, entry) for each entry. If a new Config Entry is created at runtime, Home Assistant will also call async_setup_entry(hass, entry) (example).

For platforms
If an integration includes platforms, it will need to forward the Config Entry set up to the platform. This can be done by calling the forward function on the config entry manager (example):

await hass.config_entries.async_forward_entry_setups(config_entry, ["light", "sensor", "switch"])


For a platform to support config entries, it will need to add a setup entry function (example):

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up entry."""

Unloading entries
Integrations can optionally support unloading a config entry. When unloading an entry, the integration needs to clean up all entities, unsubscribe any event listener and close all connections. To implement this, add async_unload_entry(hass, entry) to your integration (example). The state of the config entry is set to ConfigEntryState.UNLOAD_IN_PROGRESS before async_unload_entry is called.

For each platform that you forwarded the config entry to, you will need to forward the unloading too.

async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload a config entry."""


If you need to clean up resources used by an entity in a platform, have the entity implement the async_will_remove_from_hass method.

Removal of entries
If an integration needs to clean up code when an entry is removed, it can define a removal function async_remove_entry. The config entry is deleted from hass.config_entries before async_remove_entry is called.

async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""

Migrating config entries to a new version
If the config entry version is changed, async_migrate_entry must be implemented to support the migration of old entries. This is documented in detail in the config flow documentation

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""


Modifying a config entry
A ConfigEntry object, including the data and options, must never be mutated directly by integrations, instead integrations must call async_update_entry, the use of which is illustrated in the config flow documentation.

Subscribing to config entry state changes
If you want to be notified about a ConfigEntry changing its state (e.g. from ConfigEntryState.LOADED to ConfigEntryState.UNLOAD_IN_PROGRESS), you can add a listener which will be notified to async_on_state_change. This helper also returns a callback you can call to remove the listener again. Subscribing to changes until the entry is unloaded would therefore be entry.async_on_unload(entry.async_on_state_change(notify_me)).

Data entry flow
Data Entry Flow is a data entry framework that is part of Home Assistant. Data entry is done via data entry flows. A flow can represent a simple login form or a multi-step setup wizard for a component. A Flow Manager manages all flows that are in progress and handles creation of new flows.

Data Entry Flow is used in Home Assistant to login, create config entries, handle options flow, repair issues.

Flow manager
This is the class that manages the flows that are in progress. When instantiating one, you pass in two async callbacks:

async def async_create_flow(handler, context=context, data=data):
    """Create flow."""

The manager delegates instantiating of config flow handlers to this async callback. This allows the parent of the manager to define their own way of finding handlers and preparing a handler for instantiation. For example, in the case of the config entry manager, it will make sure that the dependencies and requirements are setup.

async def async_finish_flow(flow, result):
    """Finish flow."""

This async callback is called when a flow is finished or aborted. i.e. result['type'] in [FlowResultType.CREATE_ENTRY, FlowResultType.ABORT]. The callback function can modify result and return it back, if the result type changed to FlowResultType.FORM, the flow will continue running, display another form.

If the result type is FlowResultType.FORM, the result should look like:

{
    # The result type of the flow
    "type": FlowResultType.FORM,
    # the id of the flow
    "flow_id": "abcdfgh1234",
    # handler name
    "handler": "hue",
    # name of the step, flow.async_step_[step_id] will be called when form submitted
    "step_id": "init",
    # a voluptuous schema to build and validate user input
    "data_schema": vol.Schema(),
    # an errors dict, None if no errors
    "errors": errors,
    # a detail information about the step
    "description_placeholders": description_placeholders,
}


If the result type is FlowResultType.CREATE_ENTRY, the result should look like:

{
    # Data schema version of the entry
    "version": 2,
    # The result type of the flow
    "type": FlowResultType.CREATE_ENTRY,
    # the id of the flow
    "flow_id": "abcdfgh1234",
    # handler name
    "handler": "hue",
    # title and data as created by the handler
    "title": "Some title",
    "result": {
        "some": "data"
    },
}

If the result type is FlowResultType.ABORT, the result should look like:

{
    # The result type of the flow
    "type": FlowResultType.ABORT,
    # the id of the flow
    "flow_id": "abcdfgh1234",
    # handler name
    "handler": "hue",
    # the abort reason
    "reason": "already_configured",
}

Flow handler
Flow handlers will handle a single flow. A flow contains one or more steps. When a flow is instantiated, the FlowHandler.init_step step will be called. Each step has several possible results:

Show Form
Create Entry
Abort
External Step
Show Progress
Show Menu
At a minimum, each flow handler will have to define a version number and a step. This doesn't have to be init, as async_create_flow can assign init_step dependent on the current workflow, for example in configuration, context.source will be used as init_step.

For example, a bare minimum config flow would be:

from homeassistant import data_entry_flow

@config_entries.HANDLERS.register(DOMAIN)
class ExampleConfigFlow(data_entry_flow.FlowHandler):

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    # (this is not implemented yet)
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""


Data entry flows depend on translations for showing the text in the steps. It depends on the parent of a data entry flow manager where this is stored. For config and option flows, this is in strings.json under config and option, respectively.

For a more detailed explanation of strings.json see the backend translation page.

Show form
This result type will show a form to the user to fill in. You define the current step, the schema of the data (using a mixture of voluptuous and/or selectors) and optionally a dictionary of errors.

from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import selector

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        data_schema = {
            vol.Required("username"): str,
            vol.Required("password"): str,
            # Items can be grouped by collapsible sections
            vol.Required("ssl_options"): section(
                vol.Schema(
                    {
                        vol.Required("ssl", default=True): bool,
                        vol.Required("verify_ssl", default=True): bool,
                    }
                ),
                # Whether or not the section is initially collapsed (default = False)
                {"collapsed": False},
            )
        }

        if self.show_advanced_options:
            data_schema[vol.Optional("allow_groups")] = selector({
                "select": {
                    "options": ["all", "light", "switch"],
                }
            })

        return self.async_show_form(step_id="init", data_schema=vol.Schema(data_schema))


Grouping of input fields
As shown in the example above, input fields can be visually grouped in sections.

Each section has a translatable name and description, and it's also possible to specify an icon.

Grouping input fields by sections influences both how the inputs are displayed to the user and how user input is structured. In the example above, user input will be structured like this:

{
    "username": "user",
    "password": "hunter2",
    "ssl_options": {
        "ssl": True,
        "verify_ssl": False,
    },
}

Only a single level of sections is allowed; it's not possible to have sections inside a section.

To specify an icon for a section, update icons.json according to this example:

{
  "config": {
    "step": {
      "user": {
        "sections": {
          "ssl_options": "mdi:lock"
        }
      }
    }
  }
}

Labels & descriptions
Translations for the form are added to strings.json in a key for the step_id. That object may contain the folowing keys:

Key	Value	Notes
title	Form heading	Do not include your brand name. It will be automatically injected from your manifest.
description	Form instructions	Optional. Do not link to the documentation as that is linked automatically. Do not include "basic" information like "Here you can set up X".
data	Field labels	Keep succinct and consistent with other integrations whenever appropriate for the best user experience.
data_description	Field descriptions	Optional explanatory text to show below the field.
section	Section translation	Translations for sections, each section may have name and description of the section and data and data_description for its fields.
More details about translating data entry flows can be found in the core translations documentation.

The field labels and descriptions are given as a dictionary with keys corresponding to your schema. Here is a simple example:

{
  "config": {
    "step": {
      "user": {
          "title": "Add Group",
          "description": "Some description",
          "data": {
              "entities": "Entities"
          },
          "data_description": {
              "entities": "The entities to add to the group"
          },
          "sections": {
              "additional_options": {
                  "name": "Additional options",
                  "description": "A description of the section",
                  "data": {
                      "advanced_group_option": "Advanced group option"
                  },
                  "data_description": {
                      "advanced_group_option": "A very complicated option which does abc"
                  },
              }
          }
      }
    }
  }
}


Enabling browser autofill
Suppose your integration is collecting form data which can be automatically filled by browsers or password managers, such as login credentials or contact information. You should enable autofill whenever possible for the best user experience and accessibility. There are two options to enable this.

The first option is to use Voluptuous with data keys recognized by the frontend. The frontend will recognize the keys "username" and "password" and add HTML autocomplete attribute values of "username" and "current-password" respectively. Support for autocomplete is limited to "username" and "password" fields and is supported primarily to quickly enable auto-fill on the many integrations that collect them without converting their schemas to selectors.

The second option is to use a text selector. A text selector gives full control of the input type and allows any permitted value for autocomplete to be specified. A hypothetical schema collecting specific fillable data might be:

import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")
        ),
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
        vol.Required("postal_code"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="postal-code")
        ),
        vol.Required("mobile_number"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEL, autocomplete="tel")
        ),
    }
)


Defaults & suggestions
If you'd like to pre-fill data in the form, you have two options. The first is to use the default parameter. This will both pre-fill the field, and act as the default value in case the user leaves the field empty.

    data_schema = {
        vol.Optional("field_name", default="default value"): str,
    }

The other alternative is to use a suggested value - this will also pre-fill the form field, but will allow the user to leave it empty if the user so wishes.

    data_schema = {
        vol.Optional(
            "field_name", description={"suggested_value": "suggested value"}
        ): str,
    }


You can also mix and match - pre-fill through suggested_value, and use a different value for default in case the field is left empty, but that could be confusing to the user so use carefully.

Using suggested values also make it possible to declare a static schema, and merge suggested values from existing input. A add_suggested_values_to_schema helper makes this possible:

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional("field_name", default="default value"): str,
    }
)

class ExampleOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return self.async_show_form(
            data_schema = self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.entry.options
            )
        )

Displaying read-only information
Some integrations have options which are frozen after initial configuration. When displaying an options flow, you can show this information in a read-only way, so that users may remember which options were selected during the initial configuration. For this, define an optional selector as usual, but with the read_only flag set to True.

# Example Config Flow Schema
DATA_SCHEMA_SETUP = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): EntitySelector()
    }
)

# Example Options Flow Schema
DATA_SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(CONF_ENTITY_ID): EntitySelector(
            EntitySelectorConfig(read_only=True)
        ),
        vol.Optional(CONF_TEMPLATE): TemplateSelector(),
    }
)

This will show the entity selected in the initial configuration as a read-only property whenever the options flow is launched.

Validation
After the user has filled in the form, the step method will be called again and the user input is passed in. Your step will only be called if the user input passes your data schema. When the user passes in data, you will have to do extra validation of the data. For example, you can verify that the passed in username and password are valid.

If something is wrong, you can return a dictionary with errors. Each key in the error dictionary refers to a field name that contains the error. Use the key base if you want to show an error unrelated to a specific field. The specified errors need to refer to a key in a translation file.

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate user input
            valid = await is_valid(user_input)
            if valid:
                # See next section on create entry usage
                return self.async_create_entry(...)

            errors["base"] = "auth_error"

        # Specify items in the order they are to be displayed in the UI
        data_schema = {
            vol.Required("username"): str,
            vol.Required("password"): str,
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=errors
        )


Multi-step flows
If the user input passes validation, you can return one of the possible step types again. If you want to navigate the user to the next step, return the return value of that step:

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate user input
            valid = await is_valid(user_input)
            if valid:
                # Store info to use in next step
                self.init_info = user_input
                # Return the form of the next step
                return await self.async_step_account()

        ...

Create entry
When the result is "Create Entry", an entry will be created and passed to the parent of the flow manager. A success message is shown to the user and the flow is finished. You create an entry by passing a title, data and optionally options. The title can be used in the UI to indicate to the user which entry it is. Data and options can be any data type, as long as they are JSON serializable. Options are used for mutable data, for example a radius. Whilst Data is used for immutable data that isn't going to change in an entry, for example location data.

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="Title of the entry",
            data={
                "username": user_input["username"],
                "password": user_input["password"]
            },
            options={
                "mobile_number": user_input["mobile_number"]
            },
        )

Note: A user can change their password, which technically makes it mutable data, but for changing authentication credentials, you use reauthentication, which can mutate the config entry data.

Abort
When a flow cannot be finished, you need to abort it. This will finish the flow and inform the user that the flow has finished. Reasons for a flow to not be able to finish can be that a device is already configured or not compatible with Home Assistant.

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_user(self, user_input=None):
        return self.async_abort(reason="not_supported")

External step & external step done
It is possible that a user needs to finish a config flow by doing actions on an external website. For example, setting up an integration by being redirected to an external webpage. This is commonly used by integrations that use OAuth2 to authorize a user.

The example is about config entries, but works with other parts that use data entry flows too.

The flow works as follows:

The user starts config flow in Home Assistant.

Config flow prompts the user to finish the flow on an external website.

The user opens the external website.

Upon completion of the external step, the user's browser will be redirected to a Home Assistant endpoint to deliver the response.

The endpoint validates the response, and upon validation, marks the external step as done and returns JavaScript code to close the window: <script>window.close()</script>.

To be able to route the result of the external step to the Home Assistant endpoint, you will need to make sure the config flow ID is included. If your external step is an OAuth2 flow, you can leverage the oauth2 state for this. This is a variable that is not interpreted by the authorization page but is passed as-is to the Home Assistant endpoint.

The window closes and the Home Assistant user interface with the config flow will be visible to the user again.

The config flow has automatically advanced to the next step when the external step was marked as done. The user is prompted with the next step.

Example configuration flow that includes an external step.

from homeassistant import config_entries

@config_entries.HANDLERS.register(DOMAIN)
class ExampleConfigFlow(data_entry_flow.FlowHandler):
    VERSION = 1
    data = None

    async def async_step_user(self, user_input=None):
        if not user_input:
            return self.async_external_step(
                step_id="user",
                url=f"https://example.com/?config_flow_id={self.flow_id}",
            )

        self.data = user_input
        return self.async_external_step_done(next_step_id="finish")

    async def async_step_finish(self, user_input=None):
        return self.async_create_entry(title=self.data["title"], data=self.data)


Avoid doing work based on the external step data before you return an async_mark_external_step_done. Instead, do the work in the step that you refer to as next_step_id when marking the external step done. This will give the user a better user experience by showing a spinner in the UI while the work is done.

If you do the work inside the authorize callback, the user will stare at a blank screen until that all of a sudden closes because the data has forwarded. If you do the work before marking the external step as done, the user will still see the form with the "Open external website" button while the background work is being done. That too is undesirable.

Example code to mark an external step as done:

from homeassistant import data_entry_flow


async def handle_result(hass, flow_id, data):
    result = await hass.config_entries.async_configure(flow_id, data)

    if result["type"] == data_entry_flow.FlowResultType.EXTERNAL_STEP_DONE:
        return "success!"
    else:
        return "Invalid config flow specified"


Show progress & show progress done
If a data entry flow step needs a considerable amount of time to finish, we should inform the user about this.

The example is about config entries, but works with other parts that use data entry flows too.

The flow works as follows:

The user starts the config flow in Home Assistant.
The config flow creates an asyncio.Task to execute the long running task.
The config flow informs the user that a task is in progress and will take some time to finish by calling async_show_progress, passing the asyncio.Task object to it. The flow should pass a task specific string as progress_action parameter to represent the translated text string for the prompt.
The config flow will be automatically called once the task is finished, but may also be called before the task has finished, for example if frontend reloads.
If the task is not yet finished, the flow should not create another task, but instead call async_show_progress again.
If the task is finished, the flow must call the async_show_progress_done, indicating the next step
The frontend will update each time we call show progress or show progress done.
The config flow will automatically advance to the next step when the progress was marked as done. The user is prompted with the next step.
The task can optionally call async_update_progress(progress) where progress is a float between 0 and 1, indicating how much of the task is done.
Example configuration flow that includes two show sequential progress tasks.

import asyncio

from homeassistant import config_entries
from .const import DOMAIN

class TestFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    task_one: asyncio.Task | None = None
    task_two: asyncio.Task | None = None

    async def async_step_user(self, user_input=None):
        uncompleted_task: asyncio.Task[None] | None = None

        if not self.task_one:
            coro = asyncio.sleep(10)
            self.task_one = self.hass.async_create_task(coro)
        if not self.task_one.done():
            progress_action = "task_one"
            uncompleted_task = self.task_one
        if not uncompleted_task:
            if not self.task_two:
                self.async_update_progress(0.5) # tell frontend we are 50% done
                coro = asyncio.sleep(10)
                self.task_two = self.hass.async_create_task(coro)
            if not self.task_two.done():
                progress_action = "task_two"
                uncompleted_task = self.task_two
        if uncompleted_task:
            return self.async_show_progress(
                progress_action=progress_action,
                progress_task=uncompleted_task,
            )

        return self.async_show_progress_done(next_step_id="finish")

    async def async_step_finish(self, user_input=None):
        if not user_input:
            return self.async_show_form(step_id="finish")
        return self.async_create_entry(title="Some title", data={})


Show menu
This will show a navigation menu to the user to easily pick the next step. The menu labels can be hardcoded by specifying a dictionary of {step_id: label} or translated via strings.json when specifying a list.

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_user(self, user_input=None):
        return self.async_show_menu(
            step_id="user",
            menu_options=["discovery", "manual"],
            description_placeholders={
                "model": "Example model",
            }
        )
        # Example showing the other approach
        return self.async_show_menu(
            step_id="user",
            menu_options={
                "option_1": "Option 1",
                "option_2": "Option 2",
            }
        )

{
  "config": {
    "step": {
      "user": {
        "menu_options": {
          "discovery": "Discovery",
          "manual": "Manual ({model})",
        }
      }
    }
  }
}

Initializing a config flow from an external source
You might want to initialize a config flow programmatically. For example, if we discover a device on the network that requires user interaction to finish setup. To do so, pass a source parameter and optional user input when initializing a flow:

await flow_mgr.async_init(
    "hue", context={"source": data_entry_flow.SOURCE_DISCOVERY}, data=discovery_info
)


The config flow handler will not start with the init step. Instead, it will be instantiated with a step name equal to the source. The step should follow the same return values as a normal step.

class ExampleConfigFlow(data_entry_flow.FlowHandler):
    async def async_step_discovery(self, info):
        """Handle discovery info."""

The source of a config flow is available as self.source on FlowHandler.

Device automations
Device Automations provide users with a device-centric layer on top of the core concepts of Home Assistant. When creating automations, users no longer have to deal with core concepts like states and events. Instead, they will be able to pick a device and then pick from a list of pre-defined triggers, conditions and actions.

Integrations can hook into this system by exposing functions to generate the pre-defined triggers, conditions, actions and having functions that can listen for the triggers, check the condition and execute the action.

Device automations are not exposing extra functionality but are a way for users to not have to learn new concepts. Device automations are using events, state and service action helpers under the hood.

Secondary device automations
Some devices may expose a lot of device automation. To not overwhelm the user, a device automation can be marked as secondary. A device automation which is marked as secondary will still be shown to the user, but may be shown after other device automations or may require the user to select a "show more" option or similar.

If the device automation references an entity via an entity_id key, the secondary flag will automatically be set to True if the referenced entity is hidden or if the referenced entity's entity category is not None. The example below shows how to mark a device automation as secondary.

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.helpers import device_registry as dr

async def async_get_triggers(hass, device_id):
    """Return a list of triggers."""

    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    triggers = []

    # Determine which triggers are supported by this device_id ...

    triggers.append({
        # Required fields of TRIGGER_BASE_SCHEMA
        CONF_PLATFORM: "device",
        CONF_DOMAIN: "mydomain",
        CONF_DEVICE_ID: device_id,
        # Required fields of TRIGGER_SCHEMA
        CONF_TYPE: "less_important_trigger",
        # Mark the trigger as secondary
        "metadata": {"secondary": True},
    })

    return triggers

Device triggers
Device triggers are automation triggers that are tied to a specific device and an event or state change. Examples are "light turned on" or "water detected".

Device triggers can be provided by the integration that provides the device (e.g. ZHA, deCONZ) or the entity integrations that the device has entities with (e.g. light, switch). An example of the former is events not tied to an entity e.g. key press on a remote control or touch panel, while an example of the latter could be that a light has been turned on.

To add support for Device Triggers, an integration needs to have a device_trigger.py and:

Define a TRIGGER_SCHEMA: A dictionary that represents a trigger, such as a device and an event type
Create triggers: Create dictionaries containing the device or entity and supported events or state changes as defined by the schema.
Attach triggers: Associate a trigger config with an event or state change, e.g. a message fired on the event bus.
Add text and translations: Give each trigger a human readable name.
Do not apply the static schema manually. The core will apply the schema if the trigger schema is defined as a constant in the device_trigger.py module of the integration.

If the trigger requires dynamic validation that the static TRIGGER_SCHEMA can't provide, it's possible to implement an async_validate_trigger_config function.

async def async_validate_trigger_config(hass: HomeAssistant, config: ConfigType) -> ConfigType:
    """Validate config."""


Home Assistant includes a template to get started with device triggers. To get started, run inside a development environment python3 -m script.scaffold device_trigger.

The template will create a new file device_trigger.py in your integration folder and a matching test file. The file contains the following functions and constants:

Define a TRIGGER_SCHEMA
Device triggers are defined as dictionaries. These dictionaries are created by your integration and are consumed by your integration to attach the trigger.

This is a voluptuous schema that verifies that a specific trigger dictionary represents a config that your integration can handle. This should extend the TRIGGER_BASE_SCHEMA from device_automation/__init__.py.

from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_TYPE,
)

TRIGGER_TYPES = {"water_detected", "noise_detected"}

TRIGGER_SCHEMA = TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)

This example has a single type field indicating the type of events supported.

Create triggers
The async_get_triggers method returns a list of triggers supported by the device or any associated entities. These are the triggers exposed to the user for creating automations.

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.helpers import device_registry as dr

async def async_get_triggers(hass, device_id):
    """Return a list of triggers."""

    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)

    triggers = []

    # Determine which triggers are supported by this device_id ...

    triggers.append({
        # Required fields of TRIGGER_BASE_SCHEMA
        CONF_PLATFORM: "device",
        CONF_DOMAIN: "mydomain",
        CONF_DEVICE_ID: device_id,
        # Required fields of TRIGGER_SCHEMA
        CONF_TYPE: "water_detected",
    })

    return triggers

Attach triggers
To wire it up: Given a TRIGGER_SCHEMA config, make sure the action is called when the trigger is triggered.

For example, you might attach the trigger and action to Events fired on the event bus by your integration.

async def async_attach_trigger(hass, config, action, trigger_info):
    """Attach a trigger."""
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: "mydomain_event",
            event_trigger.CONF_EVENT_DATA: {
                CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )


The return value is a function that detaches the trigger.

Add text and translations
The Automation user interface will display a human-readable string in the device automation mapped to the event type. Update strings.json with the trigger types and subtypes that you support:

{
   "device_automation": {
    "trigger_type": {
      "water_detected": "Water detected",
      "noise_detected": "Noise detected"
    }
}

To test your translations during development, run python3 -m script.translations develop.

Device conditions
Device conditions allow a user to check if a certain condition is met. Examples are is a light on or is the floor wet.

Device conditions are defined as dictionaries. These dictionaries are created by your integration and are passed to your integration to create a function that checks the condition.

Device conditions can be provided by the integration that provides the device (e.g. ZHA, deCONZ) or the entity integrations that the device has entities with (e.g. light, humidity sensor). An example of the latter could be to check if a light is on or the floor is wet.

If the condition requires dynamic validation that the static CONDITION_SCHEMA can't provide, it's possible to implement an async_validate_condition_config function.

async def async_validate_condition_config(hass: HomeAssistant, config: ConfigType) -> ConfigType:
    """Validate config."""


Home Assistant includes a template to get started with device conditions. To get started, run inside a development environment python3 -m script.scaffold device_condition.

The template will create a new file device_condition.py in your integration folder and a matching test file. The file contains the following functions and constants:

CONDITION_SCHEMA
This is the schema for conditions. The base schema should be extended from homeassistant.helpers.config_validation.DEVICE_CONDITION_BASE_SCHEMA.

async_get_conditions
async def async_get_conditions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device conditions for devices."""

Return a list of conditions that this device supports.

async_condition_from_config
@callback
def async_condition_from_config(
    config: ConfigType, config_validation: bool
) -> condition.ConditionCheckerType:
    """Create a function to test a device condition."""

Create a condition function from a function. The condition functions should be an async-friendly callback that evaluates the condition and returns a bool.

The config_validation parameter will be used by the core to apply config validation conditionally with the defined CONDITION_SCHEMA.


Device actions
Device actions allow a user to have a device do something. Examples are to turn a light on or open a door.

Device actions are defined as dictionaries. These dictionaries are created by your integration and are passed to your integration to create a function that performs the action.

Device actions can be provided by the integration that provides the device (e.g. ZHA, deCONZ) or the entity integrations that the device has entities with (e.g. light, switch). An example of the former could be to reboot the device, while an example of the latter could be to turn a light on.

If the action requires dynamic validation that the static ACTION_SCHEMA can't provide, it's possible to implement an async_validate_action_config function.

async def async_validate_action_config(hass: HomeAssistant, config: ConfigType) -> ConfigType:
    """Validate config."""


Home Assistant includes a template to get started with device actions. To get started, run inside a development environment python3 -m script.scaffold device_action.

The template will create a new file device_action.py in your integration folder and a matching test file. The file contains the following functions and constants:

ACTION_SCHEMA
This is the schema for actions. The base schema should be extended from homeassistant.helpers.config_validation.DEVICE_ACTION_BASE_SCHEMA. Do not apply the schema manually. The core will apply the schema if the action schema is defined as a constant in the device_action.py module of the integration.

async_get_actions
async def async_get_actions(hass: HomeAssistant, device_id: str) -> list[dict]:
    """List device actions for devices."""


Return a list of actions that this device supports.

async_call_action_from_config
async def async_call_action_from_config(
    hass: HomeAssistant, config: dict, variables: dict, context: Context | None
) -> None:
    """Execute a device action."""


Execute the passed in action.

Brands
A commercial brand may have several integrations which provide support for different offerings under that brand. Also, a brand may offer devices which comply with an IoT standard, for example Zigbee or Z-Wave. As an example of the first case, there are multiple integrations providing support for different Google products, e.g. Google Calendar by the google integration and Google Sheets by the google_sheets integration. As an example of the second case, Innovelli offers Zigbee and Z-Wave devices and doesn't need its own integration.

To make these integrations easier to find by the user, they should be collected in a file within the homeassistant/brandsfolder.

Examples:

{
  "domain": "google",
  "name": "Google",
  "integrations": ["google", "google_sheets"]
}

{
  "domain": "innovelli",
  "name": "Innovelli",
  "iot_standards": ["zigbee", "zwave"]
}

Or a minimal example that you can copy into your project:

{
  "domain": "your_brand_domain",
  "name": "Your Brand",
  "integrations": [],
  "iot_standards": []
}

Domain
The domain is a short name consisting of characters and underscores. This domain has to be unique and cannot be changed. Example of the domain for the Google brand: google. The domain key has to match the file name of the brand file it is in. If there's an integration with the same domain, it has to be listed in the brand's integrations.

Name
The name of the brand.

Integrations
A list of integration domains implementing offerings of the brand.

IoT standards
A list of IoT standards which are supported by devices of the brand. Possible values are homekit, zigbee and zwave. Note that a certain device may not support any of the listed IoT standards.

Application credentials
Integrations may support Configuration via OAuth2 allowing users to link their accounts. Integrations may add a application_credentials.py file and implement the functions described below.

OAuth2 requires credentials that are shared between an application and provider. In Home Assistant, integration specific OAuth2 credentials are provided using one or more approaches:

Local OAuth with Application Credentials Component: Users create their own credentials with the cloud provider, often acting as an application developer, and register the credentials with Home Assistant and the integration. This approach is required by all integrations that support OAuth2.
Cloud Account Linking with Cloud Component: Nabu Casa registers credentials with the cloud provider, providing a seamless user experience. This approach provides a seamless user experience and is recommended (more info).
Adding support
Integrations support application credentials by adding a dependency on the application_credentials component in the manifest.json:

{
  ...
  "dependencies": ["application_credentials"],
  ...
}

Then add a file in the integration folder called application_credentials.py and implement the following:

from homeassistant.core import HomeAssistant
from homeassistant.components.application_credentials import AuthorizationServer


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url="https://example.com/auth",
        token_url="https://example.com/oauth2/v4/token"
    )


AuthorizationServer
An AuthorizationServer represents the OAuth2 Authorization server used for an integration.

Name	Type		Description
authorize_url	str	Required	The OAuth authorize URL that the user is redirected to during the configuration flow.
token_url	str	Required	The URL used for obtaining an access token.
Custom OAuth2 Implementations
Integrations may alternatively provide a custom AbstractOAuth2Implementation in application_credentials.py like the following:

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.components.application_credentials import AuthImplementation, AuthorizationServer, ClientCredential


class OAuth2Impl(AuthImplementation):
    """Custom OAuth2 implementation."""
    # ... Override AbstractOAuth2Implementation details

async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return auth implementation for a custom auth implementation."""
    return OAuth2Impl(
        hass,
        auth_domain,
        credential,
        AuthorizationServer(
            authorize_url="https://example.com/auth",
            token_url="https://example.com/oauth2/v4/token"
        )
    )


Authorization flow with PKCE Support
If you want to support PKCE you can return the LocalOAuth2ImplementationWithPkce in application_credentials.py as follows:

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import AbstractOAuth2Implementation, LocalOAuth2ImplementationWithPkce
from homeassistant.components.application_credentials import AuthImplementation, ClientCredential


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> AbstractOAuth2Implementation:
    """Return auth implementation for a custom auth implementation."""
    return LocalOAuth2ImplementationWithPkce(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url="https://example.com/auth",
        token_url="https://example.com/oauth2/v4/token",
        client_secret=credential.client_secret, # optional `""` is default
        code_verifier_length=128 # optional
    )


Import YAML credentials
Credentials may be imported by integrations that used to accept YAML credentials using the import API async_import_client_credential provided by the application credentials integration.

Here is an example from an integration that used to accept YAML credentials:

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)

# Example configuration.yaml schema for an integration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): cv.string,
                vol.Required(CONF_CLIENT_SECRET): cv.string,
            }
        )
    },
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    if DOMAIN not in config:
        return True

    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(
            config[DOMAIN][CONF_CLIENT_ID],
            config[DOMAIN][CONF_CLIENT_SECRET],
        ),
    )


New integrations should not accept credentials in configuration.yaml as users can instead enter credentials in the Application Credentials user interface.

ClientCredential
A ClientCredential represents a client credential provided by the user.

Name	Type		Description
client_id	str	Required	The OAuth Client ID provided by the user.
client_secret	str	Required	The OAuth Client Secret provided by the user.
Translations
Translations for Application Credentials are defined under the application_credentials key in the component translation file strings.json. As an example:

{
    "application_credentials": {
        "description": "Navigate to the [developer console]({console_url}) to create credentials then enter them below.",
    }
}


You may optionally add description placeholder keys that are added to the message by adding a new method in application_credentials.py like the following:

from homeassistant.core import HomeAssistant

async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    """Return description placeholders for the credentials dialog."""
    return {
        "console_url": "https://example.com/developer/console",
    }


While developing locally, you will need to run python3 -m script.translations develop to see changes made to strings.json More info on translating Home Assistant.

Raising exceptions
Raising exceptions in service action handlers
Operations like service action calls and entity methods (e.g. Set HVAC Mode) should raise exceptions properly.

Integrations should raise ServiceValidationError (instead of ValueError) in case when the user did something wrong. In this case a stack trace will only be printed at debug level.

For other failures such as a problem communicating with a device, HomeAssistantError should be raised. Note that the exception stack trace will be printed to the log in this case.

Localizing exceptions
Home Assistant supports localization for HomeAssistantError and its subclasses like ServiceValidationError.

Repairs
Home Assistant keeps track of issues which should be brought to the user's attention. These issues can be created by integrations or by Home Assistant itself. Issues can either be fixable via a RepairsFlow or by linking to a website with information on how the user can solve it themselves.

Creating an issue
from homeassistant.helpers import issue_registry as ir

ir.async_create_issue(
    hass,
    DOMAIN,
    "manual_migration",
    breaks_in_ha_version="2022.9.0",
    is_fixable=False,
    severity=ir.IssueSeverity.ERROR,
    translation_key="manual_migration",
)

Attribute	Type	Default	Description
domain	string		Domain raising the issue
issue_id	string		An identifier for the issue, must be unique within domain
breaks_in_ha_version	string	None	The version in which the issue is breaking
data	dict	None	Arbitrary data, not shown to the user
is_fixable	boolean		True if the issue can be automatically fixed
is_persistent	boolean		True if the issue should persists across restarts of Home Assistant
issue_domain	string	None	Set by integrations creating issues on behalf of other integrations
learn_more_url	string	None	URL where the user can find more details about an issue
severity	IssueSeverity		Severity of the issue
translation_key	str		Translation key with a brief explanation of the issue
translation_placeholders	dict	None	Placeholders which will be injected in the translation
Severity of an issue
To better understand which severity level to choose, see the list below.

IssueSeverity	Description
CRITICAL	Considered reserved, only used for true panic
ERROR	Something is currently broken and needs immediate attention
WARNING	Something breaks in the future (e.g., API shutdown) and needs attention
Offering a repair
Create a new platform file in your integration folder called repairs.py and add code according to the pattern below.

from __future__ import annotations

import voluptuous as vol

from homeassistant import data_entry_flow
from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant


class Issue1RepairFlow(RepairsFlow):
    """Handler for an issue fixing flow."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of a fix flow."""

        return await (self.async_step_confirm())

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the confirm step of a fix flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="confirm", data_schema=vol.Schema({}))


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create flow."""
    if issue_id == "issue_1":
        return Issue1RepairFlow()


Issue life cycle
Issue persistence
An issue will be kept in the issue registry until it's removed by the integration that created it or by the user fixing it.

The is_persistent flag controls if an issue should be shown to the user after a restart of Home Assistant:

If the is_persistent flag is set on the issue, the issue will be shown again to the user after a restart. Use this for issues that can only be detected when they occur (update failed, unknown action in automation).
If the is_persistent flag is not set on the issue, the issue will not be shown again to the user after a restart until it's created again by its integration. Use this for issues that can be checked for, like low disk space.
Ignored issues
It's possible for the user to "ignore" issues. An ignored issue is ignored until it's explicitly deleted - either by the integration or by the user successfully walking through its repair flow - and then created again. Ignoring an issue takes effect across restarts of Home Assistant regardless of issue persistence.

Deleting an issue
Integrations typically don't need to delete issues, but it may be useful in some cases.

from homeassistant.helpers import issue_registry as ir

ir.async_delete_issue(hass, DOMAIN, "manual_migration")

Fixing an issue
If an issue has the is_fixable issue set to True, the user will be allowed to fix the issue. An issue which is succesfully fixed will be removed from the issue registry.

Reproduce state
Home Assistant has support for scenes. Scenes are a collection of (partial) entity states. When a scene is activated, Home Assistant will try to call the right service actions to get the specified scenes in their specified state.

Integrations are responsible for adding support to Home Assistant to be able to call the right service actions to reproduce the states in a scene.

Adding support
The quickest way to add reproduce state support to a new integration is by using our built-in scaffold template. From a Home Assistant dev environment, run python3 -m script.scaffold reproduce_state and follow the instructions.

If you prefer to go the manual route, create a new file in your integration folder called reproduce_state.py and implement the following method:

import asyncio
from typing import Iterable, Optional
from homeassistant.core import Context, HomeAssistant, State


async def async_reproduce_states(
    hass: HomeAssistant, states: Iterable[State], context: Optional[Context] = None
) -> None:
    """Reproduce component states."""
    # TODO reproduce states


Significant change
Home Assistant doesn't only collect data, it also exports data to various services. Not all of these services are interested in every change. To help these services filter insignificant changes, your entity integration can add significant change support.

This support is added by creating a significant_change.py platform file with a function async_check_significant_change.

from typing import Any, Optional
from homeassistant.core import HomeAssistant, callback

@callback
def async_check_significant_change(
    hass: HomeAssistant,
    old_state: str,
    old_attrs: dict,
    new_state: str,
    new_attrs: dict,
    **kwargs: Any,
) -> bool | None:

This function is passed a state that was previously considered significant and the new state. It is not just passing the last 2 known states in. The function should return a boolean if it is significant or not, or None if the function doesn't know.

When deciding on significance, make sure you take all known attributes into account. Use device classes to differentiate between entity types.

Here are some examples of insignificant changes:

A battery that loses 0.1 % charge
A temperature sensor that changes 0.1 Celsius
A light that changes 2 brightness
Home Assistant will automatically handle cases like unknown and unavailable.

To add significant state support to an entity integration, run python3 -m script.scaffold significant_change.

WebSocket API
Home Assistant hosts a WebSocket API at /api/websocket. This API can be used to stream information from a Home Assistant instance to any client that implements WebSockets. We maintain a JavaScript library which we use in our frontend.

Server states
Client connects.
Authentication phase starts.
Server sends auth_required message.
Client sends auth message.
If auth message correct: go to 3.
Server sends auth_invalid. Go to 6.
Send auth_ok message
Authentication phase ends.
Command phase starts.
Client can send commands.
Server can send results of previous commands.
Client or server disconnects session.
During the command phase, the client attaches a unique identifier to each message. The server will add this identifier to each message so that the client can link each message to its origin.

Message format
Each API message is a JSON serialized object containing a type key. After the authentication phase messages also must contain an id, an integer that the caller can use to correlate messages to responses.

Example of an auth message:

{
  "type": "auth",
  "access_token": "ABCDEFGHIJKLMNOPQ"
}

{
   "id": 5,
   "type":"event",
   "event":{
      "data":{},
      "event_type":"test_event",
      "time_fired":"2016-11-26T01:37:24.265429+00:00",
      "origin":"LOCAL"
   }
}

Authentication phase
When a client connects to the server, the server sends out auth_required.

{
  "type": "auth_required",
  "ha_version": "2021.5.3"
}

The first message from the client should be an auth message. You can authorize with an access token.

{
  "type": "auth",
  "access_token": "ABCDEFGH"
}

If the client supplies valid authentication, the authentication phase will complete by the server sending the auth_ok message:

{
  "type": "auth_ok",
  "ha_version": "2021.5.3"
}

If the data is incorrect, the server will reply with auth_invalid message and disconnect the session.

{
  "type": "auth_invalid",
  "message": "Invalid password"
}

Feature enablement phase
Clients that supports features that needs enabling should as their first message (with "id": 1) send a message in the form:

{
  "id": 1,
  "type": "supported_features",
  "features": { coalesce_messages: 1 }
}

As of now the only feature supported is 'coalesce_messages' which result in messages being sent coalesced in bulk instead of individually.

Command phase
During this phase the client can give commands to the server. The server will respond to each command with a result message indicating when the command is done and if it was successful along with the context of the command.

{
  "id": 6,
  "type": "result",
  "success": true,
  "result": {
    "context": {
      "id": "326ef27d19415c60c492fe330945f954",
      "parent_id": null,
      "user_id": "31ddb597e03147118cf8d2f8fbea5553"
    }
  }
}

Subscribe to events
The command subscribe_events will subscribe your client to the event bus. You can either listen to all events or to a specific event type. If you want to listen to multiple event types, you will have to send multiple subscribe_events commands.

{
  "id": 18,
  "type": "subscribe_events",
  // Optional
  "event_type": "state_changed"
}

The server will respond with a result message to indicate that the subscription is active.

{
  "id": 18,
  "type": "result",
  "success": true,
  "result": null
}

For each event that matches, the server will send a message of type event. The id in the message will point at the original id of the listen_event command.

{
   "id": 18,
   "type":"event",
   "event":{
      "data":{
         "entity_id":"light.bed_light",
         "new_state":{
            "entity_id":"light.bed_light",
            "last_changed":"2016-11-26T01:37:24.265390+00:00",
            "state":"on",
            "attributes":{
               "rgb_color":[
                  254,
                  208,
                  0
               ],
               "color_temp":380,
               "supported_features":147,
               "xy_color":[
                  0.5,
                  0.5
               ],
               "brightness":180,
               "white_value":200,
               "friendly_name":"Bed Light"
            },
            "last_updated":"2016-11-26T01:37:24.265390+00:00",
            "context": {
               "id": "326ef27d19415c60c492fe330945f954",
               "parent_id": null,
               "user_id": "31ddb597e03147118cf8d2f8fbea5553"
            }
         },
         "old_state":{
            "entity_id":"light.bed_light",
            "last_changed":"2016-11-26T01:37:10.466994+00:00",
            "state":"off",
            "attributes":{
               "supported_features":147,
               "friendly_name":"Bed Light"
            },
            "last_updated":"2016-11-26T01:37:10.466994+00:00",
            "context": {
               "id": "e4af5b117137425e97658041a0538441",
               "parent_id": null,
               "user_id": "31ddb597e03147118cf8d2f8fbea5553"
            }
         }
      },
      "event_type":"state_changed",
      "time_fired":"2016-11-26T01:37:24.265429+00:00",
      "origin":"LOCAL",
      "context": {
         "id": "326ef27d19415c60c492fe330945f954",
         "parent_id": null,
         "user_id": "31ddb597e03147118cf8d2f8fbea5553"
      }
   }
}

Subscribe to trigger
You can also subscribe to one or more triggers with subscribe_trigger. These are the same triggers syntax as used for automation triggers. You can define one or a list of triggers.

{
    "id": 2,
    "type": "subscribe_trigger",
    "trigger": {
        "platform": "state",
        "entity_id": "binary_sensor.motion_occupancy",
        "from": "off",
        "to":"on"
    }
}

As a response you get:

{
 "id": 2,
 "type": "result",
 "success": true,
 "result": null
}

For each trigger that matches, the server will send a message of type trigger. The id in the message will point at the original id of the subscribe_trigger command. Note that your variables will be different based on the used trigger.

{
    "id": 2,
    "type": "event",
    "event": {
        "variables": {
            "trigger": {
                "id": "0",
                "idx": "0",
                "platform": "state",
                "entity_id": "binary_sensor.motion_occupancy",
                "from_state": {
                    "entity_id": "binary_sensor.motion_occupancy",
                    "state": "off",
                    "attributes": {
                        "device_class": "motion",
                        "friendly_name": "motion occupancy"
                    },
                    "last_changed": "2022-01-09T10:30:37.585143+00:00",
                    "last_updated": "2022-01-09T10:33:04.388104+00:00",
                    "context": {
                        "id": "90e30ad8e6d0c218840478d3c21dd754",
                        "parent_id": null,
                        "user_id": null
                    }
                },
                "to_state": {
                    "entity_id": "binary_sensor.motion_occupancy",
                    "state": "on",
                    "attributes": {
                        "device_class": "motion",
                        "friendly_name": "motion occupancy"
                    },
                    "last_changed": "2022-01-09T10:33:04.391956+00:00",
                    "last_updated": "2022-01-09T10:33:04.391956+00:00",
                    "context": {
                        "id": "9b263f9e4e899819a0515a97f6ddfb47",
                        "parent_id": null,
                        "user_id": null
                    }
                },
                "for": null,
                "attribute": null,
                "description": "state of binary_sensor.motion_occupancy"
            }
        },
        "context": {
            "id": "9b263f9e4e899819a0515a97f6ddfb47",
            "parent_id": null,
            "user_id": null
        }
    }
}


Unsubscribing from events
You can unsubscribe from previously created subscriptions. Pass the id of the original subscription command as value to the subscription field.

{
  "id": 19,
  "type": "unsubscribe_events",
  "subscription": 18
}

The server will respond with a result message to indicate that unsubscribing was successful.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": null
}

Fire an event
This will fire an event on the Home Assistant event bus.

{
  "id": 24,
  "type": "fire_event",
  "event_type": "mydomain_event",
  // Optional
  "event_data": {
    "device_id": "my-device-id",
    "type": "motion_detected"
  }
}

The server will respond with a result message to indicate that the event was fired successful.

{
  "id": 24,
  "type": "result",
  "success": true,
  "result": {
    "context": {
      "id": "326ef27d19415c60c492fe330945f954",
      "parent_id": null,
      "user_id": "31ddb597e03147118cf8d2f8fbea5553"
    }
  }
}

Calling a service action
This will call a service action in Home Assistant. Right now there is no return value. The client can listen to state_changed events if it is interested in changed entities as a result of a call.

{
  "id": 24,
  "type": "call_service",
  "domain": "light",
  "service": "turn_on",
  // Optional
  "service_data": {
    "color_name": "beige",
    "brightness": "101"
  }
  // Optional
  "target": {
    "entity_id": "light.kitchen"
  }
  // Must be included for service actions that return response data
  "return_response": true
}

The server will indicate with a message indicating that the action is done executing.

{
  "id": 24,
  "type": "result",
  "success": true,
  "result": {
    "context": {
      "id": "326ef27d19415c60c492fe330945f954",
      "parent_id": null,
      "user_id": "31ddb597e03147118cf8d2f8fbea5553"
    },
    "response": null
  }
}

The result of the call will always include a response to account for service actions that support responses. When a action that doesn't support responses is called, the value of response will be null.

Fetching states
This will get a dump of all the current states in Home Assistant.

{
  "id": 19,
  "type": "get_states"
}

The server will respond with a result message containing the states.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": [ ... ]
}

Fetching config
This will get a dump of the current config in Home Assistant.

{
  "id": 19,
  "type": "get_config"
}

The server will respond with a result message containing the config.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": { ... }
}

Fetching service actions
This will get a dump of the current service actions in Home Assistant.

{
  "id": 19,
  "type": "get_services"
}

The server will respond with a result message containing the service actions.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": { ... }
}

Fetching panels
This will get a dump of the current registered panels in Home Assistant.

{
  "id": 19,
  "type": "get_panels"
}

The server will respond with a result message containing the current registered panels.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": [ ... ]
}

Pings and pongs
The API supports receiving a ping from the client and returning a pong. This serves as a heartbeat to ensure the connection is still alive:

{
    "id": 19,
    "type": "ping"
}

The server must send a pong back as quickly as possible, if the connection is still active:

{
    "id": 19,
    "type": "pong"
}

Validate config
This command allows you to validate triggers, conditions and action configurations. The keys trigger, condition and action will be validated as if part of an automation (so a list of triggers/conditions/actions is also allowed). All fields are optional and the result will only contain keys that were passed in.

{
  "id": 19,
  "type": "validate_config",
  "trigger": ...,
  "condition": ...,
  "action": ...
}

The server will respond with the validation results. Only fields will be included in the response that were also included in the command message.

{
  "id": 19,
  "type": "result",
  "success": true,
  "result": {
    "trigger": {"valid": true, "error": null},
    "condition": {"valid": false, "error": "Invalid condition specified for data[0]"},
    "action": {"valid": true, "error": null}
  }
}


Error handling
If an error occurs, the success key in the result message will be set to false. It will contain an error key containing an object with two keys: code and message.

{
   "id": 12,
   "type":"result",
   "success": false,
   "error": {
      "code": "invalid_format",
      "message": "Message incorrectly formatted: expected str for dictionary value @ data['event_type']. Got 100"
   }
}


Error handling during service action calls and translations
The JSON below shows an example of an error response. If HomeAssistantError error (or a subclass of HomeAssistantError) is handled, translation information, if set, will be added to the response.

When handling ServiceValidationError (service_validation_error) a stack trace is printed to the logs at debug level only.

{
   "id": 24,
   "type":"result",
   "success": false,
   "error": {
      "code": "service_validation_error",
      "message": "Option 'custom' is not a supported mode.",
      "translation_key": "unsupported_mode",
      "translation_domain": "kitchen_sink",
      "translation_placeholders": {
        "mode": "custom"
      }
   }
}

Read more about raising exceptions or and the localization of exceptions.


REST API
Home Assistant provides a RESTful API on the same port as the web frontend (default port is port 8123).

If you are not using the frontend in your setup then you need to add the api integration to your configuration.yaml file.

http://IP_ADDRESS:8123/ is an interface to control Home Assistant.
http://IP_ADDRESS:8123/api/ is a RESTful API.
The API accepts and returns only JSON encoded objects.

All API calls have to be accompanied by the header Authorization: Bearer TOKEN, where TOKEN is replaced by your unique access token. You obtain a token ("Long-Lived Access Token") by logging into the frontend using a web browser, and going to your profile http://IP_ADDRESS:8123/profile. Be careful to copy the whole key.

There are multiple ways to consume the Home Assistant Rest API. One is with curl:

curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://IP_ADDRESS:8123/ENDPOINT

Another option is to use Python and the Requests module.

from requests import get

url = "http://localhost:8123/ENDPOINT"
headers = {
    "Authorization": "Bearer TOKEN",
    "content-type": "application/json",
}

response = get(url, headers=headers)
print(response.text)

Another option is to use the RESTful Command integration in a Home Assistant automation or script.

turn_light_on:
  url: http://localhost:8123/api/states/light.study_light
  method: POST
  headers:
    authorization: 'Bearer TOKEN'
    content-type: 'application/json'
  payload: '{"state":"on"}'

Successful calls will return status code 200 or 201. Other status codes that can return are:

400 (Bad Request)
401 (Unauthorized)
404 (Not Found)
405 (Method Not Allowed)
Actions
The API supports the following actions:

get
/api/
🔒
get
/api/config
🔒
get
/api/events
🔒
get
/api/services
🔒
get
/api/history/period/<timestamp>
🔒
get
/api/logbook/<timestamp>
🔒
get
/api/states
🔒
get
/api/states/<entity_id>
🔒
get
/api/error_log
🔒
get
/api/camera_proxy/<camera entity_id>
🔒
get
/api/calendars
🔒
get
/api/calendars/<calendar entity_id>?start=<timestamp>&end=<timestamp>
🔒
post
/api/states/<entity_id>
🔒
post
/api/events/<event_type>
🔒
post
/api/services/<domain>/<service>
🔒
post
/api/template
🔒
post
/api/config/core/check_config
🔒
post
/api/intent/handle
🔒
delete
/api/states/<entity_id>
🔒


Validate the input
The configuration.yaml file contains the configuration options for components and platforms. We use voluptuous to make sure that the configuration provided by the user is valid. Some entries are optional or could be required to set up a platform or a component. Others must be a defined type or from an already-defined list.

We test the configuration to ensure that users have a great experience and minimize notifications if something is wrong with a platform or component setup before Home Assistant runs.

Besides voluptuous default types, many custom types are available. For an overview, take a look at the config_validation.py helper.

Types: string, byte, and boolean
Entity ID: entity_id and entity_ids
Numbers: small_float and positive_int
Time: time, time_zone
Misc: template, slug, temperature_unit, latitude, longitude, isfile, sun_event, ensure_list, port, url, and icon
To validate platforms using MQTT, valid_subscribe_topic and valid_publish_topic are available.

Some things to keep in mind:

Use the constants defined in const.py
Import PLATFORM_SCHEMA from the integration you are integrating with and extend it.
Preferred order is required first and optional second
Default values for optional configuration keys need to be valid values. Don't use a default which is None like vol.Optional(CONF_SOMETHING, default=None): cv.string, set the default to default='' if required.
Snippets
This section contains snippets for the validation we use.

Default name
It's common to set a default for a sensor if the user doesn't provide a name to use.

DEFAULT_NAME = "Sensor name"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # ...
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

Limit the values
You might want to limit the user's input to a couple of options.

DEFAULT_METHOD = "GET"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # ...
        vol.Optional(CONF_METHOD, default=DEFAULT_METHOD): vol.In(["POST", "GET"]),
    }
)


Port
All port numbers are from a range of 1 to 65535.

DEFAULT_PORT = 993

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # ...
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

Lists
If a sensor has a pre-defined list of available options, test to make sure the configuration entry matches the list.

SENSOR_TYPES = {
    "article_cache": ("Article Cache", "MB"),
    "average_download_rate": ("Average Speed", "MB/s"),
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # ...
        vol.Optional(CONF_MONITORED_VARIABLES, default=[]): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)

Adding type hints to your code
Type hints in Python are static annotations of variables and functions, to let humans more easily understand the code. See the standard library docs and this PyCascades 2018 talk.

Type hints are not required for all modules at the moment in Home Assistant, but we aim to have a complete as possible coverage. To improve and encourage this, all code is type checked in our continuous integration process and assumes everything is type checked, unless explicitly excluded from type checking.

Adding type hints to an existing codebase can be a daunting task. To speed this up and help developers doing this, Instagram made the monkeytype program. It will analyze calls during runtime and try to assign the correct type hints to the code.

See this instagram blog post for a description of the workflow involved to use the monkeytype program.

We've added a script to start a run of our test suite or a test module and tell the monkeytype program to analyze the run.

Basic workflow
Run script/monkeytype tests/path/to/your_test_module.py.
Run monkeytype stub homeassistant.your_actual_module.
Look at output from the monkeytyped typing stub. If not totally bad, apply the stub to your module. You most likely will need to manually edit the typing in the last step.
Run monkeytype apply homeassistant.your_actual_module.
Check the diff and manually correct the typing if needed. Commit, push the branch and make a PR.
Note: Applying a monkeytyped stub to a module that has existing typing annotations might error and not work. This tool is most useful for totally untyped modules.

Including modules for strict type checking
While we encourage the use of type hints, we currently do not require them for our integrations. By default, our CI checks statically for type hints. In case a module has been fully typed, it can be marked for enabling strict checks, by adding the module to the .strict-typing file that is located at the root of the Home Assistant Core project.

Getting the instance URL
In some cases, an integration requires to know the URL of the users' Home Assistant instance that matches the requirements needed for the use cases at hand. For example, cause a device needs to communicate back data to Home Assistant, or for an external service or device to fetch data from Home Assistant (e.g., a generated image or sound file).

Getting an instance URL can be rather complex, considering a user can have a bunch of different URLs available:

A user-configured internal home network URL.
An automatically detected internal home network URL.
A user-configured, public accessible, external URL that works from the internet.
An URL provided by Home Assistant Cloud by Nabu Casa, in case the user has a subscription.
Extra complexity is added by the fact that URLs can be served on non-standard ports (e.g., not 80 or 443) and with or without SSL (http:// vs https://).

Luckily, Home Assistant provides a helper method to ease that a bit.

The URL helper
Home Assistant provides a network helper method to get the instance URL, that matches the requirements the integration needs, called get_url.

The signature of the helper method:

# homeassistant.helpers.network.get_url
def get_url(
    hass: HomeAssistant,
    *,
    require_current_request: bool = False,
    require_ssl: bool = False,
    require_standard_port: bool = False,
    allow_internal: bool = True,
    allow_external: bool = True,
    allow_cloud: bool = True,
    allow_ip: bool = True,
    prefer_external: bool = False,
    prefer_cloud: bool = False,
) -> str:

The different parameters of the method:

require_current_request Require the returned URL to match the URL the user is currently using in their browser. If there is no current request, an error will be raised.

require_ssl: Require the returned URL to use the https scheme.

require_standard_port: Require the returned URL use a standard HTTP port. So, it requires port 80 for the http scheme, and port 443 on the https scheme.

allow_internal: Allow the URL to be an internal set URL by the user or a detected URL on the internal network. Set this one to False if one requires an external URL exclusively.

allow_external: Allow the URL to be an external set URL by the user or a Home Assistant Cloud URL. Set this one to False if one requires an internal URL exclusively.

allow_cloud: Allow a Home Assistant Cloud URL to be returned, set to False in case one requires anything but a Cloud URL.

allow_ip: Allow the host part of an URL to be an IP address, set to False in case that is not usable for the use case.

prefer_external: By default, we prefer internal URLs over external ones. Set this option to True to turn that logic around and prefer an external URL over an internal one.

prefer_cloud: By default, an external URL set by the user is preferred, however, in rare cases a cloud URL might be more reliable. Setting this option to True prefers the Home Assistant Cloud URL over the user-defined external URL.

Default behavior
By default, without passing additional parameters (get_url(hass)), it will try to:

Get an internal URL set by the user, or if not available, try to detect one from the network interface (based on http settings).

If an internal URL fails, it will try to get an external URL. It prefers the external URL set by the user, in case that fails; Get a Home Assistant Cloud URL if that is available.

The default is aimed to be: allow any URL, but prefer a local one, without requirements.

Example usage
The most basic example of using the helper:

from homeassistant.helpers.network import get_url

instance_url = get_url(hass)

This example call to the helper method would return an internal URL, preferably, that is either user set or detected. If it cannot provide that, it will try the users' external URL. Lastly, if that isn't set by the user, it will try to make use of the Home Assistant Cloud URL.

If absolutely no URL is available (or none match given requirements), an exception will be raised: NoURLAvailableError.

from homeassistant.helpers import network

try:
    external_url = network.get_url(
        hass,
        allow_internal=False,
        allow_ip=False,
        require_ssl=True,
        require_standard_port=True,
    )
except network.NoURLAvailableError:
    raise MyInvalidValueError("Failed to find suitable URL for my integration")


The above example shows a little more complex use of the URL helper. In this case the requested URL may not be an internal address, the URL may not contain an IP address, requires SSL and must be served on a standard port.

If none is available, the NoURLAvailableError exception can be caught and handled.