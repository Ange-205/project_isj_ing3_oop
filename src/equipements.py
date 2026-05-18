# src/equipements.py

from abc import ABC, abstractmethod
import datetime

class Equipement:
    """Modélise un équipement réseau générique."""

    _nb_equipements = 0  

    def __init__(self, nom, marque, adresse_ip):
        self.nom = nom
        self.marque = marque
        self.adresse_ip = adresse_ip 
        self.est_actif = False
        Equipement._nb_equipements += 1

    @property
    def adresse_ip(self):
        return self._adresse_ip

    @adresse_ip.setter
    def adresse_ip(self, valeur):
        """Valide le format IPv4 avant d'affecter."""
        parties = valeur.split(".")
        if len(parties) != 4:
            raise ValueError(f"Adresse IP invalide : {valeur}")
        for partie in parties:
            if not partie.isdigit() or not (0 <= int(partie) <= 255):
                raise ValueError(f"Adresse IP invalide : {valeur}")
        self._adresse_ip = valeur

    def activer(self):
        """Active l'équipement."""
        self.est_actif = True
        print(f"[ACTIVATION] {self.nom} activé.")

    def desactiver(self):
        """Désactive l'équipement."""
        self.est_actif = False
        print(f"[DÉSACTIVATION] {self.nom} désactivé.")

    def afficher_infos(self):
        """Affiche les informations de base de l'équipement."""
        statut = "ACTIF" if self.est_actif else "INACTIF"
        print(f"  Nom    : {self.nom}")
        print(f"  Marque : {self.marque}")
        print(f"  IP     : {self._adresse_ip}")
        print(f"  Statut : {statut}")

    def diagnostiquer(self):
        """Retourne un dictionnaire d'informations pour le moniteur."""
        return {
            "type": self.__class__.__name__,
            "nom": self.nom,
            "ip": self._adresse_ip,
            "marque": self.marque,
            "statut": "ACTIF" if self.est_actif else "INACTIF"
        }

    @classmethod
    def get_nb_equipements(cls):
        """Retourne le nombre total d'équipements créés."""
        return cls._nb_equipements

    def __str__(self):
        statut = "ACTIF" if self.est_actif else "INACTIF"
        return f"[{statut}] {self.nom} ({self.marque}) -- {self._adresse_ip}"

    def __repr__(self):
        return f"Equipement(nom='{self.nom}', ip='{self._adresse_ip}')"
class Routeur(Equipement):
    """Modélise un routeur réseau avec table de routage."""

    def __init__(self, nom, marque, adresse_ip, nb_interfaces):
        super().__init__(nom, marque, adresse_ip)
        self.nb_interfaces = nb_interfaces
        self.table_routage = [] 

    def ajouter_route(self, reseau):
        """Ajoute une route à la table de routage."""
        if reseau not in self.table_routage:
            self.table_routage.append(reseau)
            print(f"[ROUTEUR] Route {reseau} ajoutée sur {self.nom}.")
        else:
            print(f"[ROUTEUR] Route {reseau} déjà présente.")

    def supprimer_route(self, reseau):
        """Supprime une route de la table de routage."""
        if reseau in self.table_routage:
            self.table_routage.remove(reseau)
            print(f"[ROUTEUR] Route {reseau} supprimée.")
        else:
            print(f"[ROUTEUR] Route {reseau} introuvable.")

    def afficher_infos(self):
        """Affiche les infos du routeur, y compris la table de routage."""
        super().afficher_infos()
        print(f"  Interfaces : {self.nb_interfaces}")
        print(f"  Table de routage ({len(self.table_routage)} routes) :")
        if self.table_routage:
            for route in self.table_routage:
                print(f"    -> {route}")
        else:
            print("    (vide)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au routeur."""
        diag = super().diagnostiquer()
        diag["nb_interfaces"] = self.nb_interfaces
        diag["nb_routes"] = len(self.table_routage)
        return diag

    def __repr__(self):
        return f"Routeur(nom='{self.nom}', ip='{self._adresse_ip}', interfaces={self.nb_interfaces})"