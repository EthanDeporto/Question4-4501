from typing import List, Dict, Tuple
from dataclasses import dataclass, field

@dataclass
class Flow:
    index: int = field(init=False, repr=False)
    prio: int # Priority
    match: Tuple[str, str] # (src, dst)
    outPort: str # Port string


@dataclass
class Switch:
    switchID: str # Identifier
    ports: Dict[str, str] = field(default_factory=dict) # Port ID to destination mapping
    table: List[Flow] = field(default_factory=list) # Orders the flow entries 

    def addPort(self, portID: str, dst: str) -> None: # Function to add a port to another switch
        self.ports[portID] = dst

    def program(self, flow: Flow) -> None: # Creates a new flow entry and keeps the table sorted
        self.table.append(flow)
        self.table.sort() # Sorts table
