import os
import sys

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
