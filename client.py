import socket
import os
import threading

HEADER = 64
FORMAT = "UTF-8"
DISCONNECT_MESAGE1 = "!DISCONNECT"
directory = "/Users/ioanmotrescu/Programare/Python/FTP_server"
#PORT = 5555
#SERVER = "127.0.0.1"
#SERVER = "192.168.1.3"
#SERVER = "86.123.70.24"

def verificare_cale(cale):
    cale = cale.split("/")
    cale.remove("")
    directory = "/"
    for dir in cale:
        if dir in os.listdir(directory):
            directory += "/" + dir
        else:
            return False
    return True

def download(name_fis):
    flag = recieve(client)
    if flag == "550": #A aparut o eroare
        print(recieve(client))
    elif flag == "150": #Deschiderea fisierului s-a terminat cu succes
        flag_fis = False
        while not flag_fis:  # introducere si verificare cale
            dir_download = input("Unde doriti sa incarcati fisierul?\n")
            flag_fis = verificare_cale(dir_download) # verificam daca calea este valida
            if not flag_fis:
                print("Calea este incorecta!")

        if name_fis in os.listdir(dir_download):  # Verificare daca fisierul deja exista
            xn = input("Fisierul deja exista. Doriti sa il rescrieti? [y/n]\n")
            if xn.lower() == "y":
                file_dw = open(dir_download + "/" + name_fis, "wb")
            else: #Cream copia fisierului adaugand la sfarsit _copy[i]
                i = 1
                while True:
                    try:
                        name = name_fis.split(".")
                        name[-2] = name[-2] + "_copy" + str(i)
                        name = ".".join(name)
                        file_dw = open(dir_download + "/" + name, "xb")
                    except FileExistsError:
                        i += 1
                        continue
                    break
        else: #Cazul in care fisierul nu exista
            file_dw = open(dir_download + "/" + name_fis, "wb")

        port = recieve(client) #Portul pentru conectiunea de date
        #print(f"Portul {port}")
        start_data_reciving(port, file_dw) #Incepem thread pentru conectiunea de date
        #print("Incepem Thread")

        comanda = recieve(client)
        if comanda == "226":  # verificam daca fisierul s-a terminat
            print("Fisierul a fost descarcat")
        elif comanda == '550':
            print(recieve(client))
            os.remove(dir_download + "/" + name_fis)
        else:
            print("comanda")


def send(client, msg):
    if not (type(msg) is bytes):
        msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg)

def send_file(port, cale, client):
    client_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_data.connect((SERVER, int(port)))
    file = open(cale, "rb")
    while True:
        text = file.read(1024)
        if text == b"": # Verificam daca am citit toate datele din fisier
            break
        send(client_data, text)
        #print("TEST1")
        while True:
            try:
                #print("TEST2")
                flag = recieve(client_data)
                #print("TEST3")
                if flag == "530":
                    #print("TEST4")
                    send(client_data, text)
                    continue
                elif flag == "230":
                    #print("TEST5")
                    break
            except:
                #print("Test6")
                break
    send(client_data, b"226")

def recieve(client):
        msg_length = client.recv(HEADER).decode(FORMAT)  # aflam si decodificam lungimea mesajului
        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            return msg
        else:
            return "None"


def recieve_file(client):
    while True:
        try:
            msg_length = client.recv(HEADER).decode(FORMAT)  # aflam si decodificam lungimea mesajului
            if msg_length:
                msg_length = int(msg_length)
                msg = client.recv(msg_length)
                send(client, "230")
                return msg
            else:
                return "None"
        except:
            send(client, "530")
            continue


def ls_recieve(client):
    files_len = int(client.recv(HEADER).decode(FORMAT))
    files = []
    for i in range(files_len):
        file = recieve(client)
        #print(file)
        files.append(file)
    return files

def logare(client, name):
    cod = recieve(client)
    match cod:
        case "331": #Numele este valid
            if name.lower() == "standart":
                print("Regim anonim")
            else:
                while True:
                    password = input("Introduceti parola\n").split()
                    if not password[0].upper() == "PASS" or not len(password) == 2: #Verificam daca parola este introdusa corect
                        print("Sintaxisul este invalid! Introduceti parola")
                        continue
                    break
                send(client, " ".join(password))
                cod = recieve(client)
                if cod == "530":
                    print(recieve(client)) #Afisam mesajul
                elif cod == "230":
                    print("Parola este corecta")
        case "530": #Eroare
            message = recieve(client)
            print(message)
            return


def start_data_reciving(port, file_dw):
    thread = threading.Thread(target=data_reciving, args=(port, file_dw))
    thread.start()

def start_data_sending(port, cale, client):
    thread = threading.Thread(target=send_file, args=(port, cale, client))
    thread.start()

def data_reciving(port, file_dw):
    client_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_data.connect((SERVER, int(port)))
    while True:
        data = recieve_file(client_data)  #Primim un kb de informatie
        if data == b"226":
            break
        file_dw.write(data)
    #print("TEST")
    file_dw.close()





#////////////////////////////////////////////////////////


while(True):

    while(True):
        try:
            SERVER = input("Introduci IP la care doriti sa va conectati: ")
            PORT = int(input("Introduceti portul la care doriti sa va conectait: "))
            ADDR = (SERVER, PORT)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)
            client.connect(ADDR)
            client.settimeout(20)
            print("Conexiunea la server a fost realizată cu succes!")
        except:
            print("A aparut o eroare la conectare!")
            continue
        break

    flag_c = True

    while True:
        conectat = True
        if flag_c == True: #Asteptam comanda de confirmarea conectiunii de la server
            if not recieve(client) == "220":
                continue
            flag_c = False
        msg_send = input("Introduceti mesajul:\n")
        msg_send = msg_send.split()

        try:
            match msg_send[0].upper():
                case 'LIST': #END
                    send(client, msg_send[0])
                    #print("TEST4")
                    directory = recieve(client)
                    #print("TEST5")
                    files = ls_recieve(client)
                    print(directory)
                    for file in files:
                        print(file)

                case "CWD": #END
                    if len(msg_send) == 1: #Verificam daca utilizatorul a introdus adresa
                        print("Nu ati specificat caleai")
                        continue
                    send(client, " ".join(msg_send))
                    flag = recieve(client)
                    #print(flag_dir)
                    if flag == "550":
                        print(recieve(client))
                    else:
                        directory = recieve(client)
                        print(directory)

                case "RETR":
                    send(client, " ".join(msg_send))
                    download(msg_send[1])

                case "STOR":
                    if not verificare_cale(msg_send[1]): # verificare
                        print("Calea este incorecta!")
                        continue
                    if os.path.isdir(msg_send[1]):
                        print("Calea duce catre o directorie!")
                        continue
                    nume = msg_send[1].split("/")[-1]
                    send(client, "LIST")
                    directory = recieve(client)
                    files = ls_recieve(client)

                    #print("TEST1")
                    if nume in files:
                        xn = input("Fisierul deja exista. Doriti sa il rescrieti? [y/n]\n").upper()
                        if xn != "Y":
                            continue

                    #print("TEST2")
                    send(client, " ".join(msg_send))
                    port = recieve(client)
                    start_data_sending(port, msg_send[1], client)


                    #print("TEST3")

                    client.settimeout(200)
                    flag = recieve(client)
                    client.settimeout(20)

                    #print("TEST4")

                    if flag == "226":
                        print("Fisierul a fost transmis")
                    elif flag == "550":
                        print(recieve(client))
                    else:
                        print(f"Eroare {flag}")

                case "USER": #END
                    send(client, " ".join(msg_send))
                    logare(client, msg_send[1])

                case "PASS": #END
                    send(client, " ".join(msg_send))
                    if recieve(client) == "530":
                        print(recieve(client))
                    else:
                        print("Parola este corecta")

                case "!DISCONNECT":
                    send(client, msg_send[0])
                    print("Deconectare!")
                    conectat = False

        except BrokenPipeError:
            print("Legatura cu server este pierduta")
            conectat = False
            break
        except Exception as eroare:
            print(f"Eroarea: {eroare}")
            if not conectat:
                break
            continue

        if not conectat:
            #print("TEST 2")
            break