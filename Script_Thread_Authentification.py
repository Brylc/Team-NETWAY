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
            
