def brutforce(client):
    envoyer("Quel est le mot de passe à trouver ?", client)
    mdp_a_trouver=reception(client, "")
    f = open("mdp.txt","r")

    for e,mdp in enumerate(f):
        if mdp[:-2]==mdp_a_trouver:
            envoyer("Le mot de pass a été trouvé : {} à la ligne {}".format(mdp[:-2], e),client)
            break

    f.close() 
