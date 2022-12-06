
#pip install paramiko
import paramiko

import json
import sys
import os
import csv
from dotenv import load_dotenv

#load dotenv to load in JWT manual token
load_dotenv()
crestron_user = os.getenv('CRESTRON_U')
crestron_pass = os.getenv('CRESTRON_P')
crestron_change = os.getenv('CRESTRON_CHG')


with open('crestron_list.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    devices = []
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            devices.append(row[0])


loaded = len(devices)
print("Devices loaded: ", loaded)
input("press any key to continue:")







for device in devices:
    try:
        print(device)
        p = paramiko.SSHClient()
        p.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # This script doesn't work for me unless this line is added!
        p.connect(device, port=22, username="crestron", password="")
        stdin, stdout, stderr = p.exec_command("version")
        opt = stdout.readlines()
        opt = "".join(opt)
        print(opt)



        stdin, stdout, stderr = p.exec_command("auenable on")
        opt = stdout.readlines()
        opt = "".join(opt)
        print(opt)

        stdin, stdout, stderr = p.exec_command("autime 20:00")
        opt = stdout.readlines()
        opt = "".join(opt)
        print(opt)

        stdin, stdout, stderr = p.exec_command(f"SNTP SERVER:{IP_ADDRESS}")
        opt = stdout.readlines()
        opt = "".join(opt)
        print(opt)

        p.close()
    except paramiko.AuthenticationException:
            print("AUTH ERROR")
    except paramiko.SSHException as SSHException:
        print("cannot connect %s" % SSHException)
    finally:
        p.close()