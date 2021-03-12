import os
import argparse
import paramiko
import getpass
import socket
import re
import sys
import time


# Define command line arguments and globals

GLOBAL_SLEEP_TIMER = 2
GLOBAL_BUFFER_SIZE = 8192




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


# Exit commands
def prog_exit():
    for attribute in attribute_list:
        if os.path.isfile(attribute) is True:
            os.remove(attribute)
    sys.exit()


'''***** Main menu and associated functions *************************************************************************'''


'''***** SSH setup, get show cdp neighbor detail and show interface status, parse information into dictionary's *****'''
# SSH and start program

def connect():
    creds()
    global remote_conn
    global host
    if os.path.isfile(hosts_file):
        myfile = open(hosts_file, 'r')
        for ip in myfile:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn = ()
            ip = ip.strip('\n')
            host = ip
            print('-%s-' % host)
            print_host = host
            print_host = print_host.replace('\n', '')
            try:
                print ('\n----- CONNECTING TO %s -----\n' % print_host)
                client.connect("188.24.110.1",
                               username=username,
                               password=password,
                               look_for_keys=False,
                               allow_agent=False,
                               timeout=10)
                print ('\t*** SSH session established with %s ***' % print_host)
                remote_conn = client.invoke_shell()
                output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
                time.sleep(0.25)
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
                    get_config()
                else:
                    print ('\t*** Incorrect Enable Password ***')
            except paramiko.SSHException:
                print ('\t*** Authentication Failed ***')
            except socket.error:
                print ('\t*** %s is Unreachable ***' % host)
            client.close()



# Send show cdp neighbors and interface status

def get_config():
    print ('\t*** Download device global configuration ***\n')
    #get_username()
    #get_enable()
    #get_password_service()
    #get_clock()
    #get_timestamp()
    get_logging()
    get_ntp()
    get_tacacs()
    get_dns()
    #get_http_server()
    get_snmp()
    #get_lines()
    #get_banner()
    print ('\t*** Configuration retrieval: DONE ***\n')
    press_return()
    sh_cmd_outputs()


# Parse interface status file


'''***** Show gathered information in parsed form, show's based on IF statements, and commands /
to configure interfaces, resync information, or move on to next switch **********************************************'''
# Menu for the different shows

def sh_cmd_outputs():
    clear_screen()
    menu_actions = sub_menu_actions
    menu_return = sh_cmd_outputs
    print_host = host
    print_host = print_host.replace('\n', '')
    print ('\n\n\t----------------- Connected to %s -------------------\n\n' % print_host)
    print ('\tPlease Choose an Option From the Following:\n\n')
    print ('\t\t1. Display config info retrieved')
    print ('\n\n\t\t2. Apply cleanup script to device')
    print ('\n\n\t\t3. Inject TFO CH Template configuration')
    print ('\n\n\t\t4. Save changes (WARNING: dangerous command)')
    print ('\n\n\t\t9. Main menu / Quit if no next device in list')
    choice = input('\n\n >> ')
    if choice == '9':
        pass
    else:
        exec_menu(menu_actions, menu_return, choice)
        return

# Get username information

def get_username():
    remote_conn.send('sh run | inc username\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    file = open('username', 'w')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.close()


# Get enable information

def get_enable():
    remote_conn.send('sh run | inc enable password\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    file = open('enable', 'w')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    remote_conn.send('sh run | inc enable secret \n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output2 = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string2 = str(output2, 'utf-8')
    file.write(string2[string2.find('\n')+1:string2.rfind('\n')])
    file.close()


# Get service password-encryption

def get_password_service():
    remote_conn.send('sh run | inc password-encryption\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    file = open('password_service', 'w')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.close()


# Get clock information

def get_clock():
    remote_conn.send('sh run | inc clock\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('clock', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get timestamps information

def get_timestamp():
    remote_conn.send('sh run | inc service timestamps\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('timestamp', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get logging information

def get_logging():
    remote_conn.send('sh run | inc logging\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('logging', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get ntp information

def get_ntp():
    remote_conn.send('sh run | inc ntp\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('ntp', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get tacacs information

def get_tacacs():
    remote_conn.send('sh run | inc tacacs-server\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('tacacs', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


    # Get dns information

def get_dns():
    remote_conn.send('sh run | inc ip name-server\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('dns', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    remote_conn.send('sh run | inc ip domain \n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output2 = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    string2 = str(output2, 'utf-8')
    file.write(string2[string2.find('\n')+1:string2.rfind('\n')])
    file.write('\n')
    file.close()


# Get tacacs information

def get_http_server():
    remote_conn.send('sh run | inc ip http\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('http_server', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get snmp information

def get_snmp():
    remote_conn.send('sh run | inc snmp\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('snmp', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get lines information

def get_lines():
    remote_conn.send('sh run | inc line\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('lines', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Get banner information

def get_banner():
    remote_conn.send('sh run | inc banner\n')
    time.sleep(GLOBAL_SLEEP_TIMER)
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    file = open('banner', 'w')
    string = str(output, 'utf-8')
    file.write(string[string.find('\n')+1:string.rfind('\n')])
    file.write('\n')
    file.close()


# Generate cleaning script command

def cleanup_script_generation():
    print('\n\t *** GENERATING CLEAN_CONFIG FILE ***\n\n')
    clean_config_file = open('clean_config','w')
    for attribute in attribute_list:
        file = open(attribute, 'r')
        for line in file:
            if 'no ' in line or not line.strip(): # if line is already negated or empty
                continue
            clean_config_file.write('no ' + line)
            print('no ' + line)
            time.sleep(0.1)
        file.close()
    clean_config_file.close()


# Clean global config

def cleanup_config():
    cleanup_script_generation()
    file = open('clean_config', 'r')
    print('\n\t *** APPLYING CLEAN_CONFIG FILE ***\n\n')
    remote_conn.send('\n')
    remote_conn.send('conf t\n')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    for line in file:
        remote_conn.send('%s\n' % line)
        time.sleep(0.66)
        output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
        print ('%s' % line)
    remote_conn.send('end\n')
    file.close()
    press_return()
    sh_cmd_outputs()


# Push template config to the device

def push_template_config():
    template_file = open('template','r')
    remote_conn.send('\n')
    remote_conn.send('end\n')
    time.sleep(0.1)
    remote_conn.send('conf t\n')
    output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    for line in template_file:
        if line.startswith("#") and line.endswith("#"):
            print ('%s' % line)
        else:
            remote_conn.send('%s\n' % line)
            time.sleep(0.66)
            print ('%s' % line)
            output = remote_conn.recv(GLOBAL_BUFFER_SIZE)
    remote_conn.send('end\n')
    template_file.close()
    press_return()
    sh_cmd_outputs()


# Display username information

def display_username():
    file = open('username','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display enable information

def display_enable():
    file = open('enable','r')
    for line in file:
        print ('%s\n' % line)
    file.close()

# Display password service information

def display_password_service():
    file = open('password_service','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display clock information

def display_clock():
    file = open('clock','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display timestamp information

def display_timestamp():
    file = open('timestamp','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display logging information

def display_logging():
    file = open('logging','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display ntp information

def display_ntp():
    file = open('ntp','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display tacacs information

def display_tacacs():
    file = open('tacacs','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display dns information

def display_dns():
    file = open('dns','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display http/https server information

def display_http_server():
    file = open('http_server','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display snmp information

def display_snmp():
    file = open('snmp','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display lines information

def display_lines():
    file = open('lines','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display banner information

def display_banner():
    file = open('banner','r')
    for line in file:
        print ('%s\n' % line)
    file.close()


# Display all informations

def display_info():
    #display_username()
    #press_return()
    #display_enable()
    #press_return()
    #display_password_service()
    #press_return()
    #display_clock()
    #press_return()
    #display_timestamp()
    #press_return()
    display_logging()
    press_return()
    display_ntp()
    press_return()
    display_tacacs()
    press_return()
    display_dns()
    press_return()
    #display_http_server()
    #press_return()
    display_snmp()
    press_return()
    #display_lines()
    #press_return()
    #display_banner()
    #press_return()
    sh_cmd_outputs()


# Configure username information as per template

def config_username():
    for item in username_list:
        print ('\t ***Sending ' + item + '\n')
        remote_conn.send(item + '\n')
        time.sleep(GLOBAL_SLEEP_TIMER)
    print ('***Username has been configured')
    press_return()
    sh_cmd_outputs()


# Configure enable information as per template

def config_enable():
    for item in enable_list:
        print ('\t ***Sending ' + item + '\n')
        remote_conn.send(item + '\n')
        time.sleep(GLOBAL_SLEEP_TIMER)
    print ('***Enable has been configured')
    press_return()
    sh_cmd_outputs()


# Configure logging information as per template

def config_logging():
    for item in logging_list:
        print ('\t ***Sending ' + item + '\n')
        remote_conn.send(item + '\n')
        time.sleep(GLOBAL_SLEEP_TIMER)
    print ('***logging has been configured')
    press_return()
    sh_cmd_outputs()


# Configure username information as per template

def config_snmp():
    for item in snmp_list:
        print ('\t ***Sending ' + item + '\n')
        remote_conn.send(item + '\n')
        time.sleep(GLOBAL_SLEEP_TIMER)
    print ('***snmp has been configured')
    press_return()
    sh_cmd_outputs()


# Print IF Interface Status == Trunk or AP Vlan AND no CDP Neighbo

'''*************** Configuration menu and associated functions ******************************************************'''
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




# Press to return
def press_return():
    print ('\n\nPress enter to continue\n')
    raw_input()


# Print IP address list
def sh_host_list():
    try:
        hosts = open(hosts_file, 'r')
        print ('\n\n\tHosts in file: \n')
        for x in hosts:
            print ('\t\t' + x.strip('\n'))
        print ('\n\n')
        hosts.close()
    except IOError:
        print('HostFile does not exist\n')
    press_return()
    main_menu()

# Print IP address list
def sh_template_config():
    template_file = open('template','r')
    for line in template_file:
        print ('%s' % line)
    print ('\n')
    press_return()
    main_menu()


# Printed main menu
def main_menu():
    clear_screen()
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*   Welcome to Cisco Template Config Checker Assistant      *')
    print ('\t*                                                           *')
    print ('\t*                                NEW!!!                     *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n')
    print('\tPlease choose an option from the following:\n\n')
    print ('\t\t1. Show IP addresses of devices to configure in list file\n')
    print ('\t\t2. Show current template info configuration settings\n')
    print ('\t\t3. Generate change config file')
    print ('\n\n\t\t0. Quit')

    choice = 1

    while (choice!=0):
        choice = input('\n\n >> ')
        if choice==1:
            sh_host_list()
        if choice==2:
            sh_template_config()
        if choice==3:
            print("Hello")
            press_return()
            main_menu()
        if choice==0:
            quit()
        else:
            print("Invalid Entry. Please try again\n")



FUNCTION TEST
For all device in file
    check config contains logging old
    clean logging old
    push new config to device
    wr mem
    Recuperer all sh run | inc logging
    for all recuperer
    cleanup_file = no + Recuperer





# Get username and passwords
def creds():
    global username, password, en_password
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*                                                           *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n Please enter username, password, and enable password:\n')
    print ('\t(Note that Username is the only one that shows up while typing, passwords are not shown.)\n\n')
    username = '' #input(' Enter Username: ')
    password =  '' #getpass.getpass(' Enter Password: ')
    en_password = '' #getpass.getpass(' Enter Enable Password: ')


def args():

    #script description and mandatory arguments
    parser = argparse.ArgumentParser(description='An awesome Python Program to search through switches and configure default TFO CH setting.')
    parser.add_argument('-f', '--hosts', help='Specify a hosts file', required=True)
    parser.add_argument('-t', '--template',help='Specify a template config to apply',required=True)

    #script arguments parser
    arg = vars(parser.parse_args())

    #definition of global variables
    #global network_devices = {}
    #global int_sts = {}
    global hosts_file
    hosts_file = arg['hosts']

    attribute_list = [
                    #'username',
                    #'enable',
                    #'password_service',
                    #'clock',
                    #'timestamp',
                    'logging',
                    'dns',
                    'ntp',
                    'tacacs',
                    #'http_server',
                    'snmp',
                    #'lines',
                    #'banner'
                    ]


if __name__ == '__main__':
    args()
    main_menu()
    creds()
