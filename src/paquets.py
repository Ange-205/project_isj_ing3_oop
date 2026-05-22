import datetime
from equipements import Equipement

class Paquet:
    """
    Modélise un paquet réseau circulant dans le simulateur.

    Attributs :
        source      : adresse IP source (str)
        destination : adresse IP destination (str)
        protocole   : 'TCP', 'UDP' ou 'ICMP' (str)
        taille      : taille en octets (int)
        priorite    : niveau de 1 (basse) à 5 (haute) (int)
        port_dest   : port destination, 0 par défaut (int)
    """

    PROTOCOLES_VALIDES = ("TCP", "UDP", "ICMP")
    _nb_paquets_crees  = 0

    def __init__(self, source, destination, protocole, taille, priorite, port_dest=0):
        if protocole.upper() not in self.PROTOCOLES_VALIDES:
            raise ValueError(f"Protocole invalide : {protocole}. Choisir TCP, UDP ou ICMP.")
        if not (1 <= priorite <= 5):
            raise ValueError(f"Priorité invalide : {priorite}. Doit être entre 1 et 5.")
        if taille <= 0:
            raise ValueError(f"Taille invalide : {taille}. Doit être positive.")

        self.source      = source
        self.destination = destination
        self.protocole   = protocole.upper()
        self.taille      = taille
        self.priorite    = priorite
        self.port_dest   = port_dest
        self.horodatage  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.statut      = "EN_ATTENTE"   # EN_ATTENTE, TRANSMIS, PERDU, BLOQUE

        Paquet._nb_paquets_crees += 1
        self.id = Paquet._nb_paquets_crees

    @classmethod
    def get_nb_paquets_crees(cls):
        """Retourne le nombre total de paquets créés."""
        return cls._nb_paquets_crees

    def __str__(self):
        return (f"Paquet#{self.id} [{self.protocole}] {self.source} -> {self.destination}"
                f" | {self.taille} octets | priorité {self.priorite} | {self.statut}")

    def __repr__(self):
        return (f"Paquet(src='{self.source}', dst='{self.destination}', "
                f"proto='{self.protocole}', taille={self.taille}, prio={self.priorite})")

    def __lt__(self, autre):
        """Comparaison par priorité — priorité haute traitée en premier."""
        return self.priorite > autre.priorite

    def __eq__(self, autre):
        """Deux paquets sont égaux s'ils ont le même identifiant."""
        if isinstance(autre, Paquet):
            return self.id == autre.id
        return False


class Simulateur:
    """
    Gère l'envoi de paquets sur la topologie réseau saut par saut.

    Utilise find_path() de la Topologie pour déterminer le chemin
    le plus court (BFS) entre deux équipements.

    Attributs :
        topologie        : instance de Topologie
        paquets_envoyes  : nombre total de paquets envoyés
        paquets_perdus   : paquets dont la destination est inatteignable
        paquets_bloques  : paquets bloqués par un firewall
        debit_cumule     : octets transmis avec succès
        temps_total      : somme des temps de transit en ms
        historique       : 10 derniers paquets traités
    """

    HISTORIQUE_MAX = 10

    def __init__(self, topologie):
        self.topologie       = topologie
        self.paquets_envoyes = 0
        self.paquets_perdus  = 0
        self.paquets_bloques = 0
        self.debit_cumule    = 0      # en octets
        self.temps_total     = 0.0   # en ms
        self.historique      = []

    def envoyer_paquet(self, paquet):
        """
        Envoie un paquet à travers la topologie.

        Etapes :
            1. Localiser les equipements source et destination par IP
            2. Calculer le chemin avec find_path()
            3. Traverser le chemin saut par saut
            4. Verifier le firewall si present sur le chemin
            5. Mettre a jour les statistiques

        Retourne True si le paquet est livre, False sinon.
        """
        self.paquets_envoyes += 1
        print(f"\n{'='*50}")
        print(f"  ENVOI : {paquet}")
        print(f"{'='*50}")

        # Etape 1 — localiser source et destination
        equip_src = self._get_equipement_par_ip(paquet.source)
        equip_dst = self._get_equipement_par_ip(paquet.destination)

        if not equip_src:
            print(f"  [X] Source introuvable : {paquet.source}")
            return self._echec(paquet, "PERDU")

        if not equip_dst:
            print(f"  [X] Destination introuvable : {paquet.destination}")
            return self._echec(paquet, "PERDU")

        if not equip_src.est_actif:
            print(f"  [X] Source inactive : {equip_src.nom}")
            return self._echec(paquet, "PERDU")

        # Etape 2 — calculer le chemin (find_path retourne une liste d'equipements)
        chemin = self.topologie.find_path(equip_src, equip_dst)

        if not chemin:
            print(f"  [X] Destination INATTEIGNABLE : {paquet.destination}")
            return self._echec(paquet, "PERDU")

        noms_chemin = [eq.name for eq in chemin]
        print(f"\n  Chemin : {' -> '.join(noms_chemin)}")

        # Etape 3 et 4 — traverser saut par saut
        temps_transit = 0.0

        for i in range(len(chemin) - 1):
            equip_actuel  = chemin[i]
            equip_suivant = chemin[i + 1]

            # Recuperer le lien entre les deux equipements
            lien = self._get_lien(equip_actuel, equip_suivant)
            if lien:
                temps_transit     += lien.latency
                print(f"  [{i+1}] {equip_actuel.name} -> {equip_suivant.name} "
                      f"[{lien.bandwidth} Mbps / {lien.latency} ms]")

            # Etape 4 — verifier si l'equipement suivant est un Firewall
            # On verifie par le nom de la classe pour eviter l'import circulaire
            if type(equip_suivant).__name__ == "Firewall":
                print(f"  [FW] Firewall detecte : {equip_suivant.nom}")
                gestion = self._get_gestion_firewall(equip_suivant)
                if gestion:
                    decision = gestion.inspecter_paquet(paquet)
                    if decision == "bloquer":
                        print(f"  [X] Bloque par {equip_suivant.nom}")
                        return self._echec(paquet, "BLOQUE")

        # Etape 5 — succes
        paquet.statut     = "TRANSMIS"
        self.debit_cumule += paquet.taille
        self.temps_total  += temps_transit
        self._ajouter_historique(paquet)

        print(f"\n  [OK] Livre en {temps_transit:.2f} ms | "
              f"Debit cumule : {self.debit_cumule} octets")
        return True

    def _echec(self, paquet, statut):
        """Gere un echec d'envoi : met a jour le statut et les compteurs."""
        paquet.statut = statut
        if statut == "PERDU":
            self.paquets_perdus  += 1
        else:
            self.paquets_bloques += 1
        self._ajouter_historique(paquet)
        return False

    def _get_equipement_par_ip(self, ip):
        """Cherche un equipement par IP dans la topologie. Retourne None si absent."""
        for equip in self.topologie.equipements:
            if equip.adresse_ip == ip:
                return equip
        return None

    def _get_lien(self, equip1, equip2):
        """Retourne le lien entre deux equipements s'il existe, None sinon."""
        for lien in self.topologie.links:
            if ((lien.equipement1 == equip1 and lien.equipement2 == equip2) or
                (lien.equipement1 == equip2 and lien.equipement2 == equip1)):
                return lien
        return None

    def _get_gestion_firewall(self, firewall):
        if hasattr(self, 'gestion_firewall'):
            return self.gestion_firewall
        return None

    def set_gestion_firewall(self, gestion):
        self.gestion_firewall = gestion

    def _ajouter_historique(self, paquet):
        self.historique.append(paquet)
        if len(self.historique) > self.HISTORIQUE_MAX:
            self.historique.pop(0)

    def get_statistiques(self):
        transmis    = self.paquets_envoyes - self.paquets_perdus - self.paquets_bloques
        taux_succes = (transmis / self.paquets_envoyes * 100) if self.paquets_envoyes > 0 else 0
        temps_moyen = (self.temps_total / transmis) if transmis > 0 else 0
           
        return {
            "paquets_envoyes" : self.paquets_envoyes,
            "paquets_transmis": transmis,
            "paquets_perdus"  : self.paquets_perdus,
            "paquets_bloques" : self.paquets_bloques,
            "taux_succes"     : round(taux_succes, 1),
            "debit_octets"    : self.debit_cumule,
            "temps_total_ms"  : round(self.temps_total, 2),
            "temps_moyen_ms"  : round(temps_moyen, 2),
        }  # Retourne un dictionnaire des statistiques de simulation

    def afficher_statistiques(self):
        s = self.get_statistiques()
        print("\n" + "="*45)
        print("      STATISTIQUES DU SIMULATEUR")
        print("="*45)
        print(f"  Paquets envoyes  : {s['paquets_envoyes']}")
        print(f"  Paquets livres   : {s['paquets_transmis']}")
        print(f"  Paquets perdus   : {s['paquets_perdus']}")
        print(f"  Paquets bloques  : {s['paquets_bloques']}")
        print(f"  Taux de succes   : {s['taux_succes']} %")
        print(f"  Debit cumule     : {s['debit_octets']} octets")
        print(f"  Temps total      : {s['temps_total_ms']} ms")
        print(f"  Temps moyen/paquet: {s['temps_moyen_ms']} ms")
        print("="*45) #Affiche les statistiques de la simulation

    def afficher_historique(self):
        print("\n" + "="*45)
        print(f"   HISTORIQUE (10 derniers paquets)")
        print("="*45)
        if not self.historique:
            print("  Aucun paquet traite.")
        else:
            for i, p in enumerate(self.historique, 1):
                print(f"  [{i:02d}] {p}")
        print("="*45) #Affiche les 10 derniers paquets traites
        