from equipements import Equipement
from paquets import Paquet

class MoniteurReseau:
    def __init__(self):
        self.equipements = []
        self.stats_paquets = {}
        self.historique = []

    def ajouter_equipement(self, equipement):
        self.equipements.append(equipement)

    def enregistrer_paquet(self, paquet):
        nom = paquet.source
        if nom not in self.stats_paquets:
            self.stats_paquets[nom] = {"envoyes": 0, "perdus": 0}

        if paquet.statut == "livré":
            self.stats_paquets[nom]["envoyes"] += 1
        else:
            self.stats_paquets[nom]["perdus"] += 1

        self.historique.append(paquet)
        if len(self.historique) > 10:
            self.historique.pop(0)

    def afficher_equipements(self):
        print("\n Equipements actifs/inactifs ")
        for eq in self.equipements:
            info = eq.diagnostiquer()
            print(info["nom"], "| IP:", info["ip"], "| Statut:", info["statut"])

    def afficher_stats(self):
        print("\n Statistiques paquets ")
        for ip, stat in self.stats_paquets.items():
            total = stat["envoyes"] + stat["perdus"]
            if total > 0:
                taux = (stat["perdus"] * 100) // total
            else:
                taux = 0
            print("IP:", ip, "| Envoyés:", stat["envoyes"], "| Perdus:", stat["perdus"], "| Taux perte:", taux, "%")

    def afficher_historique(self):
        print("\n 10 derniers paquets ")
        for paquet in self.historique:
            print(paquet.source, "-->", paquet.destination, "| Statut:", paquet.statut)

    def generer_rapport(self):
        fichier = open("rapport_simnet.txt", "w")
        fichier.write(" Rapport SimNet \n\n")

        fichier.write(" Equipements \n")
        for eq in self.equipements:
            info = eq.diagnostiquer()
            fichier.write("Nom: " + info["nom"] + " | IP: " + info["ip"] + " | Statut: " + info["statut"] + "\n")

        fichier.write("\n Statistiques paquets \n")
        for ip, stat in self.stats_paquets.items():
            fichier.write("IP: " + ip + "\n")
            fichier.write("Envoyes: " + str(stat["envoyes"]) + "\n")
            fichier.write("Perdus: " + str(stat["perdus"]) + "\n\n")

        fichier.write(" 10 derniers paquets \n")
        for paquet in self.historique:
            fichier.write(paquet.source + " --> " + paquet.destination + " : " + paquet.statut + "\n")

        fichier.close()
        print("Rapport généré : rapport_simnet.txt")




if __name__ == "__main__":
    
    
    from paquets import Paquet

    moniteur = MoniteurReseau()

    eq1 = Equipement("Routeur1", "Cisco", "192.168.1.1")
    eq2 = Equipement("Switch1", "HP", "192.168.1.2")
    eq3 = Equipement("Serveur1", "Dell", "192.168.1.3")

    eq1.activer()
    eq2.activer()

    moniteur.ajouter_equipement(eq1)
    moniteur.ajouter_equipement(eq2)
    moniteur.ajouter_equipement(eq3)

    p1 = Paquet("192.168.1.1", "10.0.0.1", "TCP", 500, 2, "TRANSMIS")
    p2 = Paquet("192.168.1.1", "10.0.0.2", "UDP", 200, 1, "PERDU")
    p3 = Paquet("192.168.1.2", "10.0.0.3", "ICMP", 100, 3, "TRANSMIS")
    p4 = Paquet("192.168.1.2", "10.0.0.4", "TCP", 300, 1, "PERDU")

    moniteur.enregistrer_paquet(p1)
    moniteur.enregistrer_paquet(p2)
    moniteur.enregistrer_paquet(p3)
    moniteur.enregistrer_paquet(p4)

    moniteur.afficher_equipements()
    moniteur.afficher_stats()
    moniteur.afficher_historique()
    moniteur.generer_rapport()
