class RegleFirewall:
    def __init__(self, action, ip_source, protocole, port_dest):
        self.action = action
        self.ip_source = ip_source
        self.protocole = protocole
        self.port_dest = port_dest


class GestionFirewall:
    def __init__(self, firewall):
        self.firewall = firewall

    def authentifier(self, login, mot_de_passe):
        if login == self.firewall.login and mot_de_passe == self.firewall.mot_de_passe:
            return True
        return False

    def ajouter_regle(self, login, mot_de_passe, action, ip_source, protocole, port_dest):
        if self.authentifier(login, mot_de_passe):
            regle = RegleFirewall(action, ip_source, protocole, port_dest)
            self.firewall.regles.append(regle)
            print("Règle ajoutée")
        else:
            print("Authentification échouée")

    def inspecter_paquet(self, paquet):
        for regle in self.firewall.regles:
            if regle.ip_source == paquet.source_ip and regle.protocole == paquet.protocole:
                self._journaliser(paquet, regle.action)
                return regle.action
        self._journaliser(paquet, "autoriser")
        return "autoriser"

    def _journaliser(self, paquet, decision):
        log = paquet.source_ip + " --> " + paquet.dest_ip + " : " + decision
        self.firewall.journal.append(log)

    def afficher_journal(self):
        print("\n=== Journal Firewall ===")
        for log in self.firewall.journal:
            print(log)


if __name__ == "__main__":

    from equipements import Firewall
    from paquets import Paquet


    print(" Creation du firewall ")
    fw = Firewall("FW1", "192.168.1.254", "Cisco", "actif", "admin", "1234")
    gestion = GestionFirewall(fw)
    print("Firewall:", fw.nom, "| IP:", fw.ip)

    print("\n Authentification ")
    print("admin / 1234 :", gestion.authentifier("admin", "1234"))
    print("admin / 0000 :", gestion.authentifier("admin", "0000"))

    print("\n Ajouter_regle ")
    gestion.ajouter_regle("admin", "1234", "bloquer", "192.168.1.1", "TCP", 80)
    gestion.ajouter_regle("admin", "1234", "bloquer", "192.168.1.2", "UDP", 443)
    gestion.ajouter_regle("admin", "0000", "autoriser", "192.168.1.3", "ICMP", 0)

    print("\n Inspection de paquet ")
    p1 = Paquet("192.168.1.1", "10.0.0.1", "TCP", 500, 2, "TRANSMIS")
    p2 = Paquet("192.168.1.2", "10.0.0.2", "UDP", 200, 1, "TRANSMIS")
    p3 = Paquet("192.168.1.5", "10.0.0.3", "ICMP", 100, 3, "TRANSMIS")

    print("p1 :", gestion.inspecter_paquet(p1))
    print("p2 :", gestion.inspecter_paquet(p2))
    print("p3 :", gestion.inspecter_paquet(p3))

    print("\n Affiche du journal ")
    gestion.afficher_journal()