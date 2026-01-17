from pymavlink import mavutil
import time
import threading
from threading import Thread

master = mavutil.mavlink_connection('COM6', baud=57600)
master.wait_heartbeat()

def update_rc_sticks():
    while True:
        try:
            msg = master.recv_match(type='RC_CHANNELS_RAW', blocking=True)
            print(msg)
        except Exception as e:
            print(f'HATA!: {e}')

        time.sleep(0.1)

rc_thread=threading.Thread(target=update_rc_sticks, daemon=True)
rc_thread.start()
