import grpc
from concurrent import futures
import CP_Server_pb2
import CP_Server_pb2_grpc
import configparser

CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read("config.properties")
SERVER_IP = CONFIG_FILE.get("server", "ip")
SERVER_PORT = CONFIG_FILE.get("server", "port")


def getFileFromServer(fileName):
    channel = grpc.insecure_channel(SERVER_IP + ':' + SERVER_PORT)
    stub = CP_Server_pb2_grpc.ContentProvider_ServerStub(channel)
    response = stub.GetFile(CP_Server_pb2.GetFileRequest(fileName = fileName))
    channel.close()
    print(response)

def serve():
    while True:
        try:
            fileName = input('Enter File Name To Retrieve From Server : ')
            getFileFromServer(fileName)
        except Exception as ex:
            print("Error Retriving File")
            continue

if __name__ == '__main__':
    serve()