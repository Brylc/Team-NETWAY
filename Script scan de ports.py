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
