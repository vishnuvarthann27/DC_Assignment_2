import configparser
import socket
import grpc
import fileread
from concurrent import futures
import CP_Server_pb2
import CP_Server_pb2_grpc
from threading import Thread
import collections
import json
from google.protobuf.json_format import (
    MessageToDict,
)
import time


CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read("config.properties")

MY_HOSTNAME = socket.gethostname()
MY_IP = socket.gethostbyname(MY_HOSTNAME)
IP_LIST = [CONFIG_FILE.get("ip", "0"), CONFIG_FILE.get("ip", "1"), CONFIG_FILE.get("ip", "2")]
SERVER_IP = CONFIG_FILE.get("server", "ip")
SERVER_PORT = CONFIG_FILE.get("server", "port")

IS_IDLE = 1
PORT = ''
HAS_TOKEN = ''

RN = [0, 0 , 0]

TOKEN = {'Q':[], 'LN':[0,0,0]}

class ContentProviderService(CP_Server_pb2_grpc.ContentProvider_ServerServicer):
    def receiveTokenRequest(self, request, context):
        print("Received Token request from Content Provider : " + str(request.processID))
        global HAS_TOKEN
        global IS_IDLE
        RN[request.processID] = max(RN[request.processID], request.seqNumber)
        response = None

        if(RN[request.processID] == TOKEN["LN"][request.processID] + 1  & HAS_TOKEN == 1 & IS_IDLE == 1):
            print("Sending Token To Content Provider : " + str(request.processID))
            HAS_TOKEN = 0
            TOKEN["Q"].append(request.processID)
            response = CP_Server_pb2.requestTokenResponse(token = TOKEN)  
        else:
            response = CP_Server_pb2.requestTokenResponse(requestStatus = 'Success')

        return response
        

    def receiveToken(self, request, context):
        print("Received Token")
        global HAS_TOKEN
        global IS_IDLE
        TOKEN["Q"] = request.Q
        TOKEN["LN"] =  request.LN
        HAS_TOKEN = 1
        response = CP_Server_pb2.sendTokenResponse(requestStatus = 'Success')
        return response
    
def sendTokenRequest(ip_address):
    print("Sending Token Request to : " + ip_address)
    global HAS_TOKEN
    channel = grpc.insecure_channel(ip_address)
    stub = CP_Server_pb2_grpc.ContentProvider_ServerStub(channel)
    response = stub.receiveTokenRequest(CP_Server_pb2.requestTokenRequest(processID = PROCESS_ID, seqNumber = RN[PROCESS_ID]))
    channel.close()
    if(response.requestStatus != "Success"):
        print("Received Token from : " + ip_address)
        data = MessageToDict(
                response.token,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,
                #including_default_value_fields=True,
                )
        TOKEN["Q"] = data["Q"]
        TOKEN["LN"] = data["LN"]
        HAS_TOKEN = 1


def transmitFile(fileName, fileContent):
    global HAS_TOKEN
    global IS_IDLE


    if(HAS_TOKEN != 1):

        RN[PROCESS_ID] = RN[PROCESS_ID] + 1

        my_ip_port = MY_IP+ ":" + PORT
        for ip in IP_LIST:
            if(my_ip_port != ip):
                thread = Thread(target=sendTokenRequest, args=(ip,))
                thread.start()
                # channel = grpc.insecure_channel(ip)
                # stub = CP_Server_pb2_grpc.ContentProvider_ServerStub(channel)
                # response = stub.receiveTokenRequest(CP_Server_pb2.requestTokenRequest(processID = PROCESS_ID, seqNumber = RN[PROCESS_ID]))
                # channel.close()
                # if(response.requestStatus == "Success"):
                #     continue
                # else:
                #     data = MessageToDict(
                #             response.token,
                #             preserving_proto_field_name=True,
                #             use_integers_for_enums=False,
                #             including_default_value_fields=True,
                #         )
                #     TOKEN["Q"] = data["Q"]
                #     TOKEN["LN"] = data["LN"]
                #     HAS_TOKEN = 1

    while HAS_TOKEN == 0:
        continue

    IS_IDLE = 0

    print("Sending File to Server...")
    time.sleep(20)
    channel = grpc.insecure_channel(SERVER_IP + ':' + SERVER_PORT)
    stub = CP_Server_pb2_grpc.ContentProvider_ServerStub(channel)
    response = stub.TransmitFile(CP_Server_pb2.TransmitFileRequest(fileName = fileName, fileContent = fileContent))
    channel.close()
    print(response.transmitStatus)

    print("Updating LN and Queue...")
    TOKEN["LN"][PROCESS_ID] = RN[PROCESS_ID]

    if(len(TOKEN["Q"]) > 0):
        if(TOKEN["Q"][0] == PROCESS_ID):
            queue = collections.deque(TOKEN["Q"])
            queue.popleft()
            TOKEN["Q"] = list(queue)

    for PID in range (0, len(RN) ):
        is_not_in_queue = (PID not in TOKEN["Q"])
        if(PID != PROCESS_ID & is_not_in_queue  & RN[PID] == (TOKEN["LN"][PID] + 1)):
            TOKEN["Q"].append(PID)


    if(len(TOKEN["Q"]) > 0):
        print("Current Queue : " + str(TOKEN["Q"]))
        print("Sending Token to Content Provider : " + str(TOKEN["Q"][0]))
        HAS_TOKEN = 0
        channel = grpc.insecure_channel( IP_LIST[TOKEN["Q"][0]] )
        stub = CP_Server_pb2_grpc.ContentProvider_ServerStub(channel)
        response = stub.receiveToken(CP_Server_pb2.sendTokenRequest(Q = TOKEN["Q"], LN = TOKEN["LN"]))
        channel.close()
        print(response.transmitStatus)

    IS_IDLE = 1

def serve(serverPort):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    CP_Server_pb2_grpc.add_ContentProvider_ServerServicer_to_server(ContentProviderService(), server)
    server.add_insecure_port('[::]:' + serverPort)
    server.start()

    try:
        while True:
            
            fileName = input('Enter File Name To Send To Server : ')
            fileContent = fileread.fileRead(fileName=fileName, folder = "ContentProvider")

            if(fileContent == "File Not Found"):
                print("File Not Found Enter a valid file name")
                continue
            else:
                transmitFile(fileName, fileContent)

    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    PROCESS_ID = int(input('Enter Content Provider Name : '))
    PORT = CONFIG_FILE.get(str(PROCESS_ID), "port")
    
    HAS_TOKEN = int(CONFIG_FILE.get(str(PROCESS_ID), "hasIdleToken"))
    serve(PORT)