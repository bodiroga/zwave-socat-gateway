#!/usr/bin/python

import os
import time
import threading
import sys
import datetime
from library import files
from library import network
from library import socat

## GLOBAL VARIABLES
server_connection = server_error = False
zwave_stick_connection = zwave_stick_error = False
socat_connection = socat_error = False


## CONTROL FUNCTIONS
# Start all control threads
def start_processes():
    t_zwave = threading.Thread(target=check_zwave_stick_connection).start()
    t_server = threading.Thread(target=check_server_connection).start()
    t_socat = threading.Thread(target=check_socat_connection).start()
    time.sleep(2)

# Checks the zwave stick connection
def check_zwave_stick_connection():
    global zwave_stick_connection
    zwave_stick_path = configuration["ZWAVE_STICK"]
    while(True):
        zwave_stick_connection = network.getZwaveStickStatus(zwave_stick_path)
        time.sleep(5)

# Checks the connectivity with the server
def check_server_connection():
    global server_connection
    server_host = configuration["SERVER_HOST"]
    while(True):
        server_connection = network.getRemoteServerStatus(server_host)
        time.sleep(5)

# Checks both local and remote socats status
def check_socat_connection():
    global socat_connection
    server_user = configuration["SERVER_USER"]
    server_host = configuration["SERVER_HOST"]
    zwave_path = configuration["ZWAVE_HOME"]
    zwave_number = configuration["ZWAVE_NUMBER"]
    while(True):
        if (socat.getLocalSocatStatus() == 1) and (socat.getRemoteSocatStatus(server_user, server_host, zwave_path, zwave_number) == 1):
            socat_connection = True
        else: 
            socat_connection = False
        time.sleep(5)


## LOG FUNCTION
def updateLogFile():
    server_user = configuration["SERVER_USER"]
    server_host = configuration["SERVER_HOST"]
    room_name = configuration["ROOM_NAME"]
    zwave_binding = "zwave"+str(configuration["ZWAVE_NUMBER"])
    ip = network.getLocalIpAddress(configuration["CONNECTION_TYPE"])    
    time = str(datetime.datetime.now())
    file = { "ip":ip, "time":time, "location":room_name, "zwave_binding":zwave_binding, "zwave_stick_status":zwave_stick_connection }
    print file
    network.updateLogFile(server_user, server_host, file, room_name)


# MAIN PROCESS
if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    configuration = files.readConfigFile("%s/CONFIGURATION" % (script_directory))
    if not configuration:
        print "Error al leer el archivo de configuracion"
        sys.exit(1)

    start_processes()

    print "Procesos lanzados, volvemos al main"
    while(True):
        if server_connection:
            print "    Hay conexion con el servidor"
            if server_error: 
                server_error = False
                print "Habia un error de conexion con el servidor pero ya se ha solucionado"
            if zwave_stick_connection:
                print "    El pincho esta bien"
                if zwave_stick_error: 
                    zwave_stick_error = False
                    print "Habia un error con el pincho pero ya se ha solucionado"
                if socat_connection:
                    print "    Socat esta bien"
                    if socat_error: 
                        socat_error = False
                        print "Habia un error con socat pero ya se ha solucionado"
                        socat.restartRemoteSocat(configuration["SERVER_USER"], configuration["SERVER_HOST"], configuration["ZWAVE_HOME"], configuration["ZWAVE_NUMBER"])
                    updateLogFile()
                    time.sleep(int(configuration["REFRESH_INTERVAL"]))
                else:
                    print "    Socat no esta bien"
                    socat_error = True
                    print "Tenemos que volver a lanzar socat aqui y reiniciar socat alli por si acaso"                        
                    updateLogFile()
                    socat.restartLocalSocat(configuration["ZWAVE_STICK"])
                    socat.restartRemoteSocat(configuration["SERVER_USER"], configuration["SERVER_HOST"], configuration["ZWAVE_HOME"], configuration["ZWAVE_NUMBER"])
                    time.sleep(int(configuration["REFRESH_INTERVAL"]))
            else:
                print "    El pincho no esta bien"
                if not zwave_stick_error: 
                    zwave_stick_error = True
                    print "Quitamos socat aqui y alli a la espera de que el pincho vuelva a funcionar"
                    socat.killLocalSocat()
                    socat.killRemoteSocat(configuration["SERVER_USER"], configuration["SERVER_HOST"], configuration["ZWAVE_HOME"], configuration["ZWAVE_NUMBER"])
                updateLogFile()
                time.sleep(int(configuration["REFRESH_INTERVAL"]))
        else:
            print "    No hay conexion con el servidor"
            if not server_error:
                server_error = True
                socat.killLocalSocat()
            time.sleep(int(configuration["REFRESH_INTERVAL"]))
