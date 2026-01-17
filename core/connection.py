from dronekit import connect, VehicleMode


def connect_vehicle(addr, baud, wait_ready, timeout, heartbeat_timeout):
    vehicle = connect(addr, baud, wait_ready, timeout, heartbeat_timeout)
    return vehicle