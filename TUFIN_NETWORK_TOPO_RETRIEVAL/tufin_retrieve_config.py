import os
import shutil
import argparse
import paramiko
import getpass
import socket
import re
import sys
import time


'''***** Get command line arguments, set global variables, and define supportive functions **************************'''
# Define command line arguments and globals

GLOBAL_SLEEP_TIMER = 2
GLOBAL_BUFFER_SIZE = 1000000

def args():
    parser = argparse.ArgumentParser(description='An awesome Python Program to parse config for loading into Tufin.')
    parser.add_argument('-f', '--hosts',
                        help='Specify a hosts file',
                        required=True)

    arg = vars(parser.parse_args())

    global main_menu_actions, hosts_file, network_devices, int_sts, attribute_list
    network_devices = {}
    int_sts = {}
    hosts_file = arg['hosts']

    main_menu_actions = {
        'main_menu': main_menu,
        '1': sh_host_list,
        '2': connect,
        '0': prog_exit}

    attribute_list = [
                    'ip_route',
                    'ip_interface'
                    ]


# Send commands to end and wr me

def end_write():
    remote_conn.send('end\n')
    remote_conn.send('wr me\n')
    print ('Configuration saved\n')
    press_return()
    sh_cmd_outputs()


# Clear screen

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Press to return

def press_return():
    print ('\n\nPress enter to go back\n')
    input(' >> ')


# Menu choice validator

def exec_menu(menu_actions, menu_return, choice):
    clear_screen()
    try:
        menu_actions[choice]()
    except KeyError:
        print ('Invalid Selection, Please Try Again.\n')
        time.sleep(1)
        menu_return()


# Exit commands

def prog_exit():
    for attribute in attribute_list:
        if os.path.isfile(attribute) is True:
            os.remove(attribute)
    sys.exit()


'''***** Main menu and associated functions *************************************************************************'''
# Printed main menu

def main_menu():
    clear_screen()
    menu_actions = main_menu_actions
    menu_return = main_menu
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*   Welcome to Tufin Configuration Retrieval Tool           *')
    print ('\t*                                                           *')
    print ('\t*                                                           *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n\tPlease choose an option from the following:\n\n')
    print ('\t\t1. Show IP addresses of the devices to retrieve config from\n')
    print ('\t\t2. Connect to device (or next device in list)')
    print ('\n\n\t\t0. Quit')
    choice = input('\n\n >> ')
    exec_menu(menu_actions, menu_return, choice)
    return


# Print IP address list

def sh_host_list():
    hosts = open(hosts_file, 'r')
    print ('\n\n\tHosts in file: \n')
    for x in hosts:
        print ('\t\t' + x.strip('\n'))
    print ('\n\n')
    hosts.close()
    press_return()
    main_menu()


'''***** SSH setup, get show cdp neighbor detail and show interface status, parse information into dictionary's *****'''
# SSH and start program

def connect():
    creds()
    global remote_conn
    global host
    if os.path.isfile(hosts_file):
        myfile = open(hosts_file, 'r')
        for file_line in myfile:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn = ()
            device_name = file_line.split('#')[0]
            device_ip = file_line.split('#')[1]
            try:
                print ('\n----- CONNECTING TO %s - %s -----\n' %(device_name, device_ip))
                client.connect(device_ip,
                               username=username,
                               password=password,
                               look_for_keys=False,
                               allow_agent=False,
                               timeout=10)
                print ('\t*** SSH session established with %s ***' % device_name)
                remote_conn = client.invoke_shell()
                output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
                output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
                time.sleep(3)
                if '#' not in str(output, 'utf-8'):
                    remote_conn.send('en\n')
                    time.sleep(0.25)
                    print ('\t*** Sending Enable Password ***')
                    remote_conn.send(en_password)
                    remote_conn.send('\n')
                    time.sleep(0.25)
                    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
                if '#' in str(output, 'utf-8'):
                    print ('\t*** Successfully Entered Enable Mode ***')
                    #disable terminal paging (---more---)
                    remote_conn.send('terminal length 0\n')
                    time.sleep(0.25)
                    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
                    get_config(device_name)
                else:
                    print ('\t*** Incorrect Enable Password ***')
            except paramiko.SSHException:
                print ('\t*** Authentication Failed ***')
            except socket.error:
                print ('\t*** %s is Unreachable ***' % device_name)
            client.close()


# Get username and passwords

def creds():
    global username, password, en_password
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*    Welcome to Tufin Configuration Retrieval               *')
    print ('\t*                                                           *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n Please enter username, password, and enable password:\n')
    print ('\t(Note that Username is the only one that shows up while typing, passwords are not shown.)\n\n')
    username = '' #input(' Enter Username: ')
    password =  '' #getpass.getpass(' Enter Password: ')
    en_password = '' #getpass.getpass(' Enter Enable Password: ')


# Send show cdp neighbors and interface status

def get_config(device_name):
    print ('\t*** Download device global configuration ***\n')
    get_ip_route()
    get_ip_interface()
    fichier_final = open(device_name+'_vrf_SGCIB', 'w')
    fichier_final.write(device_name+'#'+'show ip route\n')
    shutil.copyfileobj(open('sh_ip_route', 'r'), fichier_final)
    fichier_final.write(device_name+'#'+'show ip interface\n')
    shutil.copyfileobj(open('sh_ip_interface', 'r'), fichier_final)
    fichier_final.close()
    print ('\t*** Configuration retrieval for %s: DONE ***\n' % device_name)


# Get ip route config
def get_ip_route():
    remote_conn.send('sh ip route vrf SGCIB\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    file = open('sh_ip_route', 'w')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.close()


# Get ip interface config

def get_ip_interface():
        remote_conn.send('sh ip interface\n')
        time.sleep(GLOBAL_SLEEP_TIMER)
        file = open('sh_ip_interface', 'w')
        output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
        string = str(output, 'utf-8')
        file.write(string[string.find('\n')+1:string.rfind('\n')])
        file.close()

# Menu for Configuration

def sh_config_outputs():
    clear_screen()
    menu_actions = config_menu_actions
    menu_return = sh_config_outputs
    print_host = host
    print_host = print_host.replace('\n', '')
    print ('\n\n\t----------------- Connected to %s -------------------\n\n' % print_host)
    print ('\tPlease choose an option from the following:\n\n')
    print ('\t\t1. Replace existing username detail by template details')
    print ('\t\t2. Replace existing enable details by template details')
    print ('\t\t3. Replace existing logging detail by template details')
    print ('\t\t4. Replace existing snmp detail by template details')
    print ('\n\n\t\t9. Back')
    choice = input('\n\n >> ')
    exec_menu(menu_actions, menu_return, choice)
    return

if __name__ == '__main__':
    args()

    main_menu()
