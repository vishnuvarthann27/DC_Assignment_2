import os
import sys
import json

def getFileList():
    dir = str(os.getcwd())
    pathJoin = "\\ServerFiles\\"
    if sys.platform.startswith('linux'):
        pathJoin = "/ServerFiles/" 
    file_list = os.listdir(dir + pathJoin)
    return file_list

def fileRead(fileName, folder):
    dir = str(os.getcwd())
    pathJoin = "\\" + folder + "\\"
    if sys.platform.startswith('linux'):
        pathJoin = "/" + folder + "/"

    path = dir + pathJoin + fileName
    print(path)
    if os.path.isfile(path):
        text_file = open(path, "r")

        data = text_file.read()

        text_file.close()
 
        return data
    
    else:
        return "File Not Found"
    
def fileWrite(fileName, fileContent):
    dir = str(os.getcwd())
    pathJoin = "\\ServerFiles\\"
    if sys.platform.startswith('linux'):
        pathJoin = "/ServerFiles/"   

    path = dir + pathJoin + fileName

    try:
        with open(path, "w") as file:
            file.write(fileContent)
    except Exception as ex:
        print(ex)

def readMappingFile():
    dir = str(os.getcwd())
    pathJoin = "\\fileMapping.json"
    if sys.platform.startswith('linux'):
        pathJoin = "/fileMapping.json" 
    path = dir + pathJoin 
    input_file = open(path)
    json_array = json.load(input_file)
    return json_array

def writeToMappingFile(data):
    dir = str(os.getcwd())
    pathJoin = "\\fileMapping.json"
    if sys.platform.startswith('linux'):
        pathJoin = "/fileMapping.json" 
    path = dir + pathJoin 

    out_file = open(path, "w")
    json.dump(data, out_file)
