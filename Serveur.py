import socket
import threading
import mysql.connector
import time
import datetime
import hashlib
import ftplib

###########################################################################################################################################

#                                                              Les Threads

###########################################################################################################################################

class recevoir(threading.Thread):

    def __init__(self, Nom, client):
        self.job_started = True
        self.client_a_ecouter=client
        threading.Thread.__init__(self, name=Nom)
    
    def run(self):
        while self.job_started:

            msg_recu = self.client_a_ecouter.recv(1024)
            msg_recu = msg_recu.decode()
            print("{}: {}".format(dico_client_username[self.client_a_ecouter], msg_recu))


class emition(threading.Thread):

    def __init__(self, Nom):
        self.job_started=True
        threading.Thread.__init__(self, name=Nom)

    def run(self):
        while self.job_started:
            msgàClient=b"" 
            while msgàClient.upper()!=b"FIN":     
                msgàClient=input(">>> ")
                msgàClient=msgàClient.encode()
                clients_connectes[-1].send(msgàClient)

class serveur(threading.Thread):

    def __init__(self, nom):
        self.job_started=True
        threading.Thread.__init__(self, name=nom)
    
    def run(self):

        while self.job_started:
            connexion_avec_client, infos_connexion = connexion_principale.accept()
            print(infos_connexion) 
            dico_client_username[connexion_avec_client]="Client {}".format(str(len(clients_connectes))) 
            print("{} essaie de se connecter.".format(dico_client_username[connexion_avec_client]))
            Thread_authentification=authentification("authentification_{}".format(len(clients_connectes)),connexion_avec_client)
            dico_client_threadauthetification[connexion_avec_client]=Thread_authentification
            Thread_authentification.start()

        connexion_principale.close() 

###########################################################################################################################################

#                                                              Les Fonctions

###########################################################################################################################################


def envoyer(message, client):

    e=open("log.txt", "a+")    
    e.write(message)
    msgàclient=b""
    msgàclient=message
    msgàclient=msgàclient.encode()
    client.send(msgàclient)
    e.close()

def reception(client, temp):

    if temp == "username" or "motdepasse":
        msgclient=client.recv(1024)
        msgclient=msgclient.decode()
        return msgclient
    else:
        e=open("log.txt", "a+")
        msgclient=client.recv(1024)
        msgclient=msgclient.decode()
        e.write(dico_client_username[client],":", msgclient)
        e.close()
        return msgclient
        

def oui_non(phrase,client):
    envoyer("""{}
    1- Oui
    2- Non
""".format(phrase),client)
    return reception(client,"")


def suppression_user(connexion_bdd, client):
    reponse = oui_non("Voulez-vous afficher la liste des utilisateurs ? ",client)

    if reponse == "1":
        sql.execute("SELECT * FROM utilisateurs")
        affichage_requete = sql.fetchall()

        for index,ligne in enumerate(affichage_requete):
            print("{}- {}".format(index+1,ligne))

    envoyer("""Veuillez saisir le nom de l'utilisateur à supprimer.""",client)
    nom_user_a_supp = reception(client, "")
    nom_user_a_supp.upper()
    sql.execute("SELECT matricule,nom,prenom FROM utilisateurs WHERE nom='{}'".format(nom_user_a_supp))
    affichage_requete = sql.fetchall()
    liste=[]

    for index,ligne in enumerate(affichage_requete):
        envoyer("{}- {}".format(index+1,ligne),client)
        liste.append(ligne)

    envoyer("Quel utilisateur voulez-vous supprimer ?", client)
    user_a_supprimer= reception(client, "")
    sql.execute("DELETE FROM utilisateurs WHERE matricule = {}".format(liste[int(user_a_supprimer)-1][0]))
    print("Suppression terminée")
    connexion_bdd.commit()


def consul_user(connexion_bdd, client):
    envoyer("""Veuillez saisir le nom de l'utilisateur.
    >>>""",client)
    nom_user = reception(client, "")
    sql.execute("SELECT matricule,nom,prenom FROM utilisateurs WHERE nom='{}'".format(nom_user))
    affichage_requete = sql.fetchall()
    liste=[]

    for index,ligne in enumerate(affichage_requete):
        envoyer("{}- {}".format(index+1,ligne),client)
        liste.append(ligne)

    envoyer("Quel est donc l'utilisateur à consulter ?")
    user_a_consulter=reception(client,"")
    sql_commande = ("SELECT matricule,nom,prenom FROM utilisateurs WHERE matricule LIKE %s")
    sql.execute(sql_commande, ("%" + liste[user_a_consulter][0] + "%", ))
    resultat_sql = sql.fetchall()

    for line in resultat_sql:
        envoyer(line,client)

    connexion_bdd.commit()

def consul_info_utilisateur(connexion_bdd, client):
    recherch = dico_client_matricule[client]
    sql_commande = ("SELECT matricule,nom,prenom,lieu_de_travail,mail FROM utilisateurs WHERE matricule LIKE %s")
    sql.execute(sql_commande, ("%" + recherch + "%", ))
    resultat_sql = sql.fetchall()

    for line in resultat_sql:
        envoyer(line,client)

    connexion_bdd.commit()

def consul_all_users(connexion_bdd, client,localisation_admin):

    if localisation_admin=="Paris":
        sql.execute("SELECT matricule,nom,prenom,lieu_de_travail,mail FROM utilisateurs")

    else:
        sql.execute("SELECT matricule,nom,prenom,lieu_de_travail,mail FROM utilisateurs WHERE lieu_de_travail='{}'".format(localisation_admin))

    resultat_sql = sql.fetchall()

    for line in resultat_sql:
        envoyer(str(line), client)
        time.sleep(1)

    connexion_bdd.commit()


def creation_user(connexion_bdd, localisation_admin, client):
    envoyer("Vous êtes dans le menu de création d'un l'utilisateur.", client)
    envoyer("Veuillez Saisir le nom du nouvel l'utilisateur : ", client)
    nom = reception(client,"")
    nom.upper()
    envoyer("Veuillez saisir le prénom du nouvel l'utilisateur : ",client)
    prenom=reception(client,"")
    prenom[0].upper()
    envoyer("Le mot de passe par défaut a été attribué. L'utilisateur devra le changer lors de sa première connexion", client)
    motdepasse="Password"
    motdepasse_hash=hashlib.sha256(str(motdepasse).encode('utf-8'))
    username = prenom[0].lower()+nom.lower().replace(" ", "")

    if localisation_admin!="Paris":
        lieu_de_travail=localisation_admin
        choix2=True

        while choix2:
            envoyer("""
Quelle sera la fonction du nouvel utilisateur ? 

    1- Administrateur Classique
    2- Simple Utilisateur
""", client)
            choix_fonction=reception(client,"")
        
            if choix_fonction=="1":
                fonction = "Administrateur"
                choix2=False

            elif choix_fonction=="2":
                fonction="Utilisateur"
                choix2=False

            else:
                envoyer("Veuillez entrer une réponse valable")
    else:
        choix=True
        while choix:
            envoyer("""
Quelle sera la fonction du nouvel utilisateur ? 

    1- Administrateur Suprême
    2- Administrateur Classique
    3- Simple Utilisateur
""", client)
            choix_fonction=reception(client,"")
        
            if choix_fonction=="1":
                fonction = "Administrateur supreme"
                lieu_de_travail="Paris"
                choix=False

            elif choix_fonction=="2":
                fonction = "Administrateur"
                envoyer("Veuillez saisir le lieu de travail du nouvel utilisateur",client)
                lieu_de_travail = reception(client,"")
                choix=False

            elif choix_fonction=="3":
                fonction="Utilisateur"
                envoyer("Veuillez saisir le lieu de travail du nouvel utilisateur",client)
                lieu_de_travail = reception(client,"")
                choix=False

            else:
                envoyer("Veuillez entrer une réponse valable")

    sql.execute("INSERT INTO utilisateurs(nom,prenom,username,lieu_de_travail,fonction,mot_de_passe) VALUES('{}','{}','{}','{}','{}','{}')".format(nom,prenom,username,lieu_de_travail,fonction, motdepasse_hash.hexdigest()))
    print("l'insertion réussi")
    envoyer("l'insertion réussi",client)
    connexion_bdd.commit()


def modification_pwd_utilisateur(connexion_bdd, client):
    envoyer("Veuillez saisir votre nouveau mot de passe : ", client)
    pwd_a_modifier = reception(client, "")
    pwd_a_modifier = hashlib.sha256(str(pwd_a_modifier).encode('utf-8'))
    print(pwd_a_modifier.hexdigest())
    print("m",type(pwd_a_modifier.hexdigest()))
    print(dico_client_matricule[client])
    print(type(dico_client_matricule[client]))
    sql.execute("UPDATE utilisateurs SET mot_de_passe='{}' WHERE matricule={}".format(pwd_a_modifier.hexdigest(), dico_client_matricule[client]))
    print("Modification du mot de passe terminée")
    envoyer("Modification du mot de passe terminée", client)
    connexion_bdd.commit()


def modification_user(connexion_bdd, client, localisation_admin):
    affichage_requete=""
    while not(affichage_requete): 
        envoyer("""Veuillez saisir le nom de l'utilisateur.""",client)
        nom_user_a_supp = reception(client, "")
        sql.execute("SELECT matricule,nom,prenom,lieu_de_travail FROM utilisateurs WHERE nom='{}'".format(nom_user_a_supp))
        affichage_requete = sql.fetchall()

        if not(affichage_requete):
            envoyer("Aucun utilisateur n'a été trouvé.",client)
            

    liste=[]
    for index,ligne in enumerate(affichage_requete):

        if localisation_admin=="Paris":
            envoyer("{}- {}".format(index+1,ligne),client)
            liste.append(ligne)

        elif ligne[3]==localisation_admin:
            envoyer("{}- {}".format(index+1,ligne),client)
            liste.append(ligne)

    time.sleep(0.2)
    envoyer("Quel est donc l'utilisateur à modifier ?",client)
    user_a_modifier=reception(client,"")
    choix=True
    while choix:
        envoyer("""
Quelle modification voulez-vous apporter à l'utilisateur ?

    1- Modification du mot de passe;
    2- Modification du nom
    3- Modification du prénom
    4- Modification du lieu de travail
    5- Modification du mail 

    0- Annuler
    """, client)
        type_modification=reception(client,"")

        if type_modification=="1":
            type_modification="mot_de_passe"
            envoyer("Veuillez saisir le nouveau {} de l'utilisateur : ".format(type_modification), client)
            modification = reception(client,"")
            modification=hashlib.sha256(str(modification).encode('utf-8'))
            sql.execute("UPDATE utilisateurs SET mot_de_passe='{}' WHERE matricule ={}".format(modification.hexdigest(), liste[int(user_a_modifier)-1][0]))
            print("Modification du {} de {} par {} terminée".format(type_modification,liste[int(user_a_modifier)-1] ,dico_client_username[client]))
            envoyer("Modification du {} terminée".format(type_modification),client)
            connexion_bdd.commit()
            choix=False

        elif type_modification=="2":
            type_modification="nom"
            envoyer("Veuillez saisir le nouveau {} de l'utilisateur : ".format(type_modification), client)
            modification = reception(client,"")
            new_username=liste[int(user_a_modifier)-1][2][0].lower()+modification.lower().replace(" ", "")
            sql.execute("UPDATE utilisateurs SET nom='{}', username='{}'  WHERE matricule ={}".format(modification.upper(), new_username, liste[int(user_a_modifier)-1][0]))
            print("Modification du {} de {} par {} terminée".format(type_modification,liste[int(user_a_modifier)-1] ,dico_client_username[client]))
            envoyer("Modification du {} terminée".format(type_modification),client)
            connexion_bdd.commit()
            choix=False

        elif type_modification=="3":
            type_modification="prenom"
            envoyer("Veuillez saisir le nouveau {} de l'utilisateur : ".format(type_modification), client)
            modification = reception(client,"")
            new_username=modification[0].lower()+liste[int(user_a_modifier)-1][1].lower().replace(" ", "")
            sql.execute("UPDATE utilisateurs SET prenom='{}', username='{}'  WHERE matricule ={}".format(modification, new_username, liste[int(user_a_modifier)-1][0]))
            print("Modification du {} de {} par {} terminée".format(type_modification,liste[int(user_a_modifier)-1] ,dico_client_username[client]))
            envoyer("Modification du {} terminée".format(type_modification),client)
            connexion_bdd.commit()
            choix=False

        elif type_modification=="4":
            if localisation_admin=="Paris":
                type_modification="Lieu de travail"
                envoyer("Veuillez saisir le nouveau {} de l'utilisateur : ".format(type_modification), client)
                modification = reception(client,"")
                sql.execute("UPDATE utilisateurs SET lieu_de_travail='{}' WHERE matricule ={}".format(modification, liste[int(user_a_modifier)-1][0]))
                choix=False
                print("Modification du {} de {} par {} terminée".format(type_modification,liste[int(user_a_modifier)-1] ,dico_client_username[client]))
                envoyer("Modification du {} terminée".format(type_modification),client)
                connexion_bdd.commit()
            else:
                envoyer("Seuls les administrateurs de Paris ont le droit de faire cette modification")
                choix=False

        elif type_modification=="5":
            type_modification="Mail"
            envoyer("Veuillez saisir le nouveau {} de l'utilisateur : ".format(type_modification), client)
            modification = reception(client,"")
            sql.execute("UPDATE utilisateurs SET mail='{}' WHERE matricule ={}".format(modification, liste[int(user_a_modifier)-1][0]))
            print("Modification du {} de {} par {} terminée".format(type_modification,liste[int(user_a_modifier)-1] ,dico_client_username[client]))
            envoyer("Modification du {} terminée".format(type_modification),client)
            connexion_bdd.commit()
            choix=False
        
        elif type_modification=="0":
            choix=False    
        else:
            envoyer("Veuillez entrer une réponse valable")



    


def deconnexion(client):
    
    del dico_client_matricule[client]
    print("{} vient de se déconnecter.".format(dico_client_username[client]))
    del dico_client_username[client]
    envoyer("FIN",client)
    client.close()

###########################################################################################################################################

#                                                              Lancement du serveur

###########################################################################################################################################

hote = '127.0.0.1'
port = 12809

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(2)
print("Le serveur écoute à présent sur le port :", port)

serveur_lance = True

connexion_bdd = mysql.connector.connect(host="127.0.0.1", user="python", password="python", database="NETWAY")
sql = connexion_bdd.cursor()

log=open("log.txt", "a")

clients_connectes = []

dico_client_username={}
dico_client_matricule={}
dico_client_threadreception={}
dico_client_connexionftp={}
dico_client_threadauthetification={}

#Thread_reception_serveur=recevoir("TRS")
#Thread_reception_serveur.start()

#Thread_Emition=emition("TE")
#Thread_Emition.start()

Thread_serveur=serveur("TS")
Thread_serveur.start()

#Thread_log=log_ftp("TL", "log.txt", log)
#Thread_log.start()


 
