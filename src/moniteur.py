from equipements import Equipement
from paquets import Paquet

class MoniteurReseau:
    def __init__(self):
        self.equipements = []
        self.stats_paquets = {}
        self.historique = []

    def ajouter_equipement(self, equipement):
        self.equipements.append(equipement)
