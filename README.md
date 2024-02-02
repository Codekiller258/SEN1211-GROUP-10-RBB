## RBB - social risks and collective adaptations

### Introduction
This directory contains a RBB, which can be used to simulate what kind of collective adaptations (policies) will be used and decided by the government. This directory serves for the agent-based model of flood adaptation. The corresponding theory used in this model is FN method. Due to the fact that we want to make this model reuseable and separate from the big assignment, it contains many difference with this part in the big assignment. The model is overall simplified here for the RBB purpose, and the data used here is not necessary the same with the big assignment, but it can be later easily used in the big assignment.



### Installation
To set up the project environment, follow these steps:
1. Make sure you have installed a recent Python version, like 3.11 or 3.12.
2. Install the latest Mesa version (2.1.5 or above) with `pip install -U mesa`
2. Clone the repository to your local machine.
3. Install required dependencies:
   ```bash
   pip install -U geopandas shapely rasterio networkx
   ```

### File descriptions
The `model` directory contains the actual Python code for the RBB model. It has the following files:
- `agents.py`: Defines the `Government` agent class, each representing a local government agent in the model. These agents have attributes related to flood depth, Annual  probability of exceedance, exposure rate and number of people, and their policy decision (collective adaptation) is influenced by these factors. This script is crucial for modeling the decisions of the Government. Notice that there is no household agent in the RBB, because the RBB is only for simulating the behavior of government agent and collective measures.
- `functions.py`: Contains utility functions for the model, including setting initial values, calculating flood damage, and processing geographical data. These functions are essential for data handling and mathematical calculations within the model.
- `RBBmodel.py`: The central script that sets up and runs the simulation. It integrates the agents, geographical data, and network structures to simulate the complex interactions and collective adaptations of governments to flooding scenarios.
- `demo.ipynb`: A Jupyter notebook titled "RBB: Determine the collective adaption strategies". It demonstrates running a model and analyzing and plotting some results.
There is also a directory `input_data` that contains the geographical data used in the model. You don't have to touch it, but it's used in the code and there if you want to take a look.

### Usage
This is a simple but comprehensive model for the government agent to decide on collective adaptations (policies). It can be later  integrated into large models in the topic of flood adaptations. This model is based on the FN curve method.

### Notice
Some parameters you might want to change when you integrate this model into your model:
APE: Anual probability of exceedance ;
Different strategies: Now it only contains weak and strong. User can add more, or make it more specific.
Affected population: you can change the number of affected population according to your model.
Exposure rate: we assume it is 0.1 now, users can change later.
Parameters in determining the FN standard: This differs in different location, users might change according to the reality.


