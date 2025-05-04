# SHA-256 WATERMARK:
# 59a5699b1bfd2b6dcda48d4d68cbe7a16614878f421b4decac4b4873b213dd97

import hashlib, sys
import cmd
import Visualization
import shlex
import logging 
import os

from collections import deque
from itertools import islice
from logging.handlers import RotatingFileHandler
from typing import Any
from Controller import SDN

LOG_FILE = "SDNCLI.log" # Logging file

handler = RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount = 1) # Sets the log file size to 100000 bytes and creates 1 backup

logging.basicConfig(filename=LOG_FILE, filemode="w", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",) # Creates the format for the log file, and add timestamps

log = logging.getLogger(__name__) # Creates the logging file


class CLI(cmd.Cmd):
    intro = "SDN demo shell. Type 'help' for list of commands. Type 'help <command>' for command specific information. \n" # SDN intro message
    prompt = "(SDN demo)"
    
    def parseline(self, line: str) -> tuple[str, str, str]: # Allows the user to input commands in any case
        """Ignores the cases of commands making UI more user friendly."""
        stripped = line.lstrip() # Strips the leading whitespace
        if not stripped:
            return None, None, line # If line is empty, return

        first, *rest = stripped.split(maxsplit=1) # Seperates the first word from the rest of the line
        cmd = first.lower() # Converts the first word to lowercase
        arg = rest[0] if rest else '' # Makes the rest of the line a single string
        return cmd, arg, line 


    def __init__(self, sdn: SDN) -> None:
        super().__init__() # Intializes cmd and CLI
        self.sdn = sdn
    
    def do_addswitch(self, arg: str) -> None: # Function to add a switch
        """Adds a switch to the network."""
        check = arg.strip()
        if len(check) != 1:
            print("Invalid argument. AddSwitch <switchID>.")
            return
        
        self.sdn.addSwitch(arg.strip()) # Adds the switch to the network

    def do_addlink(self, arg: str) -> None: # Function to add a link
        """Adds a link between two switches."""
        try:
            x, y, weight = shlex.split(arg) # Splits the arguments x, y and weight
            cost = int(weight[0]) if weight else 1 # Only takes the first digit
            self.sdn.addLink(x, y, cost) # Creates the edge between two switches
        except ValueError:
            print("Invalid arguments. AddLink <src> <dst> <weight>.")
            

    def do_linkfailure(self, arg: str) -> None: # Function to simulate a link failure 
        """Simulates a link failure."""
        try:
            x, y = shlex.split(arg) # Splits arguments x and y
            self.sdn.linkFailure(x, y) # Simulates the link failure
        except ValueError:
            print("Invalid arguments. LinkFailure <src> <dst>.")

    def do_flow(self, arg: str) -> None: # Simulates a flow to the network
        """Adds a flow to the network."""
        try:
            src, dst, weight = shlex.split(arg) # Splits the arguments src, dst and weight
            priority = int(weight[0]) if weight else 10 # Only takes the first digit
            self.sdn.flow(src, dst, int(priority)) # Adds the flow to simulation
        except ValueError:
            print("Invalid arguments.Flow <src> <dst> <priority>.")

    def do_show(self, arg): # Function to show the current switches, links and flows
        """Shows the current switches, links, and flows."""
        print("Switches: ", list(self.sdn.switches.keys())) # Lists the current switches
        print("Links: ")
        for x, y, z in self.sdn.graph.edges(data="weight"): # Lists the current links
            print(f"{x} <-> {y} (weight: {z})")
        print("Flows for each switch: ") # Lists the current flows for each switch
        for swID, switch in self.sdn.switches.items(): # Iterates through each switch
            print(f"{swID}:")
            for entry in switch.table: # Iterates through each entry in switch table
                print(f"Match: {entry.match}, OutPort: {entry.outPort}, Priority: {entry.prio}")

    def precmd(self, line:str) -> str: # Function that logs commands the user inputs
        log.info("Input: %s", line)
        return line

    def do_log(self, arg: str) -> None: # Function that prints the commands the user has input
        """Shows a log of the users commands."""
        x=25 # 25 lines of the log
        if arg.strip():
            try:
                x = int(arg.strip()) # Input from user for number of lines in log
            except ValueError:
                print("Invalid argument. Log <number of lines>.")
                return
        
        if not os.path.exists(LOG_FILE): # Users tries to access log before commands
            print("Log file does not exist.")
            return
        
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as y:
                tail = deque(y, maxlen=x) # creates a deque of the last x lines of log file
            if not tail:
                print("(Log file exists but is empty.)") # Empty Log
            else:
                print("".join(tail), end="")  
        except OSError as e: # Error with log
            print(f"Error reading log: {e}")
    
    def do_visualize(self, arg: str) -> None: # Function that creates the graph
        """Draws the current topology window in a graph."""
        Visualization.renderGraph(self.sdn.graph, self.sdn.util) # Graphs the current topology

    def do_exit(self, arg: str) -> bool: # Function to exit out of CLI
        """Exits the CLI."""
        print("Exiting...")
        return True 
    
    CLIQuit= do_exit # Alias for exit

    
    def default(self, line: str) -> None: # Default function for unrecognized commands
        pass

if __name__ == "__main__":
    ID = "899538923"
    Watermark = "NeoDDaBRgX5a9"

    print("SHA-256 Watermark:")
    print(hashlib.sha256((ID + Watermark).encode()).hexdigest()) # Prints the SHA-256 watermark
    print("\n")
    
    controller = SDN()
    CLI(controller).cmdloop() # Runs the CLI loop