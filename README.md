# 🚗 Torque OBD Custom Integration for Home Assistant

> **⚡️ This is a modern, AI-powered rewrite of the default Torque logger for Home Assistant**
> 
> **🤖 Disclosure:** The author is not a Python coder—this project is powered by AI (GitHub Copilot and similar tools) based on user prompts. Contributions, suggestions, and code reviews are welcome!

Bring your car's real-time data into Home Assistant using the [Torque Pro](https://torque-bhp.com/) OBD-II app. 
This integration creates dynamic sensors for every OBD-II PID your car reports, so you can automate, visualize, and monitor your vehicle.

---

## ✨ Features

- 🚙 **Automatic Sensor Discovery:** New sensors appear instantly as new PIDs are received from Torque.
- 💾 **State Restoration:** Sensor values survive Home Assistant restarts.
- 🕒 **Throttled Updates:** Sensors update at most once every 10 seconds to prevent overloading the system.
- 🏷️ **User-Friendly Names & Units:** Sensors are clearly named and use the right units, straight from Torque.
- 🛠️ **Easy Setup:** Configure everything from the Home Assistant UI—no YAML configuration required.
- 📝 **Logging:** Get more detailed logging for troubleshooting.
- 🛠️ **Ability to customize sensors in UI:** This integration attempts to create unique IDs for all sensors so that customization (like changing display name or entity_id) is possible in the Home Assistant UI. 
---

## 🚀 Installation

1. Copy the `torque` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and search for "Torque".
4. Enter your email (as set in the Torque app) and an optional vehicle name.

---
## 📱 Torque App Setup

1. In the Torque app, go to **Settings > Data Logging & Upload**.
2. Under **Logging Preferences**:
   - Tap **Select what to log**.
   - Use the menu to **Add PID to log** and select items of interest.
3. Under **Realtime Web Upload**:
   - Enable **Upload to web-server**.
   - Set the Web-server URL to:
     - `https://YOUR_HA_HOST/api/torque`
     - or `https://YOUR_HA_HOST:PORT/api/torque`
   - (Recommended) Enable **Send https: Bearer Token** (Torque Pro 1.12.46+).
   - Paste a Home Assistant [**Long-Lived Access Token**](https://community.home-assistant.io/t/how-to-get-long-lived-access-token/162159) in the **Set Bearer Token** field.
   - Enter any non-empty string in **User Email Address** (must match the email you use in the integration setup).
   - Set the **Web Logging Interval** (I would suggest nothing lower than 10 seconds; higher values may cause system overload or use unnecessary data).

> **🔒 Security Note:**
> If you are exposing your Home Assistant instance to the internet, you should always use SSL/TLS encryption (HTTPS). Never expose your instance over plain HTTP, as this can put your credentials and data at risk. See the [Home Assistant documentation on securing your installation](https://www.home-assistant.io/docs/configuration/securing/) for setup instructions.
---

## ⚙️ Configuration
- **Email:** Must match the email set in the Torque app's web server settings.
- **Vehicle Name:** Optional, used to group sensors by vehicle.

---

## 📊 Usage
- Sensors appear automatically as data is received from the Torque app.
- Each sensor is named after your vehicle and the reported PID (e.g., `2017 Ford Fusion Engine RPM`).
- Units of measurement are set based on the data from Torque.
- Sensors update at most once every 10 seconds (configurable in code).

---

## 🏁 Example Sensors
- Engine RPM
- Speed (OBD)
- Fuel Level
- Intake Air Temperature
- Tire Pressure (per wheel)
- Distance travelled with MIL/CEL lit (distance driven while the check engine light was on)

---

## ℹ️ Notes
- **Multiple Vehicles:** You can add this integration multiple times (with different emails/vehicle names) to monitor more than one car.
- **Sensor Creation:** Sensors are created dynamically as data is received from the Torque app. If you don’t see a sensor, make sure the PID is being logged and sent by the app.
- **Limitations:** Only numeric sensors are supported. Sensors are not created for PIDs that never send data.
- **MIL/CEL:** Stands for "Malfunction Indicator Lamp" or "Check Engine Light". The "Distance travelled with MIL/CEL lit" sensor shows how far you've driven while the check engine light was illuminated.
- **Throttling:** To avoid overloading Home Assistant, sensor updates are throttled. You can adjust the interval in `sensor.py` if needed.
- **State Restoration:** Sensors retain their last value after a Home Assistant restart.

---

## 🐞 Debugging
To enable debug logging, add the following to your `logger.yaml`:

```yaml
logs:
  custom_components.torque: debug
```

---

## 🤝 Support & Contributing
This is a community integration and not officially supported by Home Assistant. For issues, feature requests, or to help make it even better, please open an issue or pull request on the repository!
