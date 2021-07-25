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

class authentification(threading.Thread):

    def __init__(self, nom, client):
        self.job_started=True
        self.client=client
        threading.Thread.__init__(self, name=nom)
    
    def run(self):
        for tentatives in range(3):
            envoyer("Veuillez saisir votre nom d'utilisateur.", self.client)
            username=reception(self.client, "username")
            envoyer("Veuillez saisir votre mot de passe.", self.client)
            mot_de_passe=reception(self.client, "motdepasse")
            mot_de_passe_hash=hashlib.sha256(str(mot_de_passe).encode('utf-8'))
            sql.execute("SELECT matricule,lieu_de_travail,fonction FROM UTILISATEURS WHERE username = '{}' AND mot_de_passe='{}'".format(username,mot_de_passe_hash.hexdigest()))
            resultat_sql = sql.fetchall()

            if not(resultat_sql):
                print("{} : Tentative {} de connexion echouée.".format(dico_client_username[self.client],tentatives+1))
                envoyer("Tentative {} utilisée. Le nom d'utilisateur ou le mot de passe ne correspondent pas. Veuillez réessayer".format(tentatives+1), self.client)

            else:
                break

            if tentatives==2:
                print("{} n'a pas réussi à se connecter. Fermeture du lien".format(dico_client_username[self.client]))
                envoyer("Vous n'avez pas réussi a vous connecter.",self.client)
                self.client.close
                self.job_started=False
                break
        
        envoyer("Bravo, vous avez réussi à vous connecter", self.client)
        dico_client_username[self.client]=username
        dico_client_matricule[self.client]=resultat_sql[0][0]
        clients_connectes.append(self.client)
        defaut_mdp=hashlib.sha256("Password".encode('utf-8'))

        if str(mot_de_passe_hash.hexdigest())==str(defaut_mdp.hexdigest()):
                envoyer("C'est votre première connexion, veuillez modifier votre mot de passe.",self.client)
                modification_pwd_utilisateur(connexion_bdd, self.client)

        print("{} vient de se connecter".format(dico_client_username[self.client]))
        host = "127.0.0.1"
        user = username
        ftp = ftplib.FTP(host, user, mot_de_passe_hash.hexdigest())
        dico_client_connexionftp[self.client]=ftp

        if resultat_sql[0][2]=="Utilisateur":
            menu_utilisateur(self.client,resultat_sql[0][1])

        elif resultat_sql[0][2]=="Administrateur":
            menu_administrateur(self.client,resultat_sql[0][1],resultat_sql[0][0])

        else:
            menu_administrateur_supreme(self.client,resultat_sql[0][1],resultat_sql[0][0])


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

class scan(threading.Thread):

    def __init__ (self, port_debut, port_fin, nom, hote):
        self.Port_Debut=int(port_debut)
        self.Port_fin=int(port_fin)
        self.Hote=hote
        self.Nombre_De_Ports=self.Port_fin-self.Port_Debut
        threading.Thread.__init__(self, name=nom)
    
    def run(self):
        for i in range(self.Nombre_De_Ports+1):
            if self.Port_Debut+i!=12809:
                try:
                    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    connexion_principale.connect((self.Hote, self.Port_Debut+i))
                    liste_des_ports_ouverts.append(self.Port_Debut+i)              

                except:
                    pass

        del liste_des_threads[-1]

class log_ftp(threading.Thread):

    def __init__(self, nom, nom_fichier, lopen):
        self.fichier=str(nom_fichier)
        self.f_open=lopen
        threading.Thread.__init__(self, name=nom)

    def run(self):
        serveurftp.storbinary('STOR ' + self.fichier, self.f_open)
        time.sleep(2)




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

def scan_de_ports(ftp, client):
    global liste_des_ports_ouverts, liste_des_threads
    hote ='127.0.0.1'
    date=datetime.datetime.now().time()
    date=date.strftime('%d_%y à %H_%M_%S')
    print("Horraire :", date)
    nom_du_fichier = "scan_du_{}.txt".format(date)

    f = open(nom_du_fichier,'a+')
    f.write ("la date :" +str(date) +"\n")
    f.write ("\n")
    f.write ('+-----------+------------+\n')
    f.write ('|port       [  etat      |\n')
    f.write ('+-----------+------------+\n')

    liste_des_ports_ouverts = []
    liste_des_threads= []

    for i in range(2048):
        port_debut=1+(32*i)
        port_fin=(i+1)*32
        scann=scan(port_debut, port_fin, "scan_{}_{}".format(port_debut, port_fin),hote)
        liste_des_threads.append(scann)
        scann.start()

    while not(not(liste_des_threads)):
        envoyer("Scan de ports en cours.", client)
        time.sleep(12)
        pass

    envoyer("Scan de ports terminé", client)
    envoyer("{} ports ont été trouvés ouverts".format(len(liste_des_ports_ouverts)), client)
    liste_des_ports_ouverts.sort()
    print(liste_des_ports_ouverts)

    for valeur in liste_des_ports_ouverts:
        f.write("le port TCP "+str (valeur)+ " : Ouvert \n")

    print("Le scan des ports est finit.")
    serveurftp.storbinary('STOR ' + nom_du_fichier, f)
    f.close()

def brutforce(client):
    envoyer("Quel est le mot de passe à trouver ?", client)
    mdp_a_trouver=reception(client, "")
    f = open("mdp.txt","r")

    for e,mdp in enumerate(f):
        if mdp[:-2]==mdp_a_trouver:
            envoyer("Le mot de pass a été trouvé : {} à la ligne {}".format(mdp[:-2], e),client)
            break

    f.close()   

    

###########################################################################################################################################

#                                                              Les Menus

###########################################################################################################################################

def menu_utilisateur(client, localisation):
    dico_client_threadauthetification[client].job_started=False
    choix=True
    while choix:
        envoyer("""
Bonjour {}, Bienvenu dans le menu utilisateur de {}.

    1 - Modification de son MDP
    2 - Consulter ses informations

    0 - Quitter (deconnexion)

Quel actions voulez-vous effectuer ?""".format(dico_client_username[client], localisation),client)

        choix=reception(client, "")
        if choix == "1":
            modification_pwd_utilisateur(connexion_bdd, client)

        elif choix == "2":
            consul_info_utilisateur(connexion_bdd, client)

        elif choix == "0":
            deconnexion(client)
            choix=False

        else:
            envoyer("Veuillez entrer une réponse valable")

def menu_administrateur(client, localisation_admin, matricule):
    dico_client_threadauthetification[client].job_started=False
    menu_admn=True
    while menu_admn:
        envoyer("""
Bonjour {}, bienvenu dans le menu de gestion de l'administrateur pour le site de {} :

    1 - Gestion des utilisateurs
    2 - Gestion du serveur FTP

    0 - Quitter (déconnexion)
    
Quel actions voulez-vous effectuer ?""".format(dico_client_username[client],localisation_admin),client)
        choix_adm = reception(client,"")

        if choix_adm == "1":
            choix=True
            while choix:
                envoyer("""
Bienvenu dans le menu de gestion des utilisateurs, quel actions voulez vous effectuer 

    1 - Création d'untilisateur
    2 - Suppression d'un utilisateur
    3 - Consultation de tous les utilisateurs
    4 - Modification d'un utilisateur

    0 - Quitter

Quelle action voulez-vous faire ?""",client)
                choix_gstu=reception(client, "")
            
                if choix_gstu == "1":
                    creation_user(connexion_bdd, localisation_admin,client)

                elif choix_gstu == "2":
                    suppression_user(connexion_bdd, client)

                elif choix_gstu == "3":
                    consul_all_users(connexion_bdd, client, localisation_admin)

                elif choix_gstu == "4":
                    modification_user(connexion_bdd, client, localisation_admin)

                elif choix_gstu == "0":
                    choix=False
                else:
                    envoyer("Veuillez entrer une réponse valable")

        elif choix_adm=="2":
            menu_ftp(client, dico_client_connexionftp[client])
            
        elif choix_adm=="0":
            deconnexion(client)
            menu_admn=False
        
        else:
            envoyer("Veuillez entrer une réponse valable")

def menu_administrateur_supreme(client,localisation_admin, matricule):
    dico_client_threadauthetification[client].job_started=False
    menu_admns=True
    while menu_admns:
        choix_menu_admns=""
        envoyer("""

Bonjour {} bienvenu dans le menu de gestion de l'administrateur suprême:

1 - Gestion des utilisateurs
2 - Scans de ports
3 - Gestion du serveur FTP
4 - Afficher les logs
5 - Test Brutforce

0 - Quitter (déconnexion)

Quelle actions voulez-vous effectuer ?""".format(dico_client_username[client]), client)
        choix_menu_admns=reception(client, "")

        if choix_menu_admns == "1":
            menu_gstu=True
            while menu_gstu:
                choix_menu_gstu=""
                envoyer("""

Vous êtes maintenant dans le menu de gestion des utilisateurs, quelle actions voulez vous effectuer ?

1 - Création d'un utilisateur
2 - Modification d'un utilisateur
3 - Consultation de tous les utilisateurs
4 - Consultation d'un utilisateur précis
5 - Suppression d'un utilisateur

0 - Quitter

Que voulez-vous faire ?""", client)
                choix_menu_gstu = reception(client, "")
                
                if choix_menu_gstu == "1":
                    creation_user(connexion_bdd,localisation_admin,client)

                elif choix_menu_gstu == "2":
                    modification_user(connexion_bdd,client, localisation_admin)

                elif choix_menu_gstu == "3":
                    consul_all_users(connexion_bdd,client,localisation_admin)

                elif choix_menu_gstu == "4":
                    consul_user(connexion_bdd,client)

                elif choix_menu_gstu == "5":
                    suppression_user(connexion_bdd,client)

                elif choix_menu_gstu == "0":
                    menu_gstu=False

        elif choix_menu_admns=="2":
            scan_de_ports(dico_client_connexionftp[client], client)

        elif choix_menu_admns=="3":
            menu_ftp(client, dico_client_connexionftp[client])
        
        elif choix_menu_admns=="4":
            f=open("log.txt", "r")
            for ligne in f:
                envoyer(ligne, client)

        elif choix_menu_admns=="5":
            brutforce(client)

        elif choix_menu_admns=="0":
            deconnexion(client)
            menu_admns=False

        else:
            envoyer("Veuillez entrer une réponse valable")

def menu_ftp(client, connexion_ftp):
    envoyer("Vous êtes actuellement dans ce dossier {}".format(str(connexion_ftp.pwd())),client)
    menu_ftp = True
    while menu_ftp:
        envoyer("""
Que voulez-vous faire ? 

1- Afficher le dossier courant
2- Affichier le contenu du dossier courant 
3- Créer un sous-dossier
4- Entrer dans un sous dossier
5- Supprimer un fichier
6- Supprimer un sous-dossier
7- Renommer un fichier ou un dossier
8- Charger un fichier sur le serveur
9- Télecharger un fichier

0- Quitter""", client)
        choix_menu_ftp=reception(client,"")

        if choix_menu_ftp=="1":
            envoyer(connexion_ftp.pwd(), client)

        elif choix_menu_ftp=="2":
            print("Montrer dans l'autre fichier")

        elif choix_menu_ftp=="3":
            envoyer("Quel est le nom du sous-dossier ?",client)
            nom_du_fichier=reception(client,"")
            connexion_ftp.mkd(nom_du_fichier)
            envoyer("Le nouveau dossier à été créé", client)

        elif choix_menu_ftp=="4":
            envoyer("Dans quel sous dossier souhaitez vous rentrer ?", client)
            sous_dossier_cible=reception(client,"")
            connexion_ftp.cwd(sous_dossier_cible)

        elif choix_menu_ftp=="5":
            envoyer("Quel est le nom du fichier ? ",client)
            nom_du_fichier_a_supp=reception(client, "")
            connexion_ftp.delete(nom_du_fichier_a_supp)

        elif choix_menu_ftp=="6":
            envoyer("Quel est le nom du dossier à supprimer ? ",client)
            nom_du_dossier_a_supp=reception(client, "")
            connexion_ftp.rmd(nom_du_dossier_a_supp)

        elif choix_menu_ftp=="7":
            envoyer("Quel est le nom du dossier ou fichier à renommer ?", client)
            entite_a_renommer=reception(client,"")
            envoyer("Sous quel nom doit-il être renommé", client)
            nouveau_nom=reception(client,"")
            connexion_ftp.rename(entite_a_renommer, nouveau_nom)
        
        elif choix_menu_ftp=="8":
            envoyer("Quel est le nom du fichier ? ")
            f_name=reception(client, "")
            f = open(f_name, 'rb')
            connexion_ftp.storbinary('STOR ' + f_name, f)
            f.close()
        
        elif choix_menu_ftp=="9":
            envoyer("Quel fichier veux-tu télecharger ?", client)
            fichiers = connexion_ftp.nlst()
            for e,f in enumerate(fichiers):
                envoyer("{}- {}".format(e,f), client)
            choix_fichier=reception(client, "")
            fichier_a_telecharger = open(fichiers[int(choix_fichier)], "wb")
            connexion_ftp.retrbinary("RETR" + fichiers[int(choix_fichier)], fichier_a_telecharger.write)
            fichier_a_telecharger.close()

        elif choix_menu_ftp=="0":
            menu_ftp=False
        
        else:
            envoyer("Veuillez entrer une réponse valable")



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

serveurftp = ftplib.FTP(hote, "serveur", "serveurmotdepasse")
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


 
