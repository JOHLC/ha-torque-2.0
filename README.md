# 🚗 **Torque OBD Custom Integration for Home Assistant**

<p align="center">
  <img src="https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/torque_logger/icon%402x.png" alt="Torque OBD Logo" width="125" />
  <img src="https://brands.home-assistant.io/_/torque/logo@2x.png" alt="Torque OBD Logo" width="300" />
</p>

Bring your car's real-time OBD-II data into Home Assistant using the [Torque Pro](https://torque-bhp.com/) app.<br>
This integration creates sensors for every OBD-II PID that your car reports, enabling automation, visualization, and monitoring of your vehicle.

**⚡️ Modern rewrite of the Torque logger integration for Home Assistant.**<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Note:** This integration replaces the Home Assistant core Torque integration. You cannot run both at the same time.

> **🤖 Disclosure: AI-Powered**<br>
> This integration is maintained and improved with the help of GitHub Copilot among various other AI assistants.<br> 
> I am not a Python coder by any means. Community feedback, contributions, and code reviews are welcome!
---

## 📑 Table of Contents
- [Features](#-features)
- [Installation & Setup](#-installation--setup)
  - [HACS Installation (Recommended)](#-hacs-installation-recommended)
  - [Manual Installation](#-manual-installation)
  - [Integration Setup](#-installation--setup)
  - [Torque App Setup](#-torque-app-setup)
- [Options & Customization](#-options--customization)
- [FAQ & Troubleshooting](#-faq--troubleshooting)
- [Contributing](#-contributing)
- [References](#-references)
- [Support & Feedback](#-support--feedback)

---

## ✨ **Features**
- 🔧 **No YAML required:** Setup is done via the "add integration" page of Home Assistant, through the UI. 
- 💾 **State Restoration:** All sensors (even if Torque is offline) are restored on Home Assistant startup.
- 📝 **Logging:** Detailed logging for troubleshooting and diagnostics.
- 🎨 **Smart Icons:** Sensors use context-appropriate Material Design Icons (e.g., gas-station for fuel, speedometer for speed, etc.).
- 🧩 **Unique IDs & Grouping:** All sensors have unique IDs and are grouped per vehicle for easy management.
- 🚙 **Automatic sensor discovery:** New sensors appear as new PIDs are received from Torque.

**Untested features:**

- 🛠️ **Options Flow for Customization:** Easily hide or rename sensors (by PID) from the Home Assistant UI—no YAML or file editing required.
- 🛡️ **Error Handling:** Malformed or unexpected data is safely ignored and logged for troubleshooting.
- 🏷️ **Device Class & State Class:** Sensors are assigned appropriate `device_class` and `state_class` for better UI and statistics.

---

## 🚀 **Installation & Setup**

#### 🛠️ **HACS Installation (Recommended)**

You can install this integration via [HACS](https://hacs.xyz/) as a custom repository:

1. In Home Assistant, go to **HACS > Integrations**.
2. Click the three dots (⋮) in the top right and select **Custom repositories**.
3. Add this repository URL as type: **Integration**:

   ```
   https://github.com/JOHLC/ha-torque-2.0/
   ```

4. Search for "Torque" in HACS and install this integration.
5. Restart Home Assistant.

#### 🖐️ **Manual Installation**

1. Copy the `torque` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

---
### ➕ **Integration Setup**

1. Add the integration via **Settings > Devices & Services > Add Integration > Torque**.
2. Enter an email address
   - Can be anything, but must match what you enter into the Torque app setup below.
3. Enter a name for the vehicle
   - Example: 2023 Ford EcoSport
4. Click submit then click finish

---

### 📱 **Torque App Setup**
1. Generate a [long-lived access token](https://community.home-assistant.io/t/how-to-get-long-lived-access-token/162159/5?) for your Home Assistant instance. 
   - Give it a good name like 'Torque - Custom' 
2. In the Torque app's main page, go to **Settings > Data Logging & Upload**.
   - Settings from the live data screen and settings from the main page of the app are different.  
3. Under **Logging Preferences**:
    - Tap **Select what to log**.
    - Use the menu to **Add PID to log** and select items of interest.
4. Under **Realtime web upload**:
    - Set the webserver URL to your Home Assistant instance: `https://homeassistant.yourdomain.com/api/torque`
    - Enable 'Send Https: Bearer Token'
    - Set 'Bearer Token' to the long-lived access code you generated in the previous steps.
    - Set your email address to match the one used in the integration setup.
    - Set the 'Logging Interval' to something higher than 10-20 seconds. Anything lower may overload the system.
    - Optional: Enable 'Only when OBD connected. This will ensure Torque is only sending data when it is actually connected to your vehicle. 
    - Enable web uploads
> **🔒 Security Note:**
> If you are exposing your Home Assistant instance to the internet, you should always use SSL/TLS encryption (HTTPS).<br>
Never expose your instance over plain HTTP, as this can put your credentials and data at risk.<br>
See the [Home Assistant documentation on securing your installation](https://www.home-assistant.io/docs/configuration/securing/) for setup instructions.

You should now be all set to start logging data to Home Assistant!
Sensors will be created once Home Assistant recieves valid data from Torque. 

---

## 🙋 **FAQ & Troubleshooting**

- **Sensors missing or not updating?**
    - Check that the Torque app is uploading to the correct URL and using the correct email.
    - Ensure the PIDs you want are enabled in Torque's logging preferences.
    - Force stop the app on your phone, then re-open it.
    - For testing, make sure that "Only when OBD connected" is not enabled under the app's 'Realtime web upload' settings.
    - Check your Home Assistant log for any details. You may also want to enable debug logging (see below).

- **Sensor values look off?**
    - The app may report the unit of measurement in imperial (e.g. mph), but the actual sensor value in metric. The integration assumes the values sent by the Torque app are metric, regardless of the reported unit.
    - If you encounter an issue with this, please open a GitHub issue and I'll do my best to investigate.

### 🔍 **Enabling Debug Logging**

To enable debug logging for this integration, add the following to your `configuration.yaml` and restart Home Assistant. This will show detailed logs from the integration in **Settings > System > Logs**.

> **Note:** This may quickly fill up your log as the logging is quite verbose. Remember to remove or revert back to a less verbose level.

```yaml
logger:
  default: info
  logs:
    custom_components.torque: debug
```

## 📚 **References**

- [Torque Pro App](https://torque-bhp.com/)
- [Home Assistant Custom Integration Docs](https://developers.home-assistant.io/docs/creating_integration_file_structure/)

---

## 📨 **Support & Feedback**

- For questions, suggestions, or bug reports, please [open an issue](https://github.com/JOHLC/ha-torque-2.0/issues) on GitHub.
- Contributions and PRs are welcome!

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
