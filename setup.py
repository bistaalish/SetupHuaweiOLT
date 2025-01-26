import json
import telnetlib
import time
import re
version = ""

def LoadJson(file_path):
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def VerifyConfig(config):
    """Verify the structure and required fields of the configuration."""
    required_fields = ['host', 'username', 'password', 'hostname', 'vlans']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")

    # Verify VLANs structure
    for vlan_name, vlan_info in config['vlans'].items():
        if 'VLANID' not in vlan_info or 'name' not in vlan_info:
            raise ValueError(f"Missing required fields in VLAN '{vlan_name}'")
        # Optional fields can be checked here if needed
        # For example, you can check if 'profile' exists but it's not mandatory
        # if 'profile' not in vlan_info:
        #     print(f"Optional field 'profile' is missing in VLAN '{vlan_name}'")

    print("Configuration verification passed.")

# Login into the OLT
def LoginToTelnet(host, username, password):
    print("[INFO] Login into the OLT")
    """Log in to the Telnet server and return the Telnet object."""
    print(f"Connecting to {host}...")
    tn = telnetlib.Telnet(host)
    
    # Read until the login prompt
    print("Waiting for username prompt...")
    tn.read_until(b">>User name:")
    print("Sending username...")
    tn.write(username.encode('utf-8') + b"\n")
    
    # Read until the password prompt
    print("Waiting for password prompt...")
    tn.read_until(b">>User password:")
    print("Sending password...")
    tn.write(password.encode('utf-8') + b"\n")
    # Read the output after login
    return tn

# Extract ports from output
def boardRegix(data):

    # Split output into lines
    lines = data.splitlines()
    # Initialize an empty list to hold dictionaries
    ports = []
    # Filter lines that contain 'X2CS' or 'SCUN'
    filtered_lines = [line for line in lines if 'X2CS' in line or 'SCUN' in line]

    # Print the extracted lines
    for line in filtered_lines:
        parts = line.split()  # Split by whitespace
        if "Standby" in parts[2]:
            continue
        portid = parts[0]     # The first part is the portid
        portType = parts[1]   # The second part is the portType
        ports.append({"portid": portid, "portType": portType}) 
    # Print the list of dictionaries
    return ports

# Get ports from board
def getBoardInfo(tn):
    print("[INFO] Display Board Information")
    tn.write(b"display board 0\n")
    output = tn.read_until(b'(config)#', timeout=10)
    # print(output.decode('utf-8'))
    ports = boardRegix(output.decode('utf-8'))
    return ports

# Enter Configuration Mode
def EnterConfigurationMode(tn):
    print("[INFO] Enter Configuration Mode:")
    tn.write(b"enable\n")
    tn.write(b"config\n")
    output = tn.read_until(b'(config)#', timeout=10)
    print(output.decode('utf-8'))


# Execute "board confirm 0/<interfaceid>"
def confirmPorts(tn,ports):
    print("[INFO] Execute board confirm")
    for port in ports:
        print(port["portid"])
        comamnd = "board confirm 0/" + port['portid']+"\n"
        tn.write(comamnd.encode("utf-8"))

def addServiceProfile(tn,id,name):
    print(f"[INFO] Adding Service-profile-id: {id}")
    global version
    profile_command = "ont-srvprofile gpon profile-id " + id + " profile-name " + name + "\n"
    print(profile_command)
    command = {
        "MA5683T" : "ont-port pots adaptive eth adaptive\n",
        "MA5600T" : "ont-port pots adaptive 32 eth adaptive 8\n"
    }
    print("[Execute] profile command")
    tn.write(profile_command.encode('utf-8'))
    prompt = "(config-gpon-srvprofile-" + id +")#"
    tn.read_until(prompt.encode('utf-8'))
    pots = command[version]
    tn.write(pots.encode('utf-8'))
    prompt = "{ <cr>|catv<K>|moca<K>|tdm-srvtype<K>|tdm-type<K>|tdm<K>|vdsl<K> }"
    tn.read_until(prompt.encode('utf-8'))
    tn.write(b"\n")
    prompt = "(config-gpon-srvprofile-" + id +")#"
    tn.read_until(prompt.encode('utf-8'))
    tn.write(b"commit\n")
    tn.read_until(prompt.encode('utf-8'))
    tn.write(b"quit\n")
    prompt = "(config)#"
    output = tn.read_until(prompt.encode('utf-8'))
    output = output.decode('utf-8')
    print(output)



# Add VLAN to ports
def AddVlanToPorts(tn,ports,vlan):
    print("[INFO] Add VLAN to ports")
    print(ports)
    for port in ports:
        portId = port['portid']
        portType = port['portType']
        if 'X2CS' in portType:
            interfaces = ["0","1"]
        if 'SCUN' in portType:
            interfaces = ["0","1","2","3"]
        for interface in interfaces:
            print(f'[INFO] Adding VLAN: {vlan} on {portId} {interface}')         
            command = "port vlan " + vlan + " 0/" + portId + " " + interface + "\n"
            tn.write(command.encode("ascii"))
            tn.read_until(b"(config)#")
            time.sleep(1)

# Add DBA Profile
def AddDBAProfile(tn,id,name):
    print("[INFO] Adding DBA-Profile")
    command = "dba-profile add profile-id " + id + " profile-name " + name + " type4 max 1000000" + '\n'
    tn.write(command.encode('utf-8'))
    tn.read_until(b"{ <cr>|priority<K>|weight<K> }:")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.read_until(b"(config)#")
    print(f"Added DBA-PROFILE-id: {id}")


# Configure OLT
def configureOLT(tn,config):
    print("[INFO] Begin OLT Configurations")
    hostname = config['hostname']
    vlans = config["vlans"]
    ports = getBoardInfo(tn)
    # print(ports)
    confirmPorts(tn,ports)
    print("[INFO] board confirmed....")
    setHostname(tn,hostname)
   
    configureVLANs(tn,vlans,ports)
    print("[INFO] Hostname Added....")

# Add VLAN to OLTs
def addVlans(tn,vlan):
    print("[INFO] 1.1 Adding VLAN:", vlan)
    command = "vlan " + vlan + " smart\n"
    tn.write(command.encode('utf-8'))
    # tn.read_until(b"(config)#")
    time.sleep(1)

def addLineProfile(tn,id,name,vlan):
    print(f"[INFO: Lineprofile] Adding profile: {id}")
    # Enter into the profile
    profile_command  = "ont-lineprofile gpon profile-id " + id + " profile-name " + name + "\n"
    tn.write(profile_command.encode('utf-8'))
    prompt = "(config-gpon-lineprofile-"+id+")#"
    tn.read_until(prompt.encode('utf-8'))
    

    # Create tcont
    print(f"[INFO: Lineprofile] Creating tcont: {id}")
    tcont = "tcont 1 dba-profile-id " + id + "\n"
    tn.write(tcont.encode('utf-8'))
    # tn.read_until(prompt.encode('utf-8'))
    output = tn.read_until(prompt.encode('utf-8'))
    output = output.decode('utf-8')
    print(output)

    # Create gem profile 
    print(f"[INFO: Lineprofile] Creating gem profile: {id}")
    gem = "gem add 1 eth tcont 1\n"
    tn.write(gem.encode('utf-8'))
    prompt = "{ <cr>|cascade<K>|downstream-priority-queue<K>|encrypt<K>|gem-car<K>|priority-queue<K> }:"
    output = tn.read_until(prompt.encode('utf-8'))
    output = output.decode('utf-8')
    print(output)
    tn.write(b"\n")
    prompt = "(config-gpon-lineprofile-"+id+")#"
    tn.read_until(prompt.encode('utf-8'))

    # Create gem mapping 
    print(f"[INFO: Lineprofile] Creating gem mapping: {id}")
    gem_mapping = "gem mapping 1 0 vlan " + vlan + "\n"
    tn.write(gem_mapping.encode('utf-8'))
    prompt = "{ <cr>|flow-car<K>|priority<K>|transparent<K> }:"
    tn.write(b"\n")
    prompt = "(config-gpon-lineprofile-"+id+")#"
    
    # Commit
    tn.write(b"commit\n")
    prompt = "(config-gpon-lineprofile-"+id+")#"
    tn.read_until(prompt.encode('utf-8'))

    tn.write(b"quit\n")


    
# Configure VLANS for olt
def configureVLANs(tn,vlans,ports):
    for vlanName in vlans:
        vlanID = vlans[vlanName]["VLANID"]
        # print(vlans[vlan]["VLANID"])
        print("Creating VLAN: ",vlanID)
        addVlans(tn,vlanID)
        AddVlanToPorts(tn,ports,vlanID)
        time.sleep(1)
        if vlanName == "MGMT":
            time.sleep(2)
            configureManagementVLAN(tn,vlans[vlanName])
            continue
        profileID = vlans[vlanName]["profile"]
        AddDBAProfile(tn,profileID,vlanName)
        addServiceProfile(tn,profileID,vlanName)
        addLineProfile(tn,profileID,vlanName,vlanID)

# Check OLT version
def displayOLTVersion(tn):
    print("[INFO] Checking OLT Version")
    tn.write(b"display version\n")
    # tn.read_until(b"{ <cr>|backplane<K>|frameid/slotid<S><Length 1-15> }:")
    time.sleep(1)
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    tn.write(b"\n")
    time.sleep(1)
    output = tn.read_until(b" Uptime")
    output = output.decode("utf-8")
    # tn.write(b"q\n")
    # Regular expression to extract the PRODUCT value
    match = re.search(r'PRODUCT\s*:\s*(\S+)', output)
    product = match.group(1)  # Extract the matched value
    print(f"[INFO] OLT Version is: {product}")
    return product

def configureManagementVLAN(tn,vlanDetails):
    print(f'[INFO] IP Address to: {vlanDetails["VLANID"]} as {vlanDetails['IP']}')
    interface = "interface vlanif " + vlanDetails['VLANID'] +"\n"
    tn.write(interface.encode('utf-8'))
    time.sleep(1)
    ip_command = "ip address " + vlanDetails["IP"] + " " + vlanDetails["subnet"] + "\n"
    time.sleep(1)
    output = tn.read_until(b"vlanif"+vlanDetails['VLANID'].encode("utf-8")+b")#")
    tn.write(b"ip address 100.126.255.111 255.255.255.0\n")
    tn.read_until(b"{ <cr>|description<K>|sub<K> }:")
    tn.write(b"\n")
    tn.read_until(b"vlanif"+vlanDetails['VLANID'].encode("utf-8")+b")#")
    tn.write(b"quit\n")
    output = tn.read_until(b"(config)#")
    print(output)
    # time.sleep(1)
    # tn.write(b"quit\n")
    # time.sleep(1)

    

def setHostname(tn,hostname):
    command = "sysname " + hostname + "\n"
    tn.write(command.encode('utf-8'))
    print("[INFO] Hostname Added....")


def main():
    # Load configuration from data.json
    config = LoadJson('data.json')
    print("Configuration loaded:")
    
        # Verify the configuration
    try:
        VerifyConfig(config)
    except ValueError as ve:
        print(f"Configuration error: {ve}")
        return
    
    # Extract the configuration values
    host = config['host']
    username = config['username']
    password = config['password']
    hostname = config['hostname']
    # Log in to the Telnet server
    try:
        tn = LoginToTelnet(host, username, password)
        global version
        version = displayOLTVersion(tn)
        EnterConfigurationMode(tn)
        configureOLT(tn,config)
        print("[INFO] OLT successfully configured")
        # print(displayOLTVersion(tn))
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        tn.close()

if __name__ == "__main__":
    print("[INFO] program begin")
    main()