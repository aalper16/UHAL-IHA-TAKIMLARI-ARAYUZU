from dronekit import connect, VehicleMode
import tkinter as tk
from tkinter import ttk
import time
import math
import threading
from pymavlink import mavutil

#! ARAÇ BAĞLANTISI
vehicle = connect('COM6', baud=57600, wait_ready=True, timeout=120, heartbeat_timeout=120)



#! PENCERE BAŞLATMA
root = tk.Tk()
root.configure(bg="#202020")
root.overrideredirect(True) 
root.geometry("800x600")
root.attributes('-topmost', True)


#! MODLAR
modes = ['AUTO', 'MANUAL', 'STABILIZE', 'LOITER', 'CIRCLE', 'FBWA', 'RTL', 'GUIDED']

def move_window(event):
    root.geometry(f'+{event.x_root}+{event.y_root}')


#! VERİ GÜNCELLEME
def update_altitude():
    global altitude
    while True:
        try:
            altitude = vehicle.location.global_relative_frame.alt
            print(altitude)
            altitude_title.config(text=f"ALT: {altitude:.3f}")
        except Exception as e:
            print(f'HATA!:',e)

        time.sleep(0.5)  # 0.5 saniyede bir güncelle

def update_arm():
    global armstat
    while True:
        try:
            armstatbool = vehicle.is_armable
            if armstatbool:
                armstat = "READY TO ARM"
                arm_title.config(text=armstat, fg='green')
            else:
                armstat = "NOT READY TO ARM"
                arm_title.config(text=armstat, fg='red')

            # BURASI YENİ: Arming durumu göster
            if vehicle.armed:
                armed_status_label.config(text="ARMED", fg="red")
                arm_button.config(text='DISARM VEHICLE')
            else:
                armed_status_label.config(text="DISARMED", fg="red")
                arm_button.config(text='ARM VEHICLE')

        except Exception as e:
            print(f'HATA!:', e)

        time.sleep(0.5)

def update_mode():
    global mode
    while True:
        try:
            mode = vehicle.mode
            mode_title.config(text=f'{mode}')
        except Exception as e:
            print(f'HATA!:',e)

        time.sleep(0.5)

def update_gps_stat():
    global gpsstat ,gpsfix,gpssatellite
    while True:
        try:
            gpsstat = vehicle.gps_0
            gpsfix = gpsstat.fix_type
            gpssatellite = gpsstat.satellites_visible
            if gpsfix == 1:
                gps_fix_title.config(text=f'No GPS Fix', fg='red')
            elif gpsfix == 2:
                gps_fix_title.config(text=f'GPS Fix: {gpsfix} | 2D Fix', fg='orange')
            elif gpsfix == 3:
                gps_fix_title.config(text=f'GPS Fix: {gpsfix} | 3D Fix', fg='green')
            elif gpsfix == 4:
                gps_fix_title.config(text=f'GPS Fix: {gpsfix} | 4D Fix', fg='green')
            else:
                gps_fix_title.config(text=f'No Data', fg='red')

            if gpssatellite >= 0 and gpssatellite <= 5:
                gps_satellite_title.config(text=f'Connected Satellites: {gpssatellite}', fg='red')
            elif gpssatellite >= 6 and gpssatellite <= 10:
                gps_satellite_title.config(text=f'Connected Satellites: {gpssatellite}', fg='orange')
            elif gpssatellite >= 11 and gpssatellite <= 20:
                gps_satellite_title.config(text=f'Connected Satellites: {gpssatellite}', fg='green')
            elif gpssatellite >= 21 and gpssatellite <=30:
                gps_satellite_title.config(text=f'Connected Satellites: {gpssatellite}', fg='green')
            else:
                gps_satellite_title.config(text=f'No Satellite Data Received!', fg='red')

        except Exception as e:
            print(f'HATA!:',e)

        time.sleep(0.5)

def update_groundspeed():
    global groundspeed_data 
    while True:
        try:
            groundspeed_data = vehicle.groundspeed
            groundspeed_title.config(text=f"{groundspeed_data}kts")
        except Exception as e:
            print(f'HATA!:',e)

        time.sleep(0.5)

def update_attitude():
    global attitude, roll, pitch, yaw
    while True:
        try:
            attitude = vehicle.attitude
            roll = math.degrees(attitude.roll)
            pitch = math.degrees(attitude.pitch)
            yaw = math.degrees(attitude.yaw)

            # HUD güncelle
            hud_base.after(0, draw_artificial_horizon, pitch, roll)
            hud_base.after(0, draw_yaw_indicator, yaw)
            hud_base.after(0, draw_altitude_speed_bar, altitude, groundspeed_data)


        except Exception as e:
            print('HATA!:', e)
        
        time.sleep(0.1)



def update_battery():
    global battery_data
    while True:
        try:
            battery_data = vehicle.battery
            percent = (battery_data.voltage - 22.2) / (25.2 - 22.2) * 100
            if percent <=100 and percent >=51:
                battery_title.config(text=f'{battery_data.voltage}v - {percent:.1f}%', fg='green')
            elif percent <= 50 and percent >= 21:
                battery_title.config(text=f'{battery_data.voltage}v - {percent:.1f}%', fg='orange')
            elif percent <= 20 and percent >= 0:
                battery_title.config(text=f'{battery_data.voltage}v - {percent:.1f}% |LOW|', fg='red')
            else:
                battery_title.config(text=f"COULDN'T FETCH BATTERY DATA", fg='red')
        except Exception as e:
            print('HATA!:',e)

        time.sleep(0.5)



def level_horizon():
    print("Sending LEVEL command (set current orientation as level)...")

    # MAV_CMD_PREFLIGHT_CALIBRATION
    # param1: gyro cal
    # param2: mag cal
    # param3: baro cal
    # param4: RC cal
    # param5: accel cal
    # param6: ESC cal
    # param7: board level cal <-- bunu 1 yapıyoruz

    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, # command
        0,     # confirmation
        0, 0, 0, 0, 0, 0, 1  # param1 - param7 (sadece param7 = 1)
    )

    vehicle.send_mavlink(msg)
    vehicle.flush()
    print("Level command sent.")
    level_calibrated.config(text="Calibrated LEVEL")


def draw_artificial_horizon(pitch_deg, roll_deg):
    hud_base.delete("horizon")  # Eski çizimi sil

    # Merkez
    cx, cy = 240, 150
    width, height = 480, 300

    # Pitch'i piksellere çevir (10 derece = 25px gibi)
    pitch_scale = 2.5  # ayarlanabilir
    pitch_offset = pitch_deg * pitch_scale

    # Roll'u radyan cinsine çevir
    roll_rad = math.radians(roll_deg)

    # Gökyüzü ve zemin renkleri
    sky_color = "#4da6ff"
    ground_color = "#996633"

    # Ufuk çizgisinin merkezdeki yatay çizgiden kayması
    points = [
        (-width, pitch_offset),
        (width, pitch_offset),
        (width, height),
        (-width, height)
    ]

    # Noktaları döndür ve taşı
    rotated_ground = []
    for x, y in points:
        x_rot = x * math.cos(roll_rad) - y * math.sin(roll_rad)
        y_rot = x * math.sin(roll_rad) + y * math.cos(roll_rad)
        rotated_ground.append((x_rot + cx, y_rot + cy))

    # Gökyüzü (arkaplan)
    hud_base.create_rectangle(0, 0, width, height, fill=sky_color, tags="horizon")

    # Zemin (dönen polygon)
    hud_base.create_polygon(rotated_ground, fill=ground_color, tags="horizon")

    # Ufuk çizgisi
    x1 = cx - 100 * math.cos(roll_rad)
    y1 = cy - 100 * math.sin(roll_rad)
    x2 = cx + 100 * math.cos(roll_rad)
    y2 = cy + 100 * math.sin(roll_rad)
    hud_base.create_line(x1, y1, x2, y2, fill="white", width=2, tags="horizon")

    # Orta daire
    hud_base.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="white", tags="horizon")

def draw_yaw_indicator(yaw_deg):
    hud_base.delete("yaw")

    cx, cy = 240, 280
    width = 240

    for angle in range(-90, 91, 30):  # -90° ila +90° arası
        val = (yaw_deg + angle) % 360
        x = cx + angle * 2  # 1° = 2px
        hud_base.create_line(x, cy, x, cy + 10, fill='white', tags="yaw")
        hud_base.create_text(x, cy + 20, text=f"{int(val)}", fill='white', font="Helvetica 8", tags="yaw")

    # Merkez oku
    hud_base.create_polygon(cx-5, cy-5, cx+5, cy-5, cx, cy-15, fill='red', tags="yaw")


def draw_altitude_speed_bar(altitude, speed):
    hud_base.delete("sidebars")

    # Altitude
    hud_base.create_rectangle(10, 50, 60, 250, fill="#1a1a1a", tags="sidebars")
    hud_base.create_text(35, 60, text="ALT", fill='white', tags="sidebars")
    hud_base.create_text(35, 150, text=f"{altitude:.1f}", fill='green', font="Helvetica 12", tags="sidebars")

    # Speed
    hud_base.create_rectangle(420, 50, 470, 250, fill="#1a1a1a", tags="sidebars")
    hud_base.create_text(445, 60, text="SPD", fill='white', tags="sidebars")
    hud_base.create_text(445, 150, text=f"{speed:.1f}", fill='green', font="Helvetica 12", tags="sidebars")

def update_rc_channels():
    while True:
        try:
            rc_roll = vehicle.channels['1']  # genelde Aileron
            rc_pitch = vehicle.channels['2']  # genelde Elevator
            rc_throttle = vehicle.channels['3']  # genelde Throttle
            rc_yaw = vehicle.channels['4']  # genelde Rudder

            print(vehicle.channels)

            rc_roll_label.config(text=f"Roll (CH1): {rc_roll}")
            rc_pitch_label.config(text=f"Pitch (CH2): {rc_pitch}")
            rc_throttle_label.config(text=f"Throttle (CH3): {rc_throttle}")
            rc_yaw_label.config(text=f"Yaw (CH4): {rc_yaw}")
        except Exception as e:
            print('HATA (RC CHANNELS):', e)
        time.sleep(0.5)


#! THREAD BAŞLATMA
arm_thread = threading.Thread(target=update_arm, daemon=True)
arm_thread.start()

altitude_thread = threading.Thread(target=update_altitude, daemon=True)
altitude_thread.start()

mode_thread = threading.Thread(target=update_mode, daemon=True)
mode_thread.start()

gps_stat_thread = threading.Thread(target=update_gps_stat, daemon=True)
gps_stat_thread.start()

groundspeed_thread = threading.Thread(target=update_groundspeed, daemon=True)
groundspeed_thread.start()

attitude_thread = threading.Thread(target=update_attitude, daemon=True)
attitude_thread.start()

battery_thread = threading.Thread(target=update_battery, daemon=True)
battery_thread.start()

rc_thread = threading.Thread(target=update_rc_channels, daemon=True)
rc_thread.start()


#! MOD DEĞİŞTİRME
def change_mode(mode):
    vehicle.mode = VehicleMode(str(mode))

#! ARAYÜZ
title_bar = tk.Frame(root, bg='black', relief='raised', bd=0, height=30)
title_bar.pack(fill=tk.X)

title_label = tk.Label(title_bar, text='UHAL IHA ARAYÜZ', bg='black', fg='white')
title_label.pack(side=tk.LEFT, padx=10)

close_button = tk.Button(title_bar, text='X', bg='black', fg='white', command=root.destroy, bd=0)
close_button.pack(side=tk.RIGHT, padx=10)

#! PENCERE SÜRÜKLEME
title_bar.bind('<B1-Motion>', move_window)

content = tk.Frame(root, bg='#2e2e2e')
content.pack(expand=True, fill=tk.BOTH)

#! PARAMETRELER
altitude_title = tk.Label(text=f"ALT: {altitude}", bg="#2e2e2e", fg='white', font="Helvetica 16")
altitude_title.place(x=500,y=30)

arm_title = tk.Label(text=f"{armstat}", bg="#2e2e2e", font="Helvetica 16")
arm_title.place(x=500, y=60)

mode_title = tk.Label(text=mode, bg="#2e2e2e", font="Helvetica 16", fg='white')
mode_title.place(x=500, y=90)
    
gps_fix_title = tk.Label(text=gpsfix, bg="#2e2e2e", font="Helvetica 16")
gps_fix_title.place(x=500, y=120)

gps_satellite_title = tk.Label(text=gpssatellite, bg="#2e2e2e", font="Helvetica 16")
gps_satellite_title.place(x=500, y=150)

groundspeed_title = tk.Label(text=groundspeed_data, bg="#2e2e2e", font="Helvetica 16", fg='white')
groundspeed_title.place(x=500, y=180)

battery_title = tk.Label(text=battery_data, bg="#2e2e2e", font="Helvetica 16", fg='white')
battery_title.place(x=500, y=210)

prearm_label = tk.Label(text="", bg="#2e2e2e", fg='red', font="Helvetica 12")
prearm_label.place(x=500, y=240)

rc_roll_label = tk.Label(root, text="Roll (CH1):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_roll_label.place(x=500, y=270)

rc_pitch_label = tk.Label(root, text="Pitch (CH2):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_pitch_label.place(x=500, y=300)

rc_throttle_label = tk.Label(root, text="Throttle (CH3):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_throttle_label.place(x=500, y=330)

rc_yaw_label = tk.Label(root, text="Yaw (CH4):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_yaw_label.place(x=500, y=360)



#! HUD
hud_base = tk.Canvas(root, width=480, height=300, bg="white")
hud_base.place(x=0, y=30)

#! HUD CROSSHAIR
def draw_hud_crosshair(roll_angle_deg):
    # Eski çarpıyı temizle
    hud_base.delete("crosshair")

    # Merkez
    cx, cy = 240, 150

    # Uç noktalar (statik pozisyonda)
    points = [
        (240, 150),  # merkez
        (200, 180),  # sol uç
        (280, 180),  # sağ uç
    ]

    # Roll'u radyana çevir
    theta = math.radians(roll_angle_deg)

    # Rotasyon fonksiyonu
    def rotate(x, y):
        x -= cx
        y -= cy
        x_rot = x * math.cos(theta) - y * math.sin(theta)
        y_rot = x * math.sin(theta) + y * math.cos(theta)
        return (x_rot + cx, y_rot + cy)

    # Noktaları döndür
    p0 = rotate(*points[0])
    p1 = rotate(*points[1])
    p2 = rotate(*points[2])

    # Çizgileri yeniden çiz
    hud_base.create_line(p0, p1, fill="red", width=3, tags="crosshair")
    hud_base.create_line(p0, p2, fill="red", width=3, tags="crosshair")
    hud_base.create_oval(cx-10, cy-10, cx+10, cy+10, width=2, outline="red", tags="crosshair")

armed_status_label = tk.Label(root, text="ARMED?", fg="red", font="Helvetica 14")
armed_status_label.place(x=180, y=100)
#! HUD ALT
hud_base.create_text(30, 30, text="ALT", fill="red", font="Helvetica 16")
#! HUD SPEED
hud_base.create_text(430, 30, text="SPEED", fill="red", font="Helvetica 16")
#TODO: DEVAM ET

#! KONTROL KISMI
# MOD DEĞİŞTİRME
modes_title = tk.Label(text='Select Mode', bg='#2e2e2e', fg='white')
modes_title.place(x=10, y=360)
modes_dropbox = ttk.Combobox(root, values=modes, font='Helvetica 12')
modes_dropbox.set(str(vehicle.mode.name))
modes_dropbox.place(x=10, y=380)


#! MOD DEĞİŞİM UYGULAMA
def apply_mode():
    selected_mode = modes_dropbox.get()    
    change_mode(selected_mode)
mode_change_button = tk.Button(text='Change Mode', fg='white', bg="#494949", bd=5, relief='ridge', command=apply_mode)
mode_change_button.place(x=220, y=380)

#! ARM KISMI
def arm_vehicle():
    if vehicle.armed == False:
        vehicle.armed = True
    elif vehicle.armed == True:
        vehicle.armed = False
        

arm_button = tk.Button(text='ARM VEHICLE', fg='white', bg='red', bd=5, relief='ridge', command=arm_vehicle)
arm_button.place(x=10, y=430)

#! KALİBRASYONLAR
calibrate_level_button = tk.Button(text='Calibrate LEVEL', fg='white', bg='green', bd=5, command=level_horizon)
level_calibrated = tk.Label(text="", fg='white', bg='#2e2e2e')
level_calibrated.place(x=10, y=520)
calibrate_level_button.place(x=10, y=480)

root.mainloop()
