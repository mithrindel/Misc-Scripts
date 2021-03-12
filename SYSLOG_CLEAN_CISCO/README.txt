* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                           *
*   Welcome to Cisco Template Configurtor Assistant         *
*                                                           *
*                                                           *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

---FILES---
- README.txt: this file
- script_launch.sh: script to launch the execution of the program
- cleanup.sh: script to delete temp file generated during program execution
- host.conf: list of equipments (ip or dns name) to connect to
- template: template config file to be applied on the equipments
- clean_config_template.py: actual python script

---HOW TO---
***Program Launch***
- Launch the program using the script "script_launch.sh"
- script_launch.sh will clean up the folder and remove the old temp file (in case the program did not exited properly the previous time
- after cleanup the python script clean_config_template.py is launched

**Script Usage***
- On the welcome menu screen, choose the option 3 to start connecting to the first equipments form the list host.conf
- At the prompt fill up the username and enable credentials -> remark: the same credentials will be used to connect to all the devices
- The script connect to the device and retrieve the global settings. It then prompts to choose between 4 options:
	1/ display info retrieved
	2/ clean up existing config
	3/ inject the template config onto the device
	4/ save change (write mem)
	5/ Main Menu allow to switch to the next device of the host.conf list
