# Importing necessary libraries
import networkx as nx
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import geopandas as gpd
import rasterio as rs
import matplotlib.pyplot as plt
import random

# Import the agent class(es) from agents.py
from agents import Government

# Import functions from functions.py
from functions import get_flood_map_data, calculate_basic_flood_damage
from functions import map_domain_gdf, floodplain_gdf

class CollectiveAdaptationModel(Model):
    """
    The main model running the simulation. It sets up the network of government agents,
    simulates their behavior, and collects data. The network type can be adjusted based on study requirements.
    """

    def __init__(self, 
                 seed = None,
                 number_of_government = 0, # number of government agents
                 # Simplified argument for choosing flood map. Can currently be "harvey", "100yr", or "500yr".
                 flood_map_choice='harvey',
                 # ### network related parameters ###
                 # The social network structure that is used.
                 # Can currently be "erdos_renyi", "barabasi_albert", "watts_strogatz", or "no_network"
                 network = 'watts_strogatz',
                 # likeliness of edge being created between two nodes
                 probability_of_network_connection = 0.4,
                 # number of edges for BA network
                 number_of_edges = 3,
                 # number of nearest neighbours for WS social network
                 number_of_nearest_neighbours = 5,
                 #local APE
                 APE=random.uniform(0.0005, 0.001),
                 #local Affected population
                 affected_population= 94623,
                 #local Affected population
                 exposure_rate=0.1,
                 #FN_standard= C/(death_population^alpha) we make assupmtions on C and alpha
                 c=0.031383,
                 a=1.5,

                 ):
        
        super().__init__(seed = seed)
        
        # defining the variables and setting the values
        self.number_of_government = number_of_government  # Total number of household agents
        self.seed = seed
        self.APE=APE
        self.affected_population= affected_population
        #local Affected population
        self.exposure_rate=exposure_rate
        self.c=c
        self.a=a
        # network
        self.network = network # Type of network to be created
        self.probability_of_network_connection = probability_of_network_connection
        self.number_of_edges = number_of_edges
        self.number_of_nearest_neighbours = number_of_nearest_neighbours

        # generating the graph according to the network used and the network parameters specified
        self.G = self.initialize_network()
        # create grid out of network graph
        self.grid = NetworkGrid(self.G)

        # Initialize maps
        self.initialize_maps(flood_map_choice)

        # set schedule for agents
        self.schedule = RandomActivation(self)  # Schedule for activating agents

        # create households through initiating a household on each node of the network graph
        for i, node in enumerate(self.G.nodes()):
            government = Government(unique_id=i, model=self)
            self.schedule.add(government)
            self.grid.place_agent(agent=government, node_id=node)

            
            
            
            
       # Data collection setup to collect data
        model_metrics = {
                        "total_collective_adaptations": self.total_adapted_governments,
                        "weak_collective_adaptations": self.total_weak_adapted_governments,
                        "strong_collective_adaptations":self.total_strong_adapted_governments
                        # ... other reporters ...
                        }
        
        agent_metrics = {
                        #"FloodDepthEstimated": "flood_depth_estimated",
                        #"FloodDepthActual": "flood_depth_actual",
                        #"FloodDamageActual" : "flood_damage_actual",
                        "Weakadaptation": "weak_collective_adaption",
                        "Strongadaptation": "strong_collective_adaption",
                        "location":"location",
                        # ... other reporters ...
                        }
        #set up the data collector 
        self.datacollector = DataCollector(model_reporters=model_metrics, agent_reporters=agent_metrics)
            
    def initialize_network(self):
        """
        Initialize and return the social network graph based on the provided network type using pattern matching.
        """
        if self.network == 'erdos_renyi':
            return nx.erdos_renyi_graph(n=self.number_of_government,
                                        p=self.number_of_nearest_neighbours / self.number_of_government,
                                        seed=self.seed)
        elif self.network == 'barabasi_albert':
            return nx.barabasi_albert_graph(n=self.number_of_government,
                                            m=self.number_of_edges,
                                            seed=self.seed)
        elif self.network == 'watts_strogatz':
            return nx.watts_strogatz_graph(n=self.number_of_government,
                                        k=self.number_of_nearest_neighbours,
                                        p=self.probability_of_network_connection,
                                        seed=self.seed)
        elif self.network == 'no_network':
            G = nx.Graph()
            G.add_nodes_from(range(self.number_of_government))
            return G
        else:
            raise ValueError(f"Unknown network type: '{self.network}'. "
                            f"Currently implemented network types are: "
                            f"'erdos_renyi', 'barabasi_albert', 'watts_strogatz', and 'no_network'")
        
    def initialize_maps(self, flood_map_choice):
        """
        Initialize and set up the flood map related data based on the provided flood map choice.
        """
        # Define paths to flood maps
        flood_map_paths = {
            'harvey': r'../input_data/floodmaps/Harvey_depth_meters.tif',
            '100yr': r'../input_data/floodmaps/100yr_storm_depth_meters.tif',
            '500yr': r'../input_data/floodmaps/500yr_storm_depth_meters.tif'  # Example path for 500yr flood map
        }

        # Throw a ValueError if the flood map choice is not in the dictionary
        if flood_map_choice not in flood_map_paths.keys():
            raise ValueError(f"Unknown flood map choice: '{flood_map_choice}'. "
                             f"Currently implemented choices are: {list(flood_map_paths.keys())}")

        # Choose the appropriate flood map based on the input choice
        flood_map_path = flood_map_paths[flood_map_choice]

        # Loading and setting up the flood map
        self.flood_map = rs.open(flood_map_path)
        self.band_flood_img, self.bound_left, self.bound_right, self.bound_top, self.bound_bottom = get_flood_map_data(
            self.flood_map)
    
    def total_weak_adapted_governments(self):
        """Return the total number of government agent that have decided on the weak collective adaptions."""
        weak_adapted_countg = sum([1 for agent in self.schedule.agents if isinstance(agent, Government) and agent.weak_collective_adaption])
        return weak_adapted_countg
    
    def total_strong_adapted_governments(self):
        """Return the total number of government agent that have decided on the strong collective adaptions."""
        strong_adapted_countg = sum([1 for agent in self.schedule.agents if isinstance(agent, Government) and agent.strong_collective_adaption])
        return strong_adapted_countg
    
    def total_adapted_governments(self):
        """Return the total number of government agent that have decided on the collective adaptions."""
        adapted_countg = sum([1 for agent in self.schedule.agents if isinstance(agent, Government) and agent.strong_collective_adaption or agent.weak_collective_adaption])
        return adapted_countg
    
    def plot_model_domain_with_agents(self):
        fig, ax = plt.subplots()
        # Plot the model domain
        map_domain_gdf.plot(ax=ax, color='lightgrey')
        # Plot the floodplain
        floodplain_gdf.plot(ax=ax, color='lightblue', edgecolor='k', alpha=0.5)

        # Collect agent locations and statuses
        for agent in self.schedule.agents:
            color = 'blue' if agent.weak_collective_adaption and agent.strong_collective_adaption ==False else 'purple' if agent.strong_collective_adaption else 'red'
                
            ax.scatter(agent.location.x, agent.location.y, color=color, s=10, label=color.capitalize() if not ax.collections else "")
            ax.annotate(str(agent.unique_id), (agent.location.x, agent.location.y), textcoords="offset points", xytext=(0,1), ha='center', fontsize=9)
        # Create legend with unique entries
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), title="Red: no collective adaptions,\n Blue: take weak collective adaptions,\n Purple: take strong collective adaptions")

        # Customize plot with titles and labels
        plt.title(f'Model Domain with Government Agents at Step {self.schedule.steps}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()

    def step(self):
        """
        introducing a shock: 
        at time step 5, there will be a global flooding.
        This will result in actual flood depth. Here, we assume it is a random number
        between 0.5 and 1.2 of the estimated flood depth. In your model, you can replace this
        with a more sound procedure (e.g., you can devide the floop map into zones and 
        assume local flooding instead of global flooding). The actual flood depth can be 
        estimated differently
        """
        
        
        if self.schedule.steps == 0:
            for agent in self.schedule.agents:
                agent.APE_in_own_node= self.APE
                agent.affected_population_in_own_node= self.affected_population
                agent.exposure_rate_in_own_node=self.exposure_rate
                agent.c=self.c
                agent.a=self.a
        
        if self.schedule.steps == 5:
            for agent in self.schedule.agents:
                # Calculate the actual flood depth as a random number between 0.5 and 1.2 times the estimated flood depth
                agent.flood_depth_actual = random.uniform(0.5, 1.2) * agent.flood_depth_own
                # calculate the actual flood damage given the actual flood depth
                agent.flood_damage_actual = calculate_basic_flood_damage(agent.flood_depth_actual)
        
        # Collect data and advance the model by one step
        self.datacollector.collect(self)
        self.schedule.step()
