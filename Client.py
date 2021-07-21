###############################################
# Mise en place d'un client simple
# simulation d'une connexion client/serveur
#"""""""""""""""""  version basique """""""""""#

import socket,sys
import threading
import time
  
# création d'un socket pour la connexion avec le serveur en local
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try: ### surveiller ce bout de code 
# connexion au serveur, bloc surveillé, et gestion de l'exception
    sock.connect(('127.0.0.1',12809))

except socket.error:
   print("la connexion a échoué.......")
   sys.exit()

print(">>> Connexion établie avec le serveur...")
# Envoi et réception de messages
#sock.send(b"hello serveur, je suis le client1 ")

class reception(threading.Thread):
    def __init__(self, Nom):
        self.job_started=True
        threading.Thread.__init__(self, name=Nom)

    def run(self):
        while self.job_started:
            msgServer=sock.recv(1024) # taille par défaut
            print(msgServer.decode())
            if msgServer=="FIN":
                print ("Fermeture de ma connexion")
                deconnexion()
                

class emition(threading.Thread):
    def __init__(self, Nom):
        self.job_started=True
        threading.Thread.__init__(self, name=Nom)
    
    def run(self):
        while self.job_started:
            msgClient=b"" 
            while msgClient.upper()!=b"FIN":
                #print(">>> Envoi vers le serveur") 
                time.sleep(0.3)     
                msgClient=input(">>> ")
                msgClient=msgClient.encode()
                sock.send(msgClient)
        
        
        

def deconnexion():
    Thread_Emition.job_started=False
    Thread_reception.job_started=False
    sock.close()
    print("Communication terminée")



Thread_Emition=emition("TE")
Thread_reception=reception("TR")
Thread_reception.start()
Thread_Emition.start()






         

