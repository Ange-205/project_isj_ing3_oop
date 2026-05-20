class link:
    def __init__(self,equipement1,equipement2,bandwidth,latency):
        self.equipement1=equipement1
        self.equipement2=equipement2
        self.bandwidth=bandwidth
        self.latency=latency
        
class topology:
    def __init__(self):
        self.equipements = []
        self.link = []
        self.connections={}

def add_equipement(self,equipement):
    self.equipements.append(equipement)
    self.connections[equipement]=[]