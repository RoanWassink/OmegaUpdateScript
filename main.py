import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
from datetime import datetime
import time
from itertools import repeat
import logging
import subprocess
import ipaddress
import yaml
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException
from netmiko.ssh_exception import NetMikoTimeoutException

# Prompt the user to input a network address
def aipFinder(net_addr):


    # Create the network
    ip_net = ipaddress.ip_network(net_addr)

    # Get all hosts on that network
    all_hosts = list(ip_net.hosts())

    # Configure subprocess to hide the console window
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE

    device_type = "linux"
    username = "root"
    password = ''
    file = open(r'devices.yaml', 'w')

    # For each IP address in the subnet,
    # run the ping command with subprocess.popen interface
    for i in range(len(all_hosts)):
        output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])], stdout=subprocess.PIPE,
                                  startupinfo=info).communicate()[0]

        if "Destination host unreachable" in output.decode('utf-8'):
            print(str(all_hosts[i]), "is Offline")
        elif "Request timed out" in output.decode('utf-8'):
            print(str(all_hosts[i]), "is Offline")
        else:
            print(str(all_hosts[i]), "is Online")
            dict_file = [{"device_type": device_type, "host": str(all_hosts[i]), "username": "root", "global_delay_factor": 10, "password": password}]
            documents = yaml.dump(dict_file, file)

    return ''
    ######################################################################################################################################################


netmiko_exceptions = (NetMikoTimeoutException,
                     NetMikoAuthenticationException)
logging.getLogger("paramiko").setLevel(logging.DEBUG)

logging.basicConfig(
    filename="update.log",
    filemode='a',
    format = '%(threadName)s %(name)s %(levelname)s: %(message)s',
    level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
start_msg = '===> {} Connection: {}'
received_msg = '<=== {} Received: {}'




def send_show(device_dict, command):

    ip = device_dict['host']
    update_klaar = open("geupdate.txt", 'w')
    logging.info(start_msg.format(datetime.now().time(), ip, command))
    tijd = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    if ip == '192.168.100.1': time.sleep(5)
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        result = ssh.send_config_set(command)
        logging.debug(received_msg.format(datetime.now().time(), ip, command))
        if "Update succesful" in result:
            print(ip + " update sucessful")
            update_klaar.write(tijd + " "+ ip + " Gelukt")
        else:
            update_klaar.write(tijd +" "+ ip + ' update gefaald ')
    return {ip: result[0:10]}


def send_command_to_devices(devices, command):
    data = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_ssh = [
            executor.submit(send_show, device, command) for device in devices
        ]
        for f in as_completed(future_ssh):
            try:
                result = f.result()
            except netmiko_exceptions as e:
                print(e)
            else:
                data.update(result)
    return data

tftp = '172.16.201.70'
commands = ['tftp -gr blup.sh 172.16.201.70', 'echo tftphost=172.16.201.70 > /tmp/serverparams.conf', 'chmod 0777 blup.sh', './blup.sh']

if __name__ == '__main__':
    if os.path.exists('devices.yaml'):
        answer = input("Lijst bestaat al, opnieuw scannen?")
        if answer == "n":
            with open('devices.yaml') as f:
                devices = yaml.safe_load(f)
                pprint(send_command_to_devices(devices, commands))
        elif answer == "y":
            net_addr = input("Voer netwerk ip in met subnet(bijv.192.168.1.0/24): ")
            aipFinder(net_addr)
            with open('devices.yaml') as f:
                devices = yaml.safe_load(f)
                pprint(send_command_to_devices(devices, commands))