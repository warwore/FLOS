# FLOS
Factory Logistics Optimization Simulator

Requests from manufacturing companies have brought upon a need to optimize factory logistics through tracking of automated guided vehicles (AGVs). The client for this project, A&E Engineering, exists to deliver custom industrial automation solutions to customers worldwide. Their services include factory automation, real-time locating systems (RTLS) and radio-frequency identification (RFID) deployment, manufacturing execution system (MES) deployment, and more. This company has reached out and tasked the team with creating a virtual test environment, which will address the needs of manufacturing companies who are seeking to optimize the AGVs their factory.  

The virtual test environment will contain the layout of the factory and all the components. The components of this simulation include: AGVs, a recharge area, consumption points, a delivery area, and paths. The AGVs will pick up and deliver goods within the factory using simulated demand by following predetermined paths. The AGVs, as well as their paths and consumption points will need to be configurable to test optimal algorithms. These algorithms are tested to improve delivery time between consumption points, reduce traffic between devices in the simulation, and optimize battery usage. 


![Example factory Map](https://user-images.githubusercontent.com/37707094/221194758-9c2c9190-27ff-4d0f-83fe-46114f7d05e5.png)



How to use:

test2.py is the file that needs to be ran. Each AGV requires 1 pick up point, 1 drop off point, and 1 recharge point. One you have placed your points and created your factory layout, press A to spawn in the AGVs and watch them navigate between consumption points. Press U to show the battery indicators for each AGV. Speed up and slow down the simulation by using the + and - keys respectively.



Placeable Objects:

Black squares = Obstacles

Yellow squares = Pickup points

Blue squares = Dropoff points 

Green squares = Recharge points

TO add RFID and Antennas you have to enter # number of them and their coordinates
Antenna 1: 5407,1520,3300
Antenna 2: 1794,2198,3200
Antenna 3: 7873,3500,3000
RFID 1:  5407, 2858
RFID 2: 4311,1203
RFID 3: 835,2858
RFID 4: 7063,1520

Example Map made using the program:
![Screenshot 2023-05-03 142040](https://user-images.githubusercontent.com/37707094/236009336-bc38e62f-604d-48c7-8673-9deff100f5e6.png)

