import networkx as nx
import matplotlib.pyplot as plt

from typing import Dict, List, Tuple

Edge = Tuple[str, str]

def edgeSize(graph: nx.Graph, packets: Dict[Edge, int]) -> list[float]: # Function to calculate edge size
    return [1 + packets.get(tuple((x, y)), 0) / 1_000 for x, y in graph.edges] # Returns the size of the edges in the graph


def renderGraph(graph: nx.Graph, packets: Dict[Edge, int]) -> None: # Function to render the graph
    cords = nx.spring_layout(graph) # (x,y) 
    width = edgeSize(graph, packets) # Edge line width
    nx.draw_networkx(graph, pos=cords, width=width, with_labels=True) # Actually draws the graph with the set arguments
    plt.tight_layout() # Puts the plot in a window
    plt.show() # Displays the graph