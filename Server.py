import grpc
from concurrent import futures
import CP_Server_pb2
import CP_Server_pb2_grpc
import time
import socket
import fileread
import hashlib

class FileTransmitService(CP_Server_pb2_grpc.ContentProvider_ServerServicer):
    def TransmitFile(self, request, context):
        fileList = fileread.getFileList()

        if(len(fileList) > 0):
            requestHash = hashlib.new("sha256", request.fileContent.encode()).hexdigest()
            for fileName in fileList:
                fileHash = hashlib.new("sha256", fileread.fileRead(fileName, "ServerFiles").encode()).hexdigest()

                if(requestHash == fileHash):
                    if(request.fileName == fileName):
                        response = CP_Server_pb2.TransmitFileResponse(transmitStatus = 'File Already Exist!!!')
                        return response
                    elif(request.fileName != fileName ):
                        mappingDetails =  fileread.readMappingFile()
                        mappingDetails[request.fileName] = fileName
                        fileread.writeToMappingFile(mappingDetails)
                        response = CP_Server_pb2.TransmitFileResponse(transmitStatus = 'File Content Already Exist!!! Mapping Done !!!')
                        return response
                
        fileread.fileWrite(request.fileName, request.fileContent)
        response = CP_Server_pb2.TransmitFileResponse(transmitStatus = 'Success')
        return response
    
    def GetFile(self, request, context):
        fileContent = fileread.fileRead(request.fileName, "ServerFiles")

        if(fileContent != "File Not Found"):
            response = CP_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = fileContent)
            return response
        else:
            mappingDetails =  fileread.readMappingFile()
            if(request.fileName in mappingDetails):
                fileContent = fileread.fileRead(mappingDetails[request.fileName], "ServerFiles")
                response = CP_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = fileContent)
                return response
            else:
                response = CP_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = "File Not Found in server")
                return response

def serve(serverPort):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    CP_Server_pb2_grpc.add_ContentProvider_ServerServicer_to_server(FileTransmitService(), server)
    server.add_insecure_port('[::]:' + serverPort)
    server.start()
    print("Server Listening to Requests...")
    try:
        while True:
            time.sleep(300)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serverPort = '13000'
    serve(serverPort)
