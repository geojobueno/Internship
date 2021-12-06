# Import the code for the dialog
import os
import sys
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from dialog import ConnectProject
from pathlib import Path
from shutil import copyfile, which


#local variables
proj_path = r'project.qgs'
icon_path = r'icon.png'
path_out = os.path.expanduser(r'~/Documents/project.qgs')


#FUNCTIONS
def fixProject(proj_path, field, key, path_out=path_out):
    proj = open(proj_path, 'r')
    fileor = proj.read()
    fileor = fileor.replace(field, key)
    proj.close()
 
    proj = open(proj_path, 'wt')
    proj.write(fileor)
    proj.close()


def fix_all(proj_path, fields_to_replace, keys, path_out=path_out):
    for idx in range(len(fields_to_replace)):
        fixProject(proj_path, fields_to_replace[idx], keys[idx])
    
    message = 'Fields replaced'
    #print(message)
    return message


#INTERFACE
app = QApplication(sys.argv) #aplication
interface = ConnectProject() #get the interface
interface.show() #show the dialog


#Check OK event
result = interface.exec_()
if result == 1:
    #Create a copy of INPUT PROJECT
    copyfile(proj_path, r'_project.qgs')

    #server variables
    host = interface.serverip.text().replace(' ','').replace(',','')  #INPUTSERVERHOST
    port = interface.port.text().replace(' ','')   #INPUTSERVERPORT
    database = interface.database.text()   #INPUTSERVERDB

    #login variables
    user = interface.user.text() #.lower().replace(".","_").replace(' ','')  #INPUTLOGINUSER
    password = interface.password.text()  #INPUTLOGINPASSWORD

    fields_to_replace = ['INPUTSERVERHOST', 'INPUTSERVERPORT', 'INPUTSERVERDB', 
                        'INPUTLOGINUSER', 'INPUTLOGINPASSWORD']
    
    inputs = [host, port, database, user, password]
    fix_all(proj_path, fields_to_replace, inputs)
    copied = copyfile(proj_path, path_out)


    print('--PARAMS--')
    print(f'HOST : {host}')
    print(f'PORT : {port}')
    print(f'USER : {user}')
    hide = '*'*len(password)
    print(f'PASSWORD : {hide}')

    #Come back to the original project
    

print(f'OUTPUT FILE: {copied}')


