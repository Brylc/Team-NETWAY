class log_ftp(threading.Thread):

    def __init__(self, nom, nom_fichier, lopen):
        self.fichier=str(nom_fichier)
        self.f_open=lopen
        threading.Thread.__init__(self, name=nom)

    def run(self):
        serveurftp.storbinary('STOR ' + self.fichier, self.f_open)
        time.sleep(2)

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


hote = '127.0.0.1'
serveurftp = ftplib.FTP(hote, "serveur", "serveurmotdepasse")
