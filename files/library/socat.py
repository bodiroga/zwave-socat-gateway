#!/usr/bin/python

import os
import subprocess
import re
import random

## LOCAL SOCAT FUNCTIONS
def getLocalSocatStatus():
    try:
        id = subprocess.check_output("pidof socat", shell=True).strip()
        return 1
    except:
        return 0


def startLocalSocat(device_path):
    try:
        ps = subprocess.Popen("/usr/bin/socat tcp-l:54321,reuseaddr,fork file:%s,raw,nonblock,echo=0" % (device_path), shell=True)
        return 1
    except:
        return 0


def killLocalSocat():
    try:
        subprocess.Popen("killall socat", shell=True)
        return 1
    except:
        return 0


def restartLocalSocat(device_path):
    try:
        killLocalSocat()
        startLocalSocat(device_path)
        return 1
    except:
        return 0

## REMOTE SOCAT FUNCTIONS
def getRemoteSocatStatus(server_user, server_host, zwave_path, zwave_number):
    try:
        ls_command = "ls -la %s%s" % (zwave_path, zwave_number)
        command = "ssh -oStrictHostKeyChecking=no %s@%s '%s'" % (server_user, server_host, ls_command)
        response = subprocess.check_output(command, shell=True)
        print("El estado del puerto zwave remoto es: %s" %response)
        return 1
    except:
        return 0

def startRemoteSocat(server_user, server_host, zwave_path, zwave_number):
    try:
        random_port = startRemotePort(server_user, server_host)
        if random_port:
            nohup_command = "nohup /usr/bin/socat pty,link=%s%s,echo=0,raw,waitslave tcp:localhost:%s" % (zwave_path, zwave_number, random_port)
            sh_command = "sh -c '%s'" % (nohup_command)
            socat_command = 'ssh -oStrictHostKeyChecking=no -n -f %s@%s "%s"' % (server_user, server_host, sh_command)
            subprocess.Popen(socat_command, shell=True)
            return 1
        return 0
    except:
        return 0

def killRemoteSocat(server_user, server_host, zwave_path, zwave_number):
    try:
        grep_command = "grep 'zwave%s,echo=0'" % (zwave_number)
        awk_command = "awk '{print $2}'"
        command_ids = 'ssh -oStrictHostKeyChecking=no -n -f %s@%s "ps aux | %s | %s"' % (server_user,server_host, grep_command, awk_command)
        lines = subprocess.check_output(command_ids, shell=True)
        ids = re.findall(re.compile(ur'%s\s+(\d{1,5})\s+' %(server_user)), lines)
        if len(ids) < 3:
            print "No hay ningun proceso en ejecucion en el servidor"
            return 1
        del ids[-1]
        del ids[-1]
        command_kill = 'ssh -oStrictHostKeyChecking=no -n -f %s@%s "kill -9 %s"' % (server_user,server_host, ' '.join(ids))
        subprocess.check_output(command_kill, shell=True)
        command_rm = 'ssh -oStrictHostKeyChecking=no %s@%s "rm %s%s"' % (server_user, server_host, zwave_path, zwave_number)
        subprocess.check_output(command_rm, shell=True)
        return 1
    except:
        return 0


def restartRemoteSocat(server_user, server_host, zwave_path, zwave_number):
    try:
        killRemoteSocat(server_user, server_host, zwave_path, zwave_number)
        startRemoteSocat(server_user, server_host, zwave_path, zwave_number)
        return 1
    except:
        return 0

def startRemotePort(server_user, server_host):
    try:
        random_port = random.randint(50000, 58000)
        command = "ssh -oStrictHostKeyChecking=no -f -N -R %s:localhost:54321 %s@%s -o ConnectTimeout=5" % (random_port, server_user, server_host)
        subprocess.Popen(command, shell=True)
        return random_port
    except:
        return 0

