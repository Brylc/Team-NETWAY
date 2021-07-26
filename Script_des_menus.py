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


