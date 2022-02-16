from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
from datetime import datetime
import time
from itertools import repeat
import logging

import yaml
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException
from netmiko.ssh_exception import NetMikoTimeoutException
netmiko_exceptions = (NetMikoTimeoutException,
                     NetMikoAuthenticationException)
logging.getLogger("paramiko").setLevel(logging.WARNING)

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
    logging.info(start_msg.format(datetime.now().time(), ip, command))
    if ip == '192.168.100.1': time.sleep(5)
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        result = ssh.send_command(command)
        logging.debug(received_msg.format(datetime.now().time(), ip, command))
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


if __name__ == '__main__':
    with open('devices.yaml') as f:
        devices = yaml.safe_load(f)
    with open('commands.yaml') as r:
        command_dict = yaml.safe_load(r)
        command_single = command_dict['command']


    #pprint(send_command_to_devices(devices, 'ip addr'))
    #pprint(send_command_to_devices(devices, 'tftp -gr blup.sh 172.16.201.70'))
    #pprint(send_command_to_devices(devices, 'echo tftphost=172.16.201.70 > /tmp/serverparams.conf'))
    #pprint(send_command_to_devices(devices, 'chmod 0777 blup.sh'))
    #pprint(send_command_to_devices(devices, './blup.sh'))
    pprint(send_command_to_devices(devices, command_dict))




