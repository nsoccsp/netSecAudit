
import easysnmp
from scapy.all import *
import paramiko
import routeros_api
import time

class DeviceDiscovery:
    def __init__(self):
        self.discovered_devices = {}
        
    def discover_lldp(self, interface):
        """LLDP Discovery"""
        try:
            sniff(iface=interface, filter="ether proto 0x88cc", timeout=30)
            return True
        except Exception as e:
            return str(e)
            
    def discover_cdp(self, interface):
        """CDP Discovery"""
        try:
            sniff(iface=interface, filter="ether host 01:00:0c:cc:cc:cc", timeout=30)
            return True
        except Exception as e:
            return str(e)

    def discover_mikrotik(self, host, username, password):
        """Mikrotik Device Discovery"""
        try:
            connection = routeros_api.RouterOsApiPool(
                host=host,
                username=username,
                password=password,
                port=8728
            )
            api = connection.get_api()
            
            # Get system identity
            identity = api.get_resource('/system/identity').get()
            
            # Get MDP neighbors
            mdp = api.get_resource('/ip/neighbor').get()
            
            # Get interface list
            interfaces = api.get_resource('/interface').get()
            
            return {
                'identity': identity,
                'mdp_neighbors': mdp,
                'interfaces': interfaces
            }
        except Exception as e:
            return str(e)
            
    def discover_mdp(self, interface):
        """Mikrotik Discovery Protocol"""
        try:
            sniff(iface=interface, filter="ether proto 0x00CC", timeout=30)
            return True
        except Exception as e:
            return str(e)

    def discover_cisco(self, host, username, password):
        """Cisco Device Discovery"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command('show cdp neighbors detail')
            return stdout.read().decode()
        except Exception as e:
            return str(e)
