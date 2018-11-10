
import socket
import threading
import random, string

# 서버의 설정값을 저장
myip = '127.0.0.1'
myport = 50000
address = (myip, myport)

# 서버를 연다.
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(address)
server_sock.listen()
print('Start Chat - Server')

# 접속한 클라이언트들을 저장할 공간
client_list = {}
client_id = []

#암호에 필요한 key생성
def make_key(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

#클라이언트로 부터 메시지를 받는 함수 | Thread 활용
def receive(client_sock):
    global client_list  # 받은 메시지를 다른 클라이언트들에게 전송하고자 변수를 가져온다.
    while True:
        # 클라이언트로부터 데이터를 받는다.
        try:
            data = client_sock.recv(1024)
        except ConnectionError:
            print("{}와 연결이 끊겼습니다. #code1".format(client_sock.fileno()))
            break
        
        # 만약 클라이언트로부터 종료 요청이 온다면, 종료함. code0 : 클라이언트 전송 기능 닫았을때 오는 메시지
        if not data:
            print("{}이 연결 종료 요청을 합니다. #code0".format(client_sock.fileno()))
            client_sock.send(bytes("서버에서 클라이언트 정보를 삭제하는 중입니다.", 'utf-8'))
            break

        #list명령어를 받으면
        if 'list'==data.decode('UTF-8').lower().strip():
            try:
                client_sock.send(bytes("현재 연결된 사용자: {}\n".format(client_id),'utf-8'))
                continue
            except ConnectionError:
                print("{}와 연결이 끊겼습니다. #code1".format(client_sock.fileno()))
                break


        #그룹 만들기
        if 'group'==data.decode('UTF-8').lower().strip():
            try:
                client_sock.send(bytes("현재 연결된 사용자: {}\n".format(client_id),'utf-8'))
                key=make_key()
                t=client_sock.recv(1024).decode('utf-8').lower().strip()
                while t!='finish':
                    try:
                        t=int(t)
                    except:
                        pass
                    client_sock.send(bytes("yourKey", 'utf-8'))
                    client_sock.send(bytes(str(key),'utf-8'))
                    if not(t in client_list):
                        client_sock.send(bytes("\n{} 유저는 현재 접속 중이 아닙니다".format(t), 'utf-8'))
                    else:
                        client_list[t].send(bytes("Key", 'utf-8'))
                        client_list[t].send(bytes(str(key),'utf-8'))
                    t=client_sock.recv(1024).decode('utf-8').lower().strip()
            except ConnectionError:
                print("{}와 연결이 끊겼습니다. #code1".format(client_sock.fileno()))
                break

        else:
            # 데이터가 들어왔다면 접속하고 있는 모든 클라이언트에게 메시지 전송
            data_with_id = bytes(str(client_sock.fileno()), 'utf-8') + b":"+data
            for sock in client_list.values():
                if sock != client_sock:
                    sock.send(data_with_id)
                
    # 메시지 송발신이 끝났으므로, 대상인 client는 목록에서 삭제.
    client_id.remove(client_sock.fileno())
    del client_list[client_sock.fileno()]
    print("현재 연결된 사용자: {}\n".format(client_id), end='')
    # 삭제 후 sock 닫기
    client_sock.close()
    print("클라이언트 소켓을 정상적으로 닫았습니다.")
    print('#----------------------------#')
    return 0


# 연결 수립용 함수 | Thread 활용
def connection():
    global client_list
    global client_id

    while True:
        # 클라이언트들이 접속하기를 기다렸다가, 연결을 수립함.
        client_sock, client_addr = server_sock.accept()
        
        # 연결된 정보를 가져와서 list에 저장함.
        client_id.append(client_sock.fileno())
        client_list[client_id[-1]]=client_sock

        print("{}가 접속하였습니다.".format(client_sock.fileno()))
        print("{}가 접속하였습니다.".format(client_addr))
        print("현재 연결된 사용자: {}\n".format(client_id))

        client_sock.send(bytes("Your ID is : {}\n".format(client_sock.fileno()),'utf-8'))

        # 접속한 클라이언트를 기준으로 메시지를 수신 할 수 있는 스레드를 생성함.
        thread_recv = threading.Thread(target=receive, args=(client_sock, ))
        thread_recv.start()


# 연결 수립용 스레드 생성 및 실행.
thread_server = threading.Thread(target=connection, args=())
thread_server.start()

print("============== Chat Server ==============")

thread_server.join()
server_sock.close()
