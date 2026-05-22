from equipements import Equipement, Routeur
from topologie   import topology, Link
from paquets     import Paquet, Simulateur
from securite    import RegleFirewall, GestionFirewall
from moniteur    import MoniteurReseau


def initialiser_reseau():
    topo     = topology()
    moniteur = MoniteurReseau()

    r1  = Routeur("R_Core",   "Cisco",   "10.0.0.1", 4)
    r2  = Routeur("R_Edge",   "Juniper", "10.0.0.2", 2)
    sw1 = Equipement("SW_Distrib", "HP",   "10.0.1.1")
    sv1 = Equipement("SRV_Web",    "Dell", "10.0.2.1")

    for eq in [r1, r2, sw1, sv1]:
        topo.add_equipement(eq)
        moniteur.ajouter_equipement(eq)
        eq.activer()

    topo.add_link(r1,  r2,  1000, 1.5)
    topo.add_link(r1,  sw1, 1000, 0.5)
    topo.add_link(sw1, sv1, 100,  0.3)

    sim = Simulateur(topo)
    return topo, sim, moniteur


def menu_ajouter_equipement(topo, moniteur):
    """Ajoute un équipement à la topologie."""
    print("\n--- Ajouter un équipement ---")
    nom    = input("Nom        : ").strip()
    marque = input("Marque     : ").strip()
    ip     = input("Adresse IP : ").strip()
    try:
        eq = Equipement(nom, marque, ip)
        topo.add_equipement(eq)
        moniteur.ajouter_equipement(eq)
        eq.activer()
        print(f"[OK] {nom} ajouté et activé.")
    except ValueError as e:
        print(f"[ERREUR] {e}")


def menu_supprimer_equipement(topo, moniteur):
    """Supprime un équipement de la topologie."""
    print("\n--- Supprimer un équipement ---")
    if not topo.equipements:
        print("  Aucun équipement dans la topologie.")
        return
    print("Équipements :")
    for eq in topo.equipements:
        print(f"  - {eq.nom} ({eq.adresse_ip})")
    nom    = input("Nom à supprimer : ").strip()
    cible  = None
    for eq in topo.equipements:
        if eq.nom == nom:
            cible = eq
            break
    if cible:
        topo.delete_equipement(cible)
        if cible in moniteur.equipements:
            moniteur.equipements.remove(cible)
        print(f"[OK] {nom} supprimé.")
    else:
        print(f"[ERREUR] '{nom}' introuvable.")


def menu_ajouter_lien(topo):
    """Ajoute un lien entre deux équipements."""
    print("\n--- Ajouter un lien ---")
    if len(topo.equipements) < 2:
        print("  Il faut au moins 2 équipements.")
        return
    print("Équipements disponibles :")
    for eq in topo.equipements:
        print(f"  - {eq.nom}")
    nom1 = input("Équipement 1 : ").strip()
    nom2 = input("Équipement 2 : ").strip()
    eq1  = eq2 = None
    for eq in topo.equipements:
        if eq.nom == nom1: eq1 = eq
        if eq.nom == nom2: eq2 = eq
    if not eq1 or not eq2:
        print("[ERREUR] Un ou deux équipements introuvables.")
        return
    try:
        bp  = float(input("Bande passante (Mbps) : "))
        lat = float(input("Latence (ms)          : "))
        topo.add_link(eq1, eq2, bp, lat)
        print(f"[OK] Lien {nom1} <-> {nom2} ajouté.")
    except ValueError:
        print("[ERREUR] Valeur invalide.")


def menu_afficher_topologie(topo):
    """Affiche tous les équipements et liens du réseau."""
    print("\n" + "="*50)
    print("  TOPOLOGIE DU RÉSEAU")
    print("="*50)
    print(f"\n  Équipements ({len(topo.equipements)}) :")
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


def menu_envoyer_paquet(sim, moniteur):
    """Envoie un paquet entre deux équipements."""
    print("\n--- Envoyer un paquet ---")
    src  = input("IP source       : ").strip()
    dst  = input("IP destination  : ").strip()
    print("Protocole : 1=TCP  2=UDP  3=ICMP")
    choix     = input("Choix           : ").strip()
    protocole = {"1": "TCP", "2": "UDP", "3": "ICMP"}.get(choix, "TCP")
    try:
        taille   = int(input("Taille (octets) : "))
        priorite = int(input("Priorité (1-5)  : "))
        port     = int(input("Port dest (0 si ICMP) : "))
        paquet   = Paquet(src, dst, protocole, taille, priorite, port)
        sim.envoyer_paquet(paquet)
        moniteur.enregistrer_paquet(paquet)
    except ValueError as e:
        print(f"[ERREUR] {e}")


def menu_firewall(sim, topo, moniteur):
    """Sous-menu de gestion du firewall."""
    print("\n--- Gestion du Firewall ---")

    if not hasattr(sim, 'gestion_firewall') or not sim.gestion_firewall:
        print("  Aucun firewall configuré.")
        reponse = input("  Créer un firewall ? (o/n) : ").strip().lower()
        if reponse != "o":
            return
        nom    = input("Nom du firewall : ").strip()
        marque = input("Marque         : ").strip()
        ip     = input("IP             : ").strip()
        login  = input("Login admin    : ").strip()
        mdp    = input("Mot de passe   : ").strip()

        # On crée un Equipement générique comme Firewall
        # car la classe Firewall n'est pas dans equipements.py
        fw          = Equipement(nom, marque, ip)
        fw.login    = login
        fw.mot_de_passe = mdp
        fw.regles   = []
        fw.journal  = []
        fw.activer()

        topo.add_equipement(fw)
        moniteur.ajouter_equipement(fw)

        gestion = GestionFirewall(fw)
        sim.set_gestion_firewall(gestion)
        print(f"[OK] Firewall {nom} créé.")

    gestion = sim.gestion_firewall

    print("\n  1. Ajouter une règle")
    print("  2. Afficher le journal")
    sous_choix = input("  Choix : ").strip()

    if sous_choix == "1":
        login  = input("Login        : ").strip()
        mdp    = input("Mot de passe : ").strip()
        action = input("Action (bloquer/autoriser) : ").strip().lower()
        ip_src = input("IP source (vide = toutes) : ").strip() or None
        proto  = input("Protocole (vide = tous)   : ").strip() or None
        try:
            port = int(input("Port dest (0 = tous) : "))
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
    """Génère le rapport d'exploitation."""
    moniteur.generer_rapport()


def afficher_menu():
    """Affiche le menu principal."""
    print("\n" + "="*50)
    print("     SIMNet — Simulateur de Réseau    ")
    print("="*50)
    print("  1. Ajouter un équipement")
    print("  2. Supprimer un équipement")
    print("  3. Ajouter un lien")
    print("  4. Afficher la topologie")
    print("  5. Envoyer un paquet")
    print("  6. Gestion du Firewall / Journal")
    print("  7. Statistiques et historique")
    print("  8. Générer le rapport")
    print("  9. Quitter")
    print("="*50)


def main():
    """Point d'entrée — boucle du menu interactif."""
    print("\n" + "="*50)
    print("   Bienvenue dans SIMNet !")
    print("   Simulateur de Réseau Intelligent")
    print("="*50)

    topo, sim, moniteur = initialiser_reseau()
    print("\n[OK] Réseau de démonstration initialisé.")

    while True:
        afficher_menu()
        choix = input("  Votre choix : ").strip()

        if   choix == "1": menu_ajouter_equipement(topo, moniteur)
        elif choix == "2": menu_supprimer_equipement(topo, moniteur)
        elif choix == "3": menu_ajouter_lien(topo)
        elif choix == "4": menu_afficher_topologie(topo)
        elif choix == "5": menu_envoyer_paquet(sim, moniteur)
        elif choix == "6": menu_firewall(sim, topo, moniteur)
        elif choix == "7": menu_statistiques(sim)
        elif choix == "8": menu_rapport(moniteur)
        elif choix == "9":
            print("\n[SIMNet] Arrêt du simulateur. Au revoir !")
            break
        else:
            print("  [ERREUR] Choix invalide. Entrez un nombre entre 1 et 9.")


if __name__ == "__main__":
    main()
