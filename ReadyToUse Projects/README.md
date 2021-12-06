# Ready to Use Qgis Projects

## Explaining the idea
At my job we often need to configure a QGS file for each employee on the project, setting the layers, colours, servers and user configs. 
This code was made to automate this work, we just need set up one project and just handle a bit of information to share with everyone!

## How to work
The code will get an original QGis project file (.qgs) and gonna insert the user input data on that.

## How to set up the original project
*A project file go along with the code for examples!*
1) Configure how you want to share the layers positions, labels and anything else.
2) With a Text editor (Preference to the Notepad++) replace the main info as:


           Host - INPUTSERVERHOST
           Port - INPUTSERVERPORT
           Database - INPUTSERVERDB
           Username - INPUTLOGINUSER
           Password - INPUTLOGINPASSWORD
 
3) Put the modified file on the main code folder and run the code, be careful while filling the interface fields.

A ready-to-use project file will be created on the Documents folder of the user. 


### Using this code on Windows
To use this code on Windows OS it will need to adapt the file paths, easily replacing "/" by "\".
