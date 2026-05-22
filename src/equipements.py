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
    
class Switch(Equipement):
    """Modélise un switch réseau capable de gérer des VLANs."""

    def __init__(self, nom, marque, adresse_ip, nb_ports):
        super().__init__(nom, marque, adresse_ip)
        self.nb_ports = nb_ports
        self.vlan_actifs = []  
    def ajouter_vlan(self, id_vlan, nom_vlan):
        """Ajoute un VLAN au switch s'il n'existe pas déjà."""
        for vlan in self.vlan_actifs:
            if vlan["id"] == id_vlan:
                print(f"[SWITCH] VLAN {id_vlan} déjà présent sur {self.nom}.")
                return
        self.vlan_actifs.append({"id": id_vlan, "nom": nom_vlan})
        print(f"[SWITCH] VLAN {id_vlan} ({nom_vlan}) ajouté sur {self.nom}.")

    def supprimer_vlan(self, id_vlan):
        """Supprime un VLAN du switch par son identifiant."""
        for vlan in self.vlan_actifs:
            if vlan["id"] == id_vlan:
                self.vlan_actifs.remove(vlan)
                print(f"[SWITCH] VLAN {id_vlan} supprimé de {self.nom}.")
                return
        print(f"[SWITCH] VLAN {id_vlan} introuvable sur {self.nom}.")

    def afficher_infos(self):
        """Affiche les infos du switch, y compris les VLANs actifs."""
        super().afficher_infos()
        print(f"  Ports      : {self.nb_ports}")
        print(f"  VLANs actifs ({len(self.vlan_actifs)}) :")
        if self.vlan_actifs:
            for vlan in self.vlan_actifs:
                print(f"    -> VLAN {vlan['id']} : {vlan['nom']}")
        else:
            print("    (aucun VLAN configuré)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au switch."""
        diag = super().diagnostiquer()
        diag["nb_ports"] = self.nb_ports
        diag["nb_vlans"] = len(self.vlan_actifs)
        return diag

    def __repr__(self):
        return f"Switch(nom='{self.nom}', ip='{self._adresse_ip}', ports={self.nb_ports})"
    
class Serveur(Equipement):
    """Modélise un serveur exposant des services réseau."""

    def __init__(self, nom, marque, adresse_ip, ram_go, cpu_coeurs):
        super().__init__(nom, marque, adresse_ip)
        self.ram_go = ram_go          
        self.cpu_coeurs = cpu_coeurs 
        self.services = []            

    def demarrer_service(self, service):
        """Démarre un service sur le serveur s'il n'est pas déjà actif."""
        if not self.est_actif:
            print(f"[SERVEUR] Impossible de démarrer {service} : {self.nom} est inactif.")
            return
        if service not in self.services:
            self.services.append(service)
            print(f"[SERVEUR] Service {service} démarré sur {self.nom}.")
        else:
            print(f"[SERVEUR] Service {service} déjà actif sur {self.nom}.")

    def arreter_service(self, service):
        """Arrête un service actif sur le serveur."""
        if service in self.services:
            self.services.remove(service)
            print(f"[SERVEUR] Service {service} arrêté sur {self.nom}.")
        else:
            print(f"[SERVEUR] Service {service} introuvable sur {self.nom}.")

    def afficher_infos(self):
        """Affiche les infos du serveur, y compris les services actifs."""
        super().afficher_infos()
        print(f"  RAM        : {self.ram_go} Go")
        print(f"  CPU        : {self.cpu_coeurs} coeurs")
        print(f"  Services actifs ({len(self.services)}) :")
        if self.services:
            for service in self.services:
                print(f"    -> {service}")
        else:
            print("    (aucun service actif)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au serveur."""
        diag = super().diagnostiquer()
        diag["ram_go"] = self.ram_go
        diag["cpu_coeurs"] = self.cpu_coeurs
        diag["services"] = self.services
        return diag

    def __repr__(self):
        return f"Serveur(nom='{self.nom}', ip='{self._adresse_ip}', ram={self.ram_go}Go)"
    
class PointAccesWifi(Equipement):
    """Modélise un point d'accès Wi-Fi gérant des clients sans fil."""

    def __init__(self, nom, marque, adresse_ip, ssid, canal):
        super().__init__(nom, marque, adresse_ip)
        self.ssid = ssid       
        self.canal = canal 
        self.clients = []       

    def connecter_client(self, adresse_mac):
        """Connecte un client Wi-Fi via son adresse MAC."""
        if not self.est_actif:
            print(f"[WIFI] {self.nom} est inactif, connexion impossible.")
            return
        if adresse_mac not in self.clients:
            self.clients.append(adresse_mac)
            print(f"[WIFI] Client {adresse_mac} connecté au réseau {self.ssid}.")
        else:
            print(f"[WIFI] Client {adresse_mac} déjà connecté.")

    def deconnecter_client(self, adresse_mac):
        """Déconnecte un client Wi-Fi via son adresse MAC."""
        if adresse_mac in self.clients:
            self.clients.remove(adresse_mac)
            print(f"[WIFI] Client {adresse_mac} déconnecté du réseau {self.ssid}.")
        else:
            print(f"[WIFI] Client {adresse_mac} introuvable sur {self.nom}.")

    def afficher_infos(self):
        """Affiche les infos du point d'accès, y compris les clients connectés."""
        super().afficher_infos()
        print(f"  SSID       : {self.ssid}")
        print(f"  Canal      : {self.canal}")
        print(f"  Clients connectés ({len(self.clients)}) :")
        if self.clients:
            for client in self.clients:
                print(f"    -> {client}")
        else:
            print("    (aucun client connecté)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au point d'accès Wi-Fi."""
        diag = super().diagnostiquer()
        # On ajoute les infos propres au point d'accès
        diag["ssid"] = self.ssid
        diag["canal"] = self.canal
        diag["nb_clients"] = len(self.clients)
        return diag

    def __repr__(self):
        return f"PointAccesWifi(nom='{self.nom}', ip='{self._adresse_ip}', ssid='{self.ssid}')"
    
class Terminal(Equipement):
    """Modélise un terminal client (PC, laptop, etc.) connecté au réseau."""

    def __init__(self, nom, marque, adresse_ip, type_terminal, adresse_mac):
        super().__init__(nom, marque, adresse_ip)
        self.type_terminal = type_terminal 
        self.adresse_mac = adresse_mac      
        self.passerelle = None              
        self.applications = []            
    def configurer_passerelle(self, ip_passerelle):
        """Configure la passerelle par défaut du terminal."""
        self.passerelle = ip_passerelle
        print(f"[TERMINAL] Passerelle de {self.nom} configurée : {ip_passerelle}.")

    def lancer_application(self, application):
        """Lance une application sur le terminal."""
        if not self.est_actif:
            print(f"[TERMINAL] {self.nom} est inactif, impossible de lancer {application}.")
            return
        if application not in self.applications:
            self.applications.append(application)
            print(f"[TERMINAL] Application {application} lancée sur {self.nom}.")
        else:
            print(f"[TERMINAL] {application} est déjà en cours d'exécution.")

    def fermer_application(self, application):
        """Ferme une application active sur le terminal."""
        if application in self.applications:
            self.applications.remove(application)
            print(f"[TERMINAL] Application {application} fermée sur {self.nom}.")
        else:
            print(f"[TERMINAL] Application {application} introuvable sur {self.nom}.")

    def afficher_infos(self):
        """Affiche les infos du terminal, y compris ses applications actives."""
        super().afficher_infos()
        print(f"  Type       : {self.type_terminal}")
        print(f"  MAC        : {self.adresse_mac}")
        print(f"  Passerelle : {self.passerelle if self.passerelle else 'Non configurée'}")
        print(f"  Applications actives ({len(self.applications)}) :")
        if self.applications:
            for app in self.applications:
                print(f"    -> {app}")
        else:
            print("    (aucune application active)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au terminal."""
        diag = super().diagnostiquer()
        diag["type_terminal"] = self.type_terminal
        diag["adresse_mac"] = self.adresse_mac
        diag["passerelle"] = self.passerelle
        diag["nb_applications"] = len(self.applications)
        return diag

    def __repr__(self):
        return f"Terminal(nom='{self.nom}', ip='{self._adresse_ip}', type='{self.type_terminal}')"
    
class Authentifiable:
    """Mixin ajoutant la capacité d'authentification par login/mot de passe."""

    def __init__(self, login, mot_de_passe):
        self.__login = login
        self.__mot_de_passe = mot_de_passe

    def authentifier(self, login, mdp):
        """Vérifie les identifiants et retourne True si corrects, False sinon."""
        if self.__login == login and self.__mot_de_passe == mdp:
            print(f"[AUTH] Authentification réussie.")
            return True
        print(f"[AUTH] Identifiants incorrects. Accès refusé.")
        return False

    def changer_mot_de_passe(self, ancien_mdp, nouveau_mdp):
        """Change le mot de passe si l'ancien est correct."""
        if self.__mot_de_passe == ancien_mdp:
            self.__mot_de_passe = nouveau_mdp
            print(f"[AUTH] Mot de passe modifié avec succès.")
        else:
            print(f"[AUTH] Ancien mot de passe incorrect. Modification refusée.")


class Journalisable:
    """Mixin ajoutant la capacité de journalisation horodatée des événements."""

    def __init__(self):
        self.journal = []

    def logger(self, message):
        """Enregistre un message dans le journal avec horodatage."""
        horodatage = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entree = f"[{horodatage}] {message}"
        self.journal.append(entree)

    def afficher_journal(self):
        """Affiche toutes les entrées du journal."""
        print("\n--- Journal du Firewall ---")
        if self.journal:
            for entree in self.journal:
                print(f"  {entree}")
        else:
            print("  (journal vide)")

    def get_journal(self):
        """Retourne la liste brute du journal pour le moniteur réseau."""
        return self.journal


class Firewall(Equipement, Authentifiable, Journalisable):
    """Modélise un firewall combinant équipement réseau, authentification et journalisation.
    
    Hérite de :
        - Equipement : attributs et méthodes réseau de base
        - Authentifiable : protection par login/mot de passe
        - Journalisable : enregistrement horodaté des décisions
    """

    def __init__(self, nom, marque, adresse_ip, login, mot_de_passe):
        Equipement.__init__(self, nom, marque, adresse_ip)
        Authentifiable.__init__(self, login, mot_de_passe)
        Journalisable.__init__(self)
        self.regles = []                   
        self.nb_connexions_bloquees = 0   

    def ajouter_regle(self, regle):
        """Ajoute une règle de filtrage au firewall."""
        if regle not in self.regles:
            self.regles.append(regle)
            self.logger(f"Règle ajoutée : {regle}")
            print(f"[FIREWALL] Règle ajoutée : {regle}")
        else:
            print(f"[FIREWALL] Règle déjà existante.")

    def supprimer_regle(self, regle):
        """Supprime une règle de filtrage existante."""
        if regle in self.regles:
            self.regles.remove(regle)
            self.logger(f"Règle supprimée : {regle}")
            print(f"[FIREWALL] Règle supprimée : {regle}")
        else:
            print(f"[FIREWALL] Règle introuvable.")

    def inspecter_paquet(self, paquet):
        """Inspecte un paquet et décide de l'autoriser ou le bloquer.
        
        Retourne True si le paquet est autorisé, False s'il est bloqué.
        """
        for regle in self.regles:
            if paquet.protocole in regle or paquet.source in regle:
                self.nb_connexions_bloquees += 1
                self.logger(
                    f"BLOQUÉ | src={paquet.source} dst={paquet.destination} "
                    f"proto={paquet.protocole} | Règle : {regle}"
                )
                print(f"[FIREWALL] Paquet bloqué : {paquet.source} -> {paquet.destination}")
                return False
        self.logger(
            f"AUTORISÉ | src={paquet.source} dst={paquet.destination} "
            f"proto={paquet.protocole}"
        )
        return True

    def afficher_infos(self):
        """Affiche les infos du firewall, y compris les règles actives."""
        Equipement.afficher_infos(self)
        print(f"  Règles actives       : {len(self.regles)}")
        print(f"  Connexions bloquées  : {self.nb_connexions_bloquees}")
        if self.regles:
            for i, regle in enumerate(self.regles, 1):
                print(f"    {i}. {regle}")
        else:
            print("    (aucune règle configurée)")

    def diagnostiquer(self):
        """Étend le diagnostic avec les infos spécifiques au firewall."""
        diag = Equipement.diagnostiquer(self)
        diag["nb_regles"] = len(self.regles)
        diag["nb_connexions_bloquees"] = self.nb_connexions_bloquees
        return diag

    def __repr__(self):
        return f"Firewall(nom='{self.nom}', ip='{self._adresse_ip}')"
    
