import carla
import random
import time

def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

def main():
    actor_list = []
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        
        world = client.get_world()
        
        blueprint_library = world.get_blueprint_library()
        
        start_time = time.time()
        
        car_model = blueprint_library.filter('model3')[0]
        
        spawn_point = random.choice(world.get_map().get_spawn_points())
        
        vehicle = world.spawn_actor(car_model, spawn_point)
        actor_list.append(vehicle)
        
        collision_sensor = world.spawn_actor(blueprint_library.find('sensor.other.collision'), carla.Transform(), attach_to=vehicle)
        actor_list.append(collision_sensor)
        
        def _on_collision(event):
            print("Collision detected")
            current_time = time.time()
            collision_time = current_time - start_time
            print(f"Collision happened after {collision_time:.2f} seconds")

            actor_type = get_actor_display_name(event.other_actor)
            print(f"Collided with {actor_type}")
            
            intensity = event.normal_impulse
            collision_intensity = (intensity.x**2 + intensity.y**2 + intensity.z**2)**0.5
            print(f"Collision intensity: {collision_intensity:.2f}")
            
            vehicle.apply_control(carla.VehicleControl(hand_brake=True))
            time.sleep(5)
            vehicle.apply_control(carla.VehicleControl(hand_brake=False))
        
        collision_sensor.listen(lambda event: _on_collision(event))
        
        while True:
            world.tick()

    finally:
        print('Destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('Done.')

if __name__ == '__main__':
    main()
