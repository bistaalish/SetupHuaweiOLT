# OLT Configuration Automation

This project provides a Python script to automate the configuration of Optical Line Terminals (OLTs) using Telnet. It simplifies the setup process, such as adding VLANs, configuring service and line profiles, and managing ports, ensuring efficient and consistent configurations.

## Features

- **Load Configurations:** Read configuration data from a JSON file.
- **Telnet Login:** Automates login to the OLT via Telnet.
- **Board Information:** Retrieves and parses board details.
- **Port Management:** Confirms and configures ports for VLANs.
- **VLAN Configuration:** Automates VLAN creation and mapping to ports.
- **Service Profile Management:** Adds and configures GPON service profiles.
- **Line Profile Management:** Adds and configures GPON line profiles.
- **DBA Profile Management:** Automates DBA profile creation.

---

## Requirements

### Software Dependencies

- Python 3.12
- Libraries:
  - `json`
  - `telnetlib`
  - `time`
  - `re`

### Supported OLT Models

- MA5683T
- MA5600T

### Configuration JSON Structure

```json
{
    "host" : "10.11.104.2",
    "username" : "root",
    "password" : "admin",
    "hostname" : "test-HUAWEI-OLT1",
    "vlans" : {
        "PPoE" : {
            "VLANID" : "100",
            "name" : "FLINK-PPOE",
            "profile" : "20"
        },
        "MGMT": {
            "VLANID" : "101",
            "IP" : "100.126.255.111",
            "subnet": "255.255.255.0",
            "name" : "FLINK-MGMT"
        },
        "Dedicated" : {
            "VLANID" : "102",
            "name" : "FLINK-Dedicated",
            "profile" : "30"
        },
        "SME_private" : {
            "VLANID" : "103",
            "name" : "FLINK-SME-EASTERN",
            "profile" : "40"
        } 
    }
}
```
## Setup Instructions

### 1. Clone the Repository
Clone this repository to your local machine:

```bash
https://github.com/bistaalish/SetupHuaweiOLT.git
cd olt-automation
```

### 2. Create a Virtual Environment (Optional but Recommended)

Using a virtual environment helps to isolate dependencies and ensure that your system's global Python environment is unaffected by the project's libraries. Follow these steps to create and activate a virtual environment:

#### 1. Create the Virtual Environment
Run the following command to create a virtual environment named `venv`:

```bash
python3 -m venv venv
```

#### 2. Activate the Virtual Environment

To activate the virtual environment, use the following commands based on your operating system:

- **Linux/macOS**:
```bash
  source venv/bin/activate
```

- **Windows**:
```bash
    venv\Scripts\activate
```
### 3. Install Dependencies

Once the virtual environment is activated, install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

### 4. Configure the JSON File

Create a configuration JSON file based on the provided structure or modify the existing one in the project directory. Ensure that you correctly specify the OLT's details, including IP address, username, password, and VLAN configurations.

```json
{
    "host" : "10.11.104.2",
    "username" : "root",
    "password" : "admin",
    "hostname" : "test-HUAWEI-OLT1",
    "vlans" : {
        "PPoE" : {
            "VLANID" : "100",
            "name" : "FLINK-PPOE",
            "profile" : "20"
        },
        "MGMT": {
            "VLANID" : "101",
            "IP" : "100.126.255.111",
            "subnet": "255.255.255.0",
            "name" : "FLINK-MGMT"
        },
        "Dedicated" : {
            "VLANID" : "102",
            "name" : "FLINK-Dedicated",
            "profile" : "30"
        },
        "SME_private" : {
            "VLANID" : "103",
            "name" : "FLINK-SME-EASTERN",
            "profile" : "40"
        } 
    }
}
```
### 5. Run the Script

To execute the script and automate the OLT configuration process, run the following command:

```bash
python olt_configuration.py
```

Ensure that the JSON configuration file is in the same directory as the script or specify its path as an argument to the script if needed.
