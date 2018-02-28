import socket, json
from typing import Dict, Type, List
from protocol import TPLinkSmartHomeProtocol


class Discover:
    DISCOVERY_QUERY = {"system": {"get_sysinfo": None},
                       "emeter": {"get_realtime": None}}

    @staticmethod
    def discover(protocol: TPLinkSmartHomeProtocol = None,
                 port: int = 9999,
                 timeout: int = 3) -> List[str]:
        """
        Sends discovery message to 255.255.255.255:9999 in order
        to detect available supported devices in the local network,
        and waits for given timeout for answers from devices.

        :param protocol: Protocol implementation to use
        :param timeout: How long to wait for responses, defaults to 5
        :param port: port to send broadcast messages, defaults to 9999.
        :rtype: dict
        :return: Array of json objects {"ip", "port", "sys_info"}
        """
        if protocol is None:
            protocol = TPLinkSmartHomeProtocol()
        
        """
        Sends UDP packets to 255.255.255.255 on Port 9999 to find
        any Smart Devices on local network. If found, sends a list
        of devices IP Address
        """
        target = "255.255.255.255"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)

        req = json.dumps(Discover.DISCOVERY_QUERY)

        encrypted_req = protocol.encrypt(req)
        sock.sendto(encrypted_req[4:], (target, port))

        devices = []

        try:
            while True:
                data, addr = sock.recvfrom(4096)
                ip, port = addr
                info = json.loads(protocol.decrypt(data))
                sysinfo = info["system"]["get_sysinfo"]
                if "type" in sysinfo:
                    type = sysinfo[type]
                elif "mic_type" in sysinfo:
                    type = sysinfo["mic_type"]
                if "smartbulb" in type.lower():
                    devices.append(ip)
        except socket.timeout:
            pass
        return devices
