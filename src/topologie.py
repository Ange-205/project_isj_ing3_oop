class test_equipement:
    def __init__(self,name):
        self.name=name
class Link:
    def __init__(self,equipement1,equipement2,bandwidth,latency):
        self.equipement1=equipement1
        self.equipement2=equipement2
        self.bandwidth=bandwidth
        self.latency=latency
        
class topology: 
    def __init__(self):
        self.equipements = []
        self.links = []
        self.connections={}

    def add_equipement(self,equipement):
        self.equipements.append(equipement)
        self.connections[equipement]=[]
        
    def add_link(self,equipement1,equipement2,bandwidth,latency):
        link = Link(equipement1,equipement2,bandwidth,latency)
        self.links.append(link)
        self.connections[equipement1].append(equipement2)
        self.connections[equipement2].append(equipement1)
        
    def find_path(self,start,destination):
        visits=[]
        queue=[]
        parents = {}
        queue.append(start)
        visits.append(start)
        parents[start]=None
        while queue:
            current=queue.pop(0)
            if current == destination:
                route = []
                actual = destination
                while actual is not None:
                    route.append(actual)
                    actual = parents[actual]
                route.reverse()
                return route             
            for neigbors in self.connections[current]:
                if neigbors not in visits:
                    visits.append(neigbors)
                    parents[neigbors]=current
                    queue.append(neigbors)
        return False
       
    def delete_equipement(self,equipement):
        for neigbors in self.connections[equipement]:
            self.connections[neigbors].remove(equipement)
        del self.connections[equipement]
        self.equipements.remove(equipement)
        for link in self.links[:]:
            if link.equipement1==equipement or \
                link.equipement2==equipement:
                self.links.remove(link)
r1=test_equipement('router')
s2=test_equipement('switch') 
l1=Link(r1, s2, 100, 10)    
print(l1.latency)
topo=topology()
r1=test_equipement('router')
topo.add_equipement(s2)
print(topo.equipements)