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


