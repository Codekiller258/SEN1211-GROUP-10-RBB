# Here is for agent class, Households and Government will be classed here
# First import necessary libraries

import math
import random
from mesa import Agent
from shapely.geometry import Point
from shapely import contains_xy

# Import functions from functions.py
from functions import generate_random_location_within_map_domain, get_flood_depth, calculate_basic_flood_damage, floodplain_multipolygon
#  First define the Households agents


class Government(Agent):
    """
    A government agent in this RBB model will in charge of doing weak and strong adaptions, the weak adaption is information management,
    and the strong adaption is providing subsidies for the householders.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #For the RBB, the government have two attribute, provide information and doing subsidies, both initial state is false
        self.weak_collective_adaption = False 
        self.strong_collective_adaption = False

        
        #  One government agent on different node
        gloc_x, gloc_y = generate_random_location_within_map_domain() # one government agent at each dot, it is now not right.
        self.location = Point(gloc_x, gloc_y)

         # Each node have an attribute related to the inputs APE, affected_population, exposure_rate, death_rate
       
        self.APE_in_own_node= random.uniform(0.0005, 0.001)
        self.affected_population_in_own_node= 94623
        self.exposure_rate_in_own_node=0.1
        self.c=0.031383
        self.a=1.5
        self.flood_depth_own = get_flood_depth(corresponding_map=model.flood_map, location=self.location, band=model.band_flood_img)
        if self.flood_depth_own < 0:
            self.flood_depth_own = 0
        self.death_rate_in_own_node= 0.655 * 0.001 * math.exp(1.16 * self.flood_depth_own)

        
    def calculate_FNstandard(self):
     """
    This function is to calculate the FN curve.
    
    Parameters
    ----------
    APE: annual probability of exceedance(years), we don't have data, have to make assumptions. For 200 years, we assume it was 1/200, i.e. 0.5%
    affected_population: the number of population affected in the flooded area. This can be counted according to the network?
    exposure_rate: rate of affected_population who are exposured to the flood, we can make assumptions, 10% for instance.
    death_rate: rate of deaths who are exposured to the flood, we can make assumptions, 0.0325% for instance. This can be linked to damage factors.

    Returns
    -------
    FN_standard: return to the FN standard value with the corresponding death population
    """
     self.exposure_population = self.affected_population_in_own_node * self.exposure_rate_in_own_node
     self.death_population = self.death_rate_in_own_node * self.exposure_population
     #FN_standard= C/(death_population^alpha) we make assupmtions on C and alpha
     self.FN_standard_own= self.c/(self.death_population**self.a)
     return self.FN_standard_own
    
    def calculate_FNvalue(self):
     """
    This function is to calculate the FN value.
    Due to lot of uncertainties, we will make it as simple as possible
    Parameters
    ----------
    APE: annual probability of exceedance(years), we don't have data, have to make assumptions. For 200 years, we assume it was 1/200, i.e. 0.5%

    Returns
    -------
    FN_value: return to the FN value with the corresponding APE
    """
    # FN=1-Rn/(k+1) here Rn is the rank of the flood event, k is the event per year, we assume it is the APE
     self.FN_value_own =1-1/(self.APE_in_own_node+1) 
     return self.FN_value_own
    
    #Functions to determine what to use    
    def step(self):
        # Logic for adaptation based on the FN value and FN standard
        # Standard should have two, to determine whether to use strong or weak adaptions
        self.calculate_FNstandard()
        self.calculate_FNvalue()
    
        if self.FN_value_own > 0.6*self.FN_standard_own and random.random() < 0.2:
            self.weak_collective_adaption = True  # government agent decide on collective adaption strategies
        if self.weak_collective_adaption == True and self.FN_value_own > self.FN_standard_own and random.random() < 0.4:
            self.strong_collective_adaption = True
        

 
        
        
        


    