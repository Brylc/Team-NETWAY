# Mise en place d'un serveur multi accès avec le module select
# Cette version est un test de réception de msg de plusieurs clients
# Version à améliorer pour l'envoi aux clients en parallèle

#importation des modules nécessaires
import socket
import select
import threading
import mysql.connector
import time
import hashlib

###########################################################################################################################################
###########################################################################################################################################

class recevoir(threading.Thread):

    def __init__(self, Nom):
        self.job_started = True
        threading.Thread.__init__(self, name=Nom)
    
    def run(self):
        while self.job_started:
            clients_a_lire = []  ### Avec gestion des exceptions 
            try:
                clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
            except select.error:
                pass

#on continue en séquence
            else:  
            # On parcourt la liste des clients à lire
                for client in clients_a_lire:
                # Client est de type socket
                    msg_recu = client.recv(1024)
                    msg_recu = msg_recu.decode()
                    print(dico_client_username)
                    print("Message reçu de {}: {}".format(dico_client_username[client], msg_recu))
                #client.send(b"5 / 5")

                #if msg_recu.upper() == "FIN":
                    #serveur_lance = False
    def reception(self, client):
        try:
            msgclient=client.recv(1024)
        except:
            pass
        else:
            #print(msgclient)
            
            msgclient=msgclient.decode()
            #print(msgclient)
            #print("Client :",msgclient)
            return msgclient


class emition(threading.Thread):

    def __init__(self, Nom):
        self.job_started=True
        threading.Thread.__init__(self, name=Nom)

    def run(self):
        while self.job_started:
            msgàClient=b"" 
            while msgàClient.upper()!=b"FIN":
     
             #print(">>> Envoi vers le serveur")      
                msgàClient=input(">>> ")
                msgàClient=msgàClient.encode()
                clients_connectes[-1].send(msgàClient)
    
def envoyer(message, client):
        
    msgàclient=b""
    msgàclient=message
    msgàclient=msgàclient.encode()
    client.send(msgàclient)

###########################################################################################################################################
###########################################################################################################################################

def Authentification(client):
 
    for tentatives in range(3):
        
        envoyer("Veuillez saisir votre nom d'utilisateur.", client)
        username=Thread_reception.reception(client)
        
        
        envoyer("Veuillez saisir votre mot de passe.", client)
        #mot_de_passe=hashlib.sha256(mot_de_passe)
        mot_de_passe=Thread_reception.reception(client)
        
        cursor.execute("SELECT matricule FROM UTILISATEURS WHERE username = '{}' AND mot_de_passe = '{}'".format(username,mot_de_passe)) #voir comment faire pour que le matricule soit attribué automatiquement a partir d'un schémas, primary key // le username = concaténation de la première lettre du prénom + nom
        res = cursor.fetchall()
        if not(res):
            print("{} : Tentative {} de connexion echouée.".format(dico_client_username[client],tentatives+1))
            envoyer("Tentative {} utilisée. Le nom d'utilisateur ou le mot de passe ne correspondent pas. Veuillez réessayer".format(tentatives+1), client)
        else:
            break
        if tentatives==2:
            print("{} n'a pas réussi à se connecter. Fermeture du lien".format(dico_client_username[client]))
            envoyer("Vous n'avez pas réussi a vous connecter.",client)
            client.close
    envoyer("Bravo, vous avez réussi à vous connecter", client)
    dico_username_client[username]=client
    dico_client_username[client]=username
    clients_connectes.append(client)
    print("{} vient de se connecter".format(dico_client_username[client]))
    
    #si oui :
    #   -vérifie le rôle
    #   -affiche le menu adéquoit

    #faire un dictionnaire avec cle=socket de la connexion // valeur = le nom d'utilisateur

###########################################################################################################################################
###########################################################################################################################################


 
# Les paramètres du serveur
hote = '127.0.0.1'
port = 12809
 

# Définition du socket de connexion
connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(2)  ## les deux clients

print("Le serveur écoute à présent sur le port :", port)
 
serveur_lance = True  #booléen

#Connexion à l abase de donnée
connexion_bdd = mysql.connector.connect(host="127.0.0.1", user="python", password="python", database="NETWAY")
cursor = connexion_bdd.cursor()


# liste de clients suceptibles de solliciter le serveur
clients_connectes = []

while serveur_lance:  ### while True ou bien while 1
    # On va vérifier les nouveaux clients qui se connectent
    # Pour cela, on écoute la connexion_principale en lecture
    # On attend maximum 60ms
    connexions_demandees, wlist, xlist = select.select([connexion_principale],
        [], [], 0.06)  # 0.06 secondes=60 ms de time out
    
    dico_client_username={}
    dico_username_client={}
     
    for connexion in connexions_demandees:  #les clients  de rlist
        
        connexion_avec_client, infos_connexion = connexion.accept()
        dico_client_username[connexion_avec_client]="Client"+str(len(dico_client_username))
        print("Un client essaie de se connecter")
        Authentification(connexion_avec_client)
        print(dico_client_username)
        
    
    Thread_reception=recevoir("TR")
    Thread_reception.start()
    Thread_Emition=emition("TE")
    Thread_Emition.start()
    
    

     
    # On écoute la liste des clients connectés
    # Les clients renvoyés par select sont ceux devant être lus (recv)
    # On attend là  60ms maximum
    # On encadre l'appel à select.select dans un bloc try
    # En effet, si la liste de clients connectés est vide, une exception
    # Peut être levée
              
print("Fermeture des connexions par l'un des clients ")

# Fermeture des connexions
for client in clients_connectes:
    client.close()
 
connexion_principale.close()