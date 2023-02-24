class AGV:
    def __init__(self, max_speed, battery_life, current_position):
        self.max_speed = max_speed  # maximum speed of the AGV
        self.battery_life = battery_life  # current battery life of the AGV
        self.current_position = current_position  # current position of the AGV
    
    def move(self, new_position):
        # calculate distance between current position and new position
        distance = abs(new_position - self.current_position)
        # calculate time to travel that distance at maximum speed
        time_to_travel = distance / self.max_speed
        # update current position
        self.current_position = new_position
        # decrease battery life by the amount of time it took to travel
        self.battery_life -= time_to_travel
        
        if self.battery_life <= 0:
            print("AGV out of battery!")
