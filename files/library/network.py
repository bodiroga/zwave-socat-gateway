#!/usr/bin/python

import socket
import subprocess
import re
import os

def getLocalIpAddress(type):
    try:
        ifconfig_result = subprocess.check_output("/sbin/ifconfig")
        if type == "ethernet": interface = "eth0"
        elif type == "wifi": interface = "wlan0"
        else: interface = "unknown"
        ip_search = re.compile(ur'%s.*\s+(Direc. inet|inet addr):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' % (interface))
        ip_result = re.search(ip_search, ifconfig_result)
        if ip_result:
            return ip_result.group(2)
        else:
            return None
    except:
        return None

def getRemoteServerStatus(server_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, 22))
        s.close()
        return 1
    except Exception as e:
        s.close()
        return 0


def getZwaveStickStatus(zwave_stick_path):
    try:
        if os.path.exists(zwave_stick_path):
            return True
        else:
            return False
    except:
        return False

def updateLogFile(server_user, server_host, file, room_name):
    try:
        cat_command =  "cat > %s.log" % (room_name)
        command = 'echo "%s" | ssh -oStrictHostKeyChecking=no %s@%s "%s"' % (repr(file), server_user, server_host, cat_command)
        print command
        subprocess.Popen(command, shell=True)
        return 1
    except:
        return 0
