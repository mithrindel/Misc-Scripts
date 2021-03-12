import os
import argparse
import paramiko
import getpass
import socket
import re
import sys
import time


#GLOBAL VARIABLES
GLOBAL_SLEEP_TIMER = 2
GLOBAL_BUFFER_SIZE = 8192
LOGGING_FILE = 'logging'
TEMPLATE_FILE ='template'
PATTERN = "logging host"

#function to parth python function call arguments
def args():
    parser = argparse.ArgumentParser(description='An awesome Python Program to search through switches and configure default TFO CH setting.')
    parser.add_argument('-f', '--hosts',help='Specify a hosts file',required=True)
    parser.add_argument('-t', '--template',help='Specify a template config to apply',required=True)

    arg = vars(parser.parse_args())

    global hosts_file,template
    hosts_file = arg['hosts']
    template = arg['template']

#get in the template file the pattern to search for
def get_pattern_to_find():

    global configList
    configList = []
    i=0
    file = open(TEMPLATE_FILE, 'r')

    for line in file:
        if line[0] != '#':
            configList.append(line)
        i = i +1
    configList
    print (configList)

#function to enter user credentials
def creds():
    global username, password, en_password
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*   Welcome to Cisco Template Configurtor Assistant         *')
    print ('\t*                                                           *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n Please enter username, password, and enable password:\n')
    print ('\t(Note that Username is the only one that shows up while typing, passwords are not shown.)\n\n')
    username = input(' Enter Username: ')
    password =  getpass.getpass(' Enter Password: ')
    en_password = getpass.getpass(' Enter Enable Password: ')

#connect to the equipment
def connect(ip):
    global remote_conn
    global host
    global client

    ##retrieve network admin credential to allow connection to device
    #creds()
    username = ''
    password = ''
    en_password = ''

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn = ()
    try:
        print ('\n----- CONNECTING TO %s -----\n' % ip)
        client.connect(ip,username=username,password=password,look_for_keys=False,allow_agent=False,timeout=10)
        print ('\t*** SSH session established with %s ***' % ip)
        remote_conn = client.invoke_shell()
        output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
        time.sleep(0.25)
        if '#' not in str(output).encode("utf-8"):
            remote_conn.send('en\n')
            time.sleep(0.25)
            print ('\t*** Sending Enable Password ***')
            remote_conn.send(en_password)
            remote_conn.send('\n')
            time.sleep(0.25)
            output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
        if '#' in str(output).encode("utf-8"):
            print ('\t*** Successfully Entered Enable Mode ***')
            #disable terminal paging (---more---)
            remote_conn.send('terminal length 0\n')
            time.sleep(0.25)
            output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
        else:
            print ('\t*** Incorrect Enable Password ***')
    except paramiko.SSHException:
        print ('\t*** Authentication Failed ***')
    except socket.error:
        print ('\t*** %s is Unreachable ***' % host)

# Get logging information
def get_config_extract():

    #list of extracted config matching pattern searched
    global config_extract
    config_extract = []

    remote_conn.send('sh run | inc logging host\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    #receive the commande sent and ignore it
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    #filling up the structure with the matched config
    config_extract = (str(output).encode("utf-8")).split('\r\n')
    del config_extract[len(config_extract)-1]
    print ('\t*** Config Successfully Extracted ***')

#check if logging outdated logging server is present
def check_old_logging_srv():
    file = open(LOGGING_FILE, 'r')
    get_pattern_to_find()
    remote_conn.send('sh run | inc logging host\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    print("output 1:\n %s" % output)
    #time.sleep(GLOBAL_SLEEP_TIMER)
    #output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    #print("output 2: %s" % output)

    file = open(LOGGING_FILE, 'w')
    string = str(output).encode("utf-8")
    file.write(string.rstrip())
    file.write('\n')
    file.close()

#check extract config from the switch with new config and generate cleaning file to load
def compare_configs():
    cleaning_script = []

    for confExtract in config_extract:
        for i in range (0, len(configList)):
            string_test = (configList[i]).replace('\n','')
            if string_test == confExtract:
                print("They are equal")
            else:
                print("They are not equal")
            print("\n\n")

if __name__ == '__main__':
    args()
    get_pattern_to_find()
    if os.path.isfile(hosts_file):
        myfile = open(hosts_file, 'r')
        for ip in myfile:
            host = ip
            ip = ip.strip('\n')
            connect(ip)
            get_config_extract()
            compare_configs()
            generate_cleaning_script()
            inject_new_config()
            client.close()


#    main_menu()
