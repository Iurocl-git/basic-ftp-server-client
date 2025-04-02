import socket
import threading
import os





s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
server_ip = s.getsockname()[0]
s.close()

port = 5550
#server_ip = "127.0.0.1"


ADDR = (server_ip, port)
HEADER = 64
FORMAT = "UTF-8"
DISCONNECT_MESAGE = "!DISCONECT"

STANDART = os.getcwd();
DIRECTORY = STANDART + "/client"
PUBLIC_DIRECTORY = "Public"
CLIENT_DIRECTORY = "client"


def send_file(conn, cale):
    try:
        file = open(cale, "rb")
    except IsADirectoryError:
        send(conn, "550")
        send(conn, "Elementul este o directorie")
        return
    except:
        send(conn, "550")
        send(conn, "Au aparut probleme la deschiderea fisierului")
        return

    send(conn, "150")
    #print("-Thread")
    start_data(conn, file) #incepem un thread pentru a transmite datele
    #print("+Thread")



def dir_calatorie(directory, mesaj, username, flag = True):
    if mesaj == ".." or mesaj == "...":
        directory = directory.split("/")
        directory.pop()
        directory = "/".join(directory)

        if DIRECTORY in directory: #Calea noua este accesibila
            return True, directory
        else: #Calea nou este inacc1esibila
            return False, DIRECTORY

    else:
        if flag: #Calea completa
            mesaj = mesaj.split("/")
            mesaj.remove('')
            directory = STANDART
        else: #Calea se afla in directoriu curent
            mesaj = mesaj.split("/")
            if len(mesaj) > 1:
                mesaj.remove('')

        if not directory == DIRECTORY:
            if not "/client/Public" in directory and not "/client/"+username in directory and not mesaj == [CLIENT_DIRECTORY]: #Verificam daca deja ne aflam in directoriu utilizatorului sau daca trecem la directoriu de baza
                if not mesaj[1] == username and not mesaj[1] == PUBLIC_DIRECTORY: #Verificam daca utilizatorul are acces la directoriu
                    return False, directory
        else:
            if not "/client/Public" in directory and not "/client/" + username in directory:  # Verificam daca deja ne aflam in directoriu utilizatorului sau daca trecem la directoriu de baza
                if not mesaj[0] == username and not mesaj[0] == PUBLIC_DIRECTORY:  # Verificam daca utilizatorul are acces la directoriu
                    return False, directory

        dir_copy = directory
        for element in mesaj: #Parcurgem fiecare element din cale
            if element in os.listdir(dir_copy) and os.path.isdir(dir_copy+"/"+element): #Verificam daca calea se afla in directoriu curent si nu este fisier
                dir_copy += "/" + element
            else:
                return False, directory
        return True, dir_copy

def ls_send(conn, directory):
    files = os.listdir(directory)
    try:
        files.remove(".DS_Store")
    except:
        files = files
    #files = [s.encode(FORMAT) for s in files]
    files_len = str(len(files)).encode(FORMAT)
    files_len += b" " * (HEADER - len(files_len))
    conn.send(files_len)
    for file in files:
        send(conn, file)

def send(conn, msg):
    if not (type(msg) is bytes):
        msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(msg)

def recv(conn):
    lenght = conn.recv(HEADER).decode(FORMAT)
    if lenght:
        lenght = int(lenght)
        msg = conn.recv(lenght).decode(FORMAT)
        return msg
    else:
        return "None"

def recieve_file(conn_data, conn):
    while True:
        try:
            msg_length = conn_data.recv(HEADER).decode(FORMAT)  # aflam si decodificam lungimea mesajului
            if msg_length:
                msg_length = int(msg_length)
                msg = conn_data.recv(msg_length)
                send(conn_data, "230")
                #print(f"Test1 {msg_length} {msg}")
                return msg
            else:
                #print("Test2")
                return "None"
        except:
            #print("Test3")
            send(conn_data, "530")
            continue


def logare(conn, username):
    flag = False
    if username.lower() == "standart":
        send(conn, "331")
        return "standart", "standart"
    else:
        while True:
            fisier_utilizatori = open(STANDART + "/utilizatori.txt", "r")
            for linie in fisier_utilizatori:
                linie = linie[:-1].split(":")
                if linie[0] == username: #utilizatorul exista
                    flag = True
                    send(conn, "331") #trimitam ca numele utilizatorului este valid
                    password = recv(conn).split()[1]
                    if linie[1] == password:
                        send(conn, "230") #trimitem ca parola este valida
                        return username, password
                    else:
                        send(conn, "530") #trimitem ca parola este invalida
                        send(conn, "Parola este incorecta")
                        return "standart", "standart"
            if flag == False:
                send(conn, "530")
                send(conn, "Numele utilizatorului nu a fost gasit")
                return "standart", "standart"


def cwd_implementation(conn, directory, new_dir, username):
    #####
    if new_dir == ".." or new_dir == "...":  #Cazul undo
        if directory == DIRECTORY:
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory

        flag, directory = dir_calatorie(directory, new_dir, username)
        if flag:  #Posibil undo
            send(conn, "250")
            send(conn, directory.replace(STANDART, ""))
            return directory
        else:  #Imposibil undo
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory
    #####

    ##### Primul element se afla in directoriu curent
    fisier = new_dir.split("/")
    if len(fisier) == 1:
        fisier = fisier[0]
    else:
        try:
            fisier = (new_dir.split("/"))[1]  #Salvam primul element din cale
        except:
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory

    if fisier in os.listdir(directory):  #Verificare daca primul fisier din cale este in directoriu curent
        flag, directory = dir_calatorie(directory, new_dir, username, False)  #Verificam calea
        if flag:  #Calea este valida
            send(conn, "250")
            send(conn, directory.replace(STANDART, ""))
            return directory
        else:  #Calea este invalida
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory
    #####

    ##### Calea completa
    try:
        if not new_dir.split("/")[1] == CLIENT_DIRECTORY:  #Verificare daca directoriu este accesibil pentru client
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory
    except:
        send(conn, "550")
        send(conn, "Directoriu este inaccesibil")
        return directory
    else:  #Directoriu este accesibil
        flag, directory = dir_calatorie(directory, new_dir, username)  #Verificam validitatea calei
        if flag:  #Calea este valida
            send(conn, "250")
            send(conn, directory.replace(STANDART, ""))
            return directory
        else:  #Calea este invalida
            send(conn, "550")
            send(conn, "Directoriu este inaccesibil")
            return directory
    #####

def data_transfer(conn_data, conn, file):

    try:
        while True:
            text = file.read(1024)
            if text == b"":  #Verificam daca am citit toate datele din fisier
                break
            send(conn_data, text)
            while True:
                try:
                    flag = recv(conn_data)
                    if flag == "530":
                        send(conn_data, text)
                    elif flag == "230":
                        break
                except:
                    break
    except:
        send(conn_data, b"226") #Transmitem end_of_file
        send(conn, "550")
        send(conn, "Au aparut probleme la transmiterea fisierului")
        return
    send(conn_data, b"226") #Transmitem end_of_file
    send(conn, "226")
    print("Close Data conexion")

def data_recieve(conn_data, conn, file):
    try:
        while True:
            text = recieve_file(conn_data, conn)  # primim un kb de informatie
            if text == b"226":  # verificam daca fisierul s-a terminat
                break
            file.write(text)
            #print("TEST")
        #print("TEST1")
        file.close()
        #print("TEST2")
    except:
        file.close()
        send(conn, "550")
        send(conn, "A aparut o eroare la transferul fisierului")
        return
    send(conn, "226")
    print("Close Data conexion")



####################################################################
def handle_client(conn, addr):
    print(f"[NEW CONECTION] {addr} connected")
    connected = True
    directory = DIRECTORY
    username = "standart"
    password = "standart"
    send(conn, "220")


    while connected:
        conn.settimeout(180)
        try:
            msg = recv(conn)
        except socket.timeout:
            break
        except:
            continue
        print(f"{addr} {msg}")
        msg = msg.split()

        match msg[0].upper():

            case "LIST":
                send(conn, directory.replace(STANDART, ""))
                ls_send(conn, directory)

            case "CWD":
                new_dir = msg[1]    #citim directoriu nou
                directory = cwd_implementation(conn, directory, new_dir,username)

            case "RETR":
                if not msg[1] in os.listdir(directory):  # verificam daca fisierul exista in directoriu
                    send(conn, "550")
                    send(conn, "Numele fisierului este incorect")
                    continue
                send_file(conn, directory + "/" + msg[1])

            case "STOR":
                name_fis = msg[1]  #citim denumirea cu /
                name_fis = name_fis.split("/")[-1]  #salvam denumirea fisierului

                try:
                    file = open(directory + "/" + name_fis, "wb")
                    start_data(conn, file, False)
                except:
                    send(conn, "550")
                    send(conn, "A aparut la crearea fisierului")
                    continue

            case "USER": #END
                username, password = logare(conn, msg[1])

            case "PASS": #END
                send(conn, "530")
                send(conn, "Intai introduceti numele!")

            case "!DISCONNECT":
                connected = False

            case "NONE":
                connected = False
    print(f"[ACTIVE CONECTIONS] {threading.active_count() - 2}")
    conn.close()

def start():
    server.listen() #Incepem sa ascultam portul
    print(f"[LISTENING] Server is listening on {server_ip} {port}")
    while True:
        conn, addr = server.accept() #Asteptam conectare
        thread = threading.Thread(target = handle_client, args = (conn, addr)) #Cream procesul in paralel
        thread.start() #Incepem procesul in paralel
        print(f"[ACTIVE CONECTIONS] {threading.active_count() - 1}")

def start_data(conn, file, flag = True):
    server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for port in range(1024, 6001):
        try:
            addr = (server_ip, port)
            server_data.bind(addr)
        except OSError:
            print(f"Erorea portul: {port}")
            continue
        break
    server_data.listen()
    print(f"Portul {port}")
    send(conn, str(port))
    try:
        server_data.settimeout(30)
        conn_data, addr_data = server_data.accept()
    except:
        return

    if flag == True:
        thread = threading.Thread(target=data_transfer, args=(conn_data, conn, file))
        thread.start()
    else:
        thread = threading.Thread(target=data_recieve, args=(conn_data, conn, file))
        thread.start()






server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
print("[STARTING] server is starting...")
start()

#Stor alternativ
# if name_fis in os.listdir(directory): # verificam daca fisierul deja exista in directoriu
                #     send(conn, "Exista")
                #     if recv(conn) == "y":   #rescriem fisierul
                #         fisier = open(directory + "/" + name_fis, "wb")
                #     else:   #se creaza copia fisierului
                #         i = 1
                #         while True: # cream o copie a fisierului
                #             try:
                #                 name = name_fis.split(".")
                #                 name[-2] = name[-2] + "_copy" + str(i)
                #                 name = ".".join(name)
                #                 fisier = open(directory + "/" + name, "xb")
                #             except FileExistsError:
                #                 i += 1
                #                 continue
                # else:   #fisierul nu exista in directoriu curent
                #     send(conn, "NuExista")
                #     fisier = open(directory + "/" + name_fis, "xb")
