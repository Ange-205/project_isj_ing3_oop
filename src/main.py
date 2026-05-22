from equipements import Equipement, Routeur, Switch, Serveur, Firewall, PointAccesWifi, Terminal
from topologie   import topology, Link
from paquets     import Paquet, Simulateur
from securite    import RegleFirewall, GestionFirewall
from moniteur    import MoniteurReseau


def initialiser_reseau():
    topo     = topology()
    moniteur = MoniteurReseau()

    r1  = Routeur(  "R_Core",    "Cisco",   "10.0.0.1",  4)
    r2  = Routeur(  "R_Edge",    "Juniper", "10.0.0.2",  2)
    sw1 = Switch(   "SW_Distrib","HP",      "10.0.1.1", 24)
    sv1 = Serveur(  "SRV_Web",   "Dell",    "10.0.2.1",  16, 4)

    for eq in [r1, r2, sw1, sv1]:
        topo.add_equipement(eq)
        moniteur.ajouter_equipement(eq)
        eq.activer()

    topo.add_link(r1,  r2,  1000, 1.5)
    topo.add_link(r1,  sw1, 1000, 0.5)
    topo.add_link(sw1, sv1,  100, 0.3)

    sim = Simulateur(topo)
    return topo, sim, moniteur

# bloquer les doublons de liens
def lien_existe(topo, eq1, eq2):
    """Retourne True si un lien entre eq1 et eq2 existe deja."""
    for lien in topo.links:
        if ((lien.equipement1 == eq1 and lien.equipement2 == eq2) or
                (lien.equipement1 == eq2 and lien.equipement2 == eq1)):
            return True
    return False


def menu_ajouter_equipement(topo, moniteur):
    """Ajoute un equipement a la topologie."""
    print("\n--- Ajouter un equipement ---")
    print("Types : 1=Routeur  2=Switch  3=Serveur  4=Firewall  5=WiFi  6=Terminal")
    choix  = input("Type       : ").strip()
    nom    = input("Nom        : ").strip()
    marque = input("Marque     : ").strip()
    ip     = input("Adresse IP : ").strip()

    try:
        if choix == "1":
            nb = int(input("Nb interfaces : "))
            eq = Routeur(nom, marque, ip, nb)
        elif choix == "2":
            nb = int(input("Nb ports : "))
            eq = Switch(nom, marque, ip, nb)
        elif choix == "3":
            ram = int(input("RAM (Go)     : "))
            cpu = int(input("CPU (coeurs) : "))
            eq  = Serveur(nom, marque, ip, ram, cpu)
        elif choix == "4":
            login = input("Login admin  : ").strip()
            mdp   = input("Mot de passe : ").strip()
            eq    = Firewall(nom, marque, ip, login, mdp)
        elif choix == "5":
            ssid  = input("SSID  : ").strip()
            canal = int(input("Canal : "))
            eq    = PointAccesWifi(nom, marque, ip, ssid, canal)
        elif choix == "6":
            type_t = input("Type terminal (PC/Laptop/...) : ").strip()
            mac    = input("Adresse MAC                   : ").strip()
            eq     = Terminal(nom, marque, ip, type_t, mac)
        else:
            print("[ERREUR] Type invalide.")
            return

        topo.add_equipement(eq)
        moniteur.ajouter_equipement(eq)
        eq.activer()
        print(f"[OK] {nom} ajoute et active.")
    except ValueError as e:
        print(f"[ERREUR] {e}")


def menu_supprimer_equipement(topo, moniteur):
    """Supprime un equipement de la topologie."""
    print("\n--- Supprimer un equipement ---")
    if not topo.equipements:
        print("  Aucun equipement dans la topologie.")
        return
    for eq in topo.equipements:
        print(f"  - {eq.nom} ({eq.adresse_ip})")
    nom   = input("Nom a supprimer : ").strip()
    cible = None
    for eq in topo.equipements:
        if eq.nom == nom:
            cible = eq
            break
    if cible:
        topo.delete_equipement(cible)
        if cible in moniteur.equipements:
            moniteur.equipements.remove(cible)
        print(f"[OK] {nom} supprime.")
    else:
        print(f"[ERREUR] '{nom}' introuvable.")


def menu_ajouter_lien(topo):
    """Ajoute un lien entre deux equipements."""
    print("\n--- Ajouter un lien ---")
    if len(topo.equipements) < 2:
        print("  Il faut au moins 2 equipements.")
        return

    # Afficher les equipements disponibles avec IP
    print("  Equipements disponibles :")
    for eq in topo.equipements:
        print(f"    - {eq.nom} ({eq.adresse_ip})")

    nom1 = input("  Equipement 1 : ").strip()
    nom2 = input("  Equipement 2 : ").strip()
    eq1  = eq2 = None
    for eq in topo.equipements:
        if eq.nom == nom1: eq1 = eq
        if eq.nom == nom2: eq2 = eq
    if not eq1 or not eq2:
        print("[ERREUR] Un ou deux equipements introuvables.")
        return

    # bloquer les doublons
    if lien_existe(topo, eq1, eq2):
        print(f"[ERREUR] Un lien entre {nom1} et {nom2} existe deja.")
        return

    try:
        bp  = float(input("  Bande passante (Mbps) : "))
        lat = float(input("  Latence (ms)          : "))
        topo.add_link(eq1, eq2, bp, lat)
        print(f"[OK] Lien {nom1} <-> {nom2} ajoute.")
    except ValueError:
        print("[ERREUR] Valeur invalide.")


def menu_afficher_topologie(topo):
    """Affiche tous les equipements et liens du reseau."""
    print("\n" + "="*50)
    print("  TOPOLOGIE DU RESEAU")
    print("="*50)
    print(f"\n  Equipements ({len(topo.equipements)}) :")
    for eq in topo.equipements:
        statut = "ACTIF" if eq.est_actif else "INACTIF"
        print(f"    [{statut}] {eq.nom} ({eq.marque}) -- {eq.adresse_ip}")
    print(f"\n  Liens ({len(topo.links)}) :")
    if not topo.links:
        print("    (aucun lien)")
    else:
        for lien in topo.links:
            print(f"    {lien.equipement1.nom} <-> {lien.equipement2.nom} "
                  f"[{lien.bandwidth} Mbps / {lien.latency} ms]")
    print("="*50)

# afficher les details d'un equipement choisi
def menu_details_equipement(topo):
    """Affiche les proprietes completes d'un equipement choisi."""
    print("\n--- Details d'un equipement ---")
    if not topo.equipements:
        print("  Aucun equipement dans la topologie.")
        return
    print("  Equipements disponibles :")
    for eq in topo.equipements:
        print(f"    - {eq.nom} ({eq.adresse_ip})")
    nom   = input("  Nom de l'equipement : ").strip()
    cible = None
    for eq in topo.equipements:
        if eq.nom == nom:
            cible = eq
            break
    if cible:
        print()
        cible.afficher_infos()
    else:
        print(f"[ERREUR] '{nom}' introuvable.")


def menu_envoyer_paquet(sim, moniteur, topo):
    """Envoie un paquet entre deux equipements."""
    print("\n--- Envoyer un paquet ---")

    # lister tous les equipements avec leur IP
    print("\n  Equipements disponibles :")
    for eq in topo.equipements:
        statut = "ACTIF" if eq.est_actif else "INACTIF"
        print(f"    [{statut}] {eq.nom:15s} IP : {eq.adresse_ip}")

    print()
    src = input("  IP source       : ").strip()
    dst = input("  IP destination  : ").strip()

    print("\n  Protocoles : 1=TCP  2=UDP  3=ICMP")
    choix     = input("  Choix           : ").strip()
    protocole = {"1": "TCP", "2": "UDP", "3": "ICMP"}.get(choix, "TCP")

    # expliquer la priorite
    print("\n  Priorite du paquet :")
    print("    1 = tres basse  (ex: email non urgent)")
    print("    2 = basse       (ex: telechargement fichier)")
    print("    3 = normale     (ex: navigation web)")
    print("    4 = haute       (ex: video en streaming)")
    print("    5 = tres haute  (ex: appel voix, urgence reseau)")

    try:
        taille   = int(input("  Taille (octets)       : "))
        priorite = int(input("  Priorite (1-5)        : "))
        port     = int(input("  Port dest (0 si ICMP) : "))
        paquet   = Paquet(src, dst, protocole, taille, priorite, port)
        sim.envoyer_paquet(paquet)
        moniteur.enregistrer_paquet(paquet)
    except ValueError as e:
        print(f"[ERREUR] {e}")



def menu_firewall(sim, topo, moniteur):
    """Sous-menu de gestion du firewall."""
    print("\n--- Gestion du Firewall ---")


    # Chercher un Firewall existant dans la topologie
    fw_existant = None
    for eq in topo.equipements:
        if type(eq).__name__ == "Firewall":
            fw_existant = eq
            break

    if not hasattr(sim, 'gestion_firewall') or not sim.gestion_firewall:
        if fw_existant:
            gestion = GestionFirewall(fw_existant)
            sim.set_gestion_firewall(gestion)
            print(f"[OK] Firewall '{fw_existant.nom}' detecte et configure.")
        else:
            print("  Aucun firewall dans la topologie.")
            reponse = input("  Creer un firewall ? (o/n) : ").strip().lower()
            if reponse != "o":
                return
            nom    = input("  Nom        : ").strip()
            marque = input("  Marque     : ").strip()
            ip     = input("  IP         : ").strip()
            login  = input("  Login      : ").strip()
            mdp    = input("  Mot de passe : ").strip()
            try:
                fw = Firewall(nom, marque, ip, login, mdp)
                fw.activer()
                topo.add_equipement(fw)
                moniteur.ajouter_equipement(fw)
                gestion = GestionFirewall(fw)
                sim.set_gestion_firewall(gestion)
                print(f"[OK] Firewall {nom} cree.")
            except ValueError as e:
                print(f"[ERREUR] {e}")
                return

    gestion = sim.gestion_firewall

    print("\n  1. Ajouter une regle de filtrage")
    print("  2. Afficher le journal")
    print("  0. Retour")
    sous_choix = input("  Choix : ").strip()

    if sous_choix == "1":

        login  = input("  Login        : ").strip()
        mdp    = input("  Mot de passe : ").strip()
        action = input("  Action (bloquer/autoriser) : ").strip().lower()
        ip_src = input("  IP source (vide = toutes)  : ").strip() or None
        proto  = input("  Protocole (vide = tous)    : ").strip() or None
        try:
            port = int(input("  Port dest (0 = tous) : "))
        except ValueError:
            port = 0
        gestion.ajouter_regle(login, mdp, action, ip_src, proto, port)

    elif sous_choix == "2":
        gestion.afficher_journal()


def menu_statistiques(sim):
    """Affiche les statistiques et l'historique."""
    sim.afficher_statistiques()
    sim.afficher_historique()


def menu_rapport(moniteur):
    """Genere le rapport d'exploitation."""
    moniteur.generer_rapport()


def afficher_menu():
    """Affiche le menu principal."""
    print("\n" + "="*50)
    print("     SIMNet - Simulateur de Reseau")
    print("="*50)
    print("  1. Ajouter un equipement")
    print("  2. Supprimer un equipement")
    print("  3. Ajouter un lien")
    print("  4. Afficher la topologie")
    print("  5. Envoyer un paquet")
    print("  6. Gestion du Firewall / Journal")
    print("  7. Statistiques et historique")
    print("  8. Details d'un equipement")
    print("  9. Generer le rapport")
    print("  0. Quitter")
    print("="*50)


def main():
    """Point d'entree — boucle du menu interactif."""
    print("\n" + "="*50)
    print("   Bienvenue dans SIMNet !")
    print("   Simulateur de Reseau Intelligent")
    print("="*50)

    topo, sim, moniteur = initialiser_reseau()
    print("\n[OK] Reseau de demonstration initialise.")

    while True:
        afficher_menu()
        choix = input("  Votre choix : ").strip()

        if   choix == "1": menu_ajouter_equipement(topo, moniteur)
        elif choix == "2": menu_supprimer_equipement(topo, moniteur)
        elif choix == "3": menu_ajouter_lien(topo)
        elif choix == "4": menu_afficher_topologie(topo)
        elif choix == "5": menu_envoyer_paquet(sim, moniteur, topo)
        elif choix == "6": menu_firewall(sim, topo, moniteur)
        elif choix == "7": menu_statistiques(sim)
        elif choix == "8": menu_details_equipement(topo)
        elif choix == "9": menu_rapport(moniteur)
        elif choix == "0":
            print("\n[SIMNet] Arret du simulateur. Au revoir !")
            break
        else:
            print("  [ERREUR] Choix invalide. Entrez un nombre entre 0 et 9.")


if __name__ == "__main__":
    main()
