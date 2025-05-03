import networkx as nx
import numpy as np

from collections import defaultdict
from typing import List, Dict, Tuple, Any
from itertools import islice

from Dataplane import Flow, Switch

class SDN:
    def __init__(self) -> None:
        self.graph = nx.Graph() # Graph to represent network
        self.util: Dict[Tuple[str, str], int] = defaultdict(int) # Link utilization 
        self.switches: Dict[str, Switch] = {} # Sets switchID to switch object
        self.backups: Dict[Tuple[str, str], List[str]] = {} # Backup paths
        self.RR: Dict[Tuple[str, str], int] = defaultdict(int) # Round robin

    def addSwitch(self, switchID: str) -> None: 
        if switchID not in self.switches: # Creates a switch object
            self.switches[switchID] = Switch(switchID) 
        if not self.graph.has_node(switchID): # Adds to the graph
            self.graph.add_node(switchID) 


    def addLink(self, src: str, dst: str, weight: int) -> None:
        self.addSwitch(src) # Checks if src exists
        self.addSwitch(dst) # Checks if dst exists
        self.graph.add_edge(src, dst, weight=weight) # Adds an edge to the graph
        self.switches[src].addPort("{}->{}".format(src, dst), dst) # Port on the src
        self.switches[dst].addPort("{}->{}".format(dst, src), src) # Port on the dst


    def removeLink(self, src: str, dst: str, weight: int = 1) -> None: 
        if self.graph.has_edge(src, dst): # Check edge exists
            self.graph.remove_edge(src, dst) # Removes the edge

    def kShortestPaths(self, src: str, dst: str, k: int = 2) -> List[List[str]]: # Finds up to k shortest paths
        paths = [] # List of paths
        for path in nx.shortest_simple_paths(self.graph, src, dst, weight="weight"): 
            paths.append(path) # Adds the path
            if len(paths) == k: # Stops at k
                break
        return paths
    
    def flow(self, src: str, dst: str, priority: int = 10) -> None:
        paths = self.kShortestPaths(src, dst, 2) # Finds shortest paths
        if not paths: # No path
            return 
        
        path = paths[0] # Best path
        backup = paths[1] if len(paths) > 1 else None # Second path

        pick = self.RR[(src, dst)] # Round robin
        chosen = path if pick % 2 == 0 or backup is None else backup # Chooses primary or backup path

        self.pushFlow(chosen, src, dst, priority) # Creates the flow
        if backup: 
            self.backups[(src, dst)] = backup # Records backup path

    def pushFlow(self, path: List[str], src: str, dst: str, priority: int) -> None: # Pushes flow to the switches
        for i in range(len(path) - 1): # Iterates through the nodes
            node = path[i] # Current switch
            nextHop = path[i + 1] # Next switch
            port = f"{node}->{nextHop}" # Name of the port
            entry = Flow(priority, (src, dst), outPort=port) # Creates a flow entry
            self.switches[node].program(entry) # Adds it to the table


    def linkFailure(self, x: str, y: str) -> None: # Simulates a link failure
        self.removeLink(x, y) # Removes the link
        affectedFlows = [(a, b) for (a,b), path in self.backups.items() if x in path or y in path] # Finds the (src, dst) that are affected by the link failure
        for src, dst in affectedFlows: 
            self.pushFlow(self.backups[(src, dst)], src, dst, priority=10) # Reinstalls backups

    def recordUtil(self, path: List[str], bytes: int) -> None:
        for x, y in zip(path, path[1:]): # Each hop in the path
            key = (x, y) if x < y else (y, x) # Consistent key order 
            self.util[key] += bytes # Adds to the counter
