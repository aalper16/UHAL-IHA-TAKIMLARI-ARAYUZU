from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import tkinter as tk
from tkinter import ttk
import time
import math
import threading
from pymavlink import mavutil
from connection import connect_vehicle
import numpy as np
import pygame
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
from tkinter import messagebox
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')


#! ARAÇ BAĞLANTISI
pygame.mixer.init(frequency=44100, size=-16, channels=1)

def play_tone(frequency=440, duration=0.2, volume=1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Sinüs dalgası üretimi
    waveform = np.sin(2 * np.pi * frequency * t)
    
    # 16-bit PCM’e dönüştür
    waveform = (waveform * 32767).astype(np.int16)
    
    # pygame ses nesnesi oluştur
    sound = pygame.sndarray.make_sound(waveform)
    sound.set_volume(volume)
    sound.play()
    
    # Sesin bitmesini bekle
    pygame.time.wait(int(duration * 1000))

def safe_connect(connection_str, baud=115200, wait_ready=True):
    vehicle = None
    while vehicle is None:
        try:
            print(f"Bağlanmaya çalışılıyor: {connection_str}")
            vehicle = connect(connection_str, baud=baud, wait_ready=wait_ready, timeout=30, heartbeat_timeout=30)
            print("Bağlantı başarılı!")
        except Exception as e:
            print(f"Bağlantı başarısız: {e}. 5 saniye sonra tekrar denenecek...")
            time.sleep(5)
    return vehicle



#vehicle = connect('COM6', baud=57600, wait_ready=True, timeout=120, heartbeat_timeout=120)

vehicle = safe_connect('tcp:127.0.0.1:5762')
counter_home = 0
while vehicle.home_location is None:
    print('Home konumu bekleniyor...', vehicle.home_location)
    time.sleep(1)
    counter_home +=1
    if vehicle.home_location is None and counter_home == 1:
        with open('data/home_lat.txt', "r") as homefile_lat:
            homepoint_lat = homefile_lat.read()
        with open('data/home_lon.txt', "r") as homefile_lon:
            homepoint_lon = homefile_lon.read()
        with open('data/home_alt.txt', "r") as homefile_alt:
            homepoint_alt = homefile_alt.read()
        newhome = LocationGlobal(float(homepoint_lat), float(homepoint_lon), float(homepoint_alt))
        vehicle.home_location = newhome
# Prearm ve genel uyarıları yakalama
def statustext_listener(self, name, message):
    text = message.text
    severity = message.severity

    # "PreArm" içeren uyarılar
    if "PreArm" in text or "prearm" in text:
        print(f"[PREARM UYARISI] {text}")
        prearm_label.after(0, lambda: prearm_label.config(text=text, fg="red"))
    elif "Arm" in text or "arming" in text:
        # Silahlanma ile ilgili diğer mesajlar
        prearm_label.after(0, lambda: prearm_label.config(text=text, fg="orange"))
        prearm_label.after(8000, lambda: prearm_label.config(text=""))

    else:
        # PreArm dışı genel sistem mesajlarını da görmek istersen aktif edebilirsin:
        # print(f"[{severity}] {text}")
        pass

vehicle.add_message_listener('STATUSTEXT', statustext_listener)

vehicletype = vehicle._vehicle_type
if vehicletype == 1:
    plane_img = Image.open('images/plane.png')
elif vehicletype == 2:
    plane_img = Image.open('images/copter.png')
elif vehicletype == 10:
    plane_img = Image.open('images/rover.png')




#! PENCERE BAŞLATMA
root = tk.Tk()
root.configure(bg="#202020")
root.overrideredirect(True) 
root.geometry("800x600")
root.attributes('-topmost', True)
marker_img = ImageTk.PhotoImage(plane_img)



#! MODLAR
modes = ['AUTO', 'MANUAL', 'STABILIZE', 'LOITER', 'CIRCLE', 'FBWA', 'FBWB','RTL', 'GUIDED', 'LAND', 'TAKEOFF', 'AUTOLAND', 'AUTOTUNE']

def move_window(event):
    root.geometry(f'+{event.x_root}+{event.y_root}')

last_bank_alert = 0
last_stall_alert = 0
last_overspeed_alert = 0

#! FONKSİYONLAR
def get_telemetry():
    try:
        attitude = vehicle.attitude
        altitude = vehicle.location.global_relative_frame.alt
        speed = vehicle.groundspeed
        vertical_speed = vehicle.velocity[2]
        return {
            "roll": attitude.roll * 57.3,
            "pitch": attitude.pitch * 57.3,
            "yaw": attitude.yaw * 57.3,
            "altitude": altitude,
            "speed": speed,
            "vario": -vertical_speed,
            "mode": mode
        }
    except Exception as e:
        print(e)
        time.sleep(0.5)
# Ses oynatma fonksiyonu thread ile
def speak(text):
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def check_audio_alerts():
    try:
        global last_bank_alert, last_stall_alert
        while True:
            now = time.time()
            telem = get_telemetry()
            if telem['roll'] > 55 and now - last_bank_alert > 2:
                engine.setProperty('voice', voices[1].id)  # erkek sesi
                engine.setProperty('rate', 160)
                speak("bank angle")
                time.sleep(1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)
                play_tone(400, 0.1)
                play_tone(800, 0.1)
                play_tone(1200, 0.1)

                last_bank_alert = now

            if telem['speed'] <= 13 and telem['mode'] == 'MANUAL' or telem['mode'] == 'GUIDED' or telem['mode'] == 'STABILIZE' and telem['altitude'] >=5 and now - last_stall_alert > 3:
                engine.setProperty('voice', voices[23].id)  # erkek sesi
                engine.setProperty('rate', 160)
                speak("stall")
                time.sleep(1)
                play_tone(300, 3)

                last_stall_alert = now
            
            if telem['speed'] >= 40 and now - last_overspeed_alert > 3:
                engine.setProperty('voice', voices[23].id)  # erkek sesi
                engine.setProperty('rate', 160)
                speak("over speed")
                time.sleep(1)
                play_tone(800, 1)
                play_tone(1600, 1)
                

                last_stall_alert = now
            time.sleep(0.5)
    except Exception as e:
        print(e)
        time.sleep(0.5)

def change_alt(alt):
    try:
        current_location = vehicle.location.global_relative_frame
        vmode = vehicle.mode.name
        if vmode == 'GUIDED':
            target_alt = LocationGlobalRelative(current_location.lat, current_location.lon, alt)
            vehicle.simple_goto(target_alt)
            print(f'Yükseklik {str(alt)} olarak ayarlanıyor...')
        else:
            print('GUIDED mod olmadan yükseklik manuel bir şekilde değiştirilemez!')
    except Exception as e:
        print(e)
        time.sleep(0.5)

def change_airspeed(speed):
    try:
        vehicle.airspeed = int(speed)
    except Exception as e:
        print(e)
        time.sleep(0.5)

def only_int(char):
    # Girilen karakter sayı mı?
    return char.isdigit() or char == ""
vcmd = (root.register(only_int), "%S")

def arm_vehicle():
    try:
        if vehicle.armed == False:
            vehicle.armed = True
            engine.setProperty('voice', voices[23].id)  # erkek sesi
            engine.setProperty('rate', 160)
            speak("vehicle armed")
        elif vehicle.armed == True:
            vehicle.armed = False
            engine.setProperty('voice', voices[23].id)  # erkek sesi
            engine.setProperty('rate', 160)
            speak("vehicle disarmed")
    except Exception as e:
        print(e)
        time.sleep(0.5)
def emergency_rtl():
    try:
        change_mode('RTL')
        engine.setProperty('voice', voices[23].id)  # erkek sesi
        engine.setProperty('rate', 160)
        speak("emergency return to launch")
    except Exception as e:
        print(e)
        time.sleep(0.5)

#! VERİ GÜNCELLEME
def update_homefiles():
    try:
        get_home_lat = vehicle.home_location.lat
        get_home_lon = vehicle.home_location.lon
        get_home_alt = vehicle.home_location.alt

        with open ('data/home_alt.txt', 'w') as updhome_alt:
            updhome_alt.write(str(get_home_alt))
        with open ('data/home_lat.txt', 'w') as updhome_lat:
            updhome_lat.write(str(get_home_lat))
        with open ('data/home_lon.txt', 'w') as updhome_lon:
            updhome_lon.write(str(get_home_lon))
        
        time.sleep(3)
    except Exception as e:
        print(e)
        time.sleep(0.5)
def update_loc():
    try:
        global lat, lon, heading
        while True:
            try:
                loc = vehicle.location.global_frame
                lat = loc.lat
                lon = loc.lon
                alt = loc.alt
                heading = vehicle.heading
                print(f"Konum: Enlem={lat}, Boylam={lon}, İrtifa={alt}")
                time.sleep(1)  # Her saniyede bir güncelle
            except Exception as e:
                print("Konum alınamadı:", e)
                break
    except Exception as e:
        print(e)
        time.sleep(0.5)

def update_altitude_vario():
    try:
        global altitude, previous_alt, vario_value
        previous_alt = vehicle.location.global_relative_frame.alt
        while True:
            try:
                altitude = vehicle.location.global_relative_frame.alt
                vario_value = (altitude - previous_alt) / 0.5  # m/s
                previous_alt = altitude
                altitude_title.config(text=f"ALT: {altitude:.2f} | VARIO: {vario_value:.2f}")
            except Exception as e:
                print(e)
            time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(0.5)


def update_arm():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)

def update_mode():
    try:
        global mode
        while True:
            try:
                mode = vehicle.mode
                mode_title.config(text=f'{mode}')
            except Exception as e:
                print(f'HATA!:',e)

            time.sleep(0.5)
    except Exception as e:
        print(e)
        time.sleep(0.5)

def update_gps_stat():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)

def update_groundspeed():
    try:
        global groundspeed_data 
        while True:
            try:
                groundspeed_data = vehicle.groundspeed  # m/s
                groundspeed_kmh = groundspeed_data * 3.6  # m/s → km/h

                groundspeed_title.config(
                    text=f"{groundspeed_data:.2f} m/s | {groundspeed_kmh:.1f} km/h"
                )
            except Exception as e:
                print(f'HATA!:', e)

            time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(0.5)


def update_attitude():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)


def update_battery():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)


def level_horizon():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)


def draw_artificial_horizon(pitch_deg, roll_deg):
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)

def draw_yaw_indicator(yaw_deg):
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)


def draw_altitude_speed_bar(altitude, speed):
    try:
        hud_base.delete("sidebars")

        # Altitude
        hud_base.create_rectangle(10, 50, 60, 250, fill="#1a1a1a", tags="sidebars")
        hud_base.create_text(35, 60, text="ALT", fill='white', tags="sidebars")
        hud_base.create_text(35, 150, text=f"{altitude:.1f}", fill='green', font="Helvetica 12", tags="sidebars")

        # Speed
        hud_base.create_rectangle(420, 50, 470, 250, fill="#1a1a1a", tags="sidebars")
        hud_base.create_text(445, 60, text="SPD", fill='white', tags="sidebars")
        hud_base.create_text(445, 150, text=f"{speed:.1f}", fill='green', font="Helvetica 12", tags="sidebars")

    except Exception as e:
        print(e)
        time.sleep(0.5)

def update_rc_channels():
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)

def reconnect_loop():
    global vehicle
    while True:
        try:
            if vehicle is None or not vehicle.is_armable:
                print("Bağlantı yok, yeniden bağlanılıyor...")
                vehicle = safe_connect('tcp:127.0.0.1:5762')
        except Exception as e:
            print("Reconnect error:", e)
        time.sleep(5)

reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
reconnect_thread.start()


#! THREAD BAŞLATMA
homefiles_update_thread = threading.Thread(target=update_homefiles, daemon=True)
homefiles_update_thread.start()

arm_thread = threading.Thread(target=update_arm, daemon=True)
arm_thread.start()

altitude_thread = threading.Thread(target=update_altitude_vario, daemon=True)
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

loc_thread = threading.Thread(target=update_loc, daemon=True)
loc_thread.start()

sound_warning_thread = threading.Thread(target=check_audio_alerts, daemon=True)
sound_warning_thread.start()

reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
reconnect_thread.start()

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
prearm_label.place(x=10, y=550)

rc_roll_label = tk.Label(root, text="Roll (CH1):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_roll_label.place(x=500, y=270)

rc_pitch_label = tk.Label(root, text="Pitch (CH2):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_pitch_label.place(x=500, y=300)

rc_throttle_label = tk.Label(root, text="Throttle (CH3):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_throttle_label.place(x=500, y=330)

rc_yaw_label = tk.Label(root, text="Yaw (CH4):", bg="#2e2e2e", fg="white", font="Helvetica 12")
rc_yaw_label.place(x=500, y=360)



#! ARAÇ TİPİ

if vehicletype == 1:
    vehicleTypeIndicator = tk.PhotoImage(file="images/plane.png")
    vehicleTypeLabel = tk.Label(
        root,
        image=vehicleTypeIndicator,
        bg="#2e2e2e",    
        borderwidth=0,
        highlightthickness=0
    )
    vehicleTypeLabel.image = vehicleTypeIndicator
    vehicleTypeLabel.place(x=700, y=500)
    vti_text = tk.Label(text='ArduPlane', fg='white', bg='#2e2e2e', font='Helvetica 16')
    vti_text.place(x=1, y=580)
elif vehicletype == 2:
    vehicleTypeIndicator = tk.PhotoImage(file="images/copter.png")
    vehicleTypeLabel = tk.Label(
        root,
        image=vehicleTypeIndicator,
        bg="#2e2e2e",    
        borderwidth=0,
        highlightthickness=0
    )
    vehicleTypeLabel.image = vehicleTypeIndicator
    vehicleTypeLabel.place(x=700, y=500)
    vti_text = tk.Label(text='ArduCopter', fg='white', bg='#2e2e2e', font='Helvetica 16')
    vti_text.place(x=1, y=580)
elif vehicletype == 10:
    vehicleTypeIndicator = tk.PhotoImage(file="images/rover.png")
    vehicleTypeLabel = tk.Label(
        root,
        image=vehicleTypeIndicator,
        bg="#2e2e2e",     
        borderwidth=0,
        highlightthickness=0
    )
    vehicleTypeLabel.image = vehicleTypeIndicator
    vehicleTypeLabel.place(x=700, y=500)
    vti_text = tk.Label(text='ArduRover', fg='white', bg='#2e2e2e', font='Helvetica 16')
    vti_text.place(x=1, y=580)



#! HUD
hud_base = tk.Canvas(root, width=480, height=300, bg="white")
hud_base.place(x=0, y=30)

#! HUD CROSSHAIR
def draw_hud_crosshair(roll_angle_deg):
    try:
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

    except Exception as e:
        print(e)
        time.sleep(0.5)

armed_status_label = tk.Label(root, text="ARMED", fg="red", font="Helvetica 14")
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
modes_dropbox = ttk.Combobox(root, values=modes, font='Helvetica 22')
modes_dropbox.set(str(vehicle.mode.name))
modes_dropbox.place(x=10, y=380)

#! ACİL DURUM RTL BUTONU

emergency_rtl_button_image = tk.PhotoImage(file="images/pad.png")
emergency_rtl_button = tk.Button(image=emergency_rtl_button_image, command=emergency_rtl, bg='red')
emergency_rtl_button.place(x=180,y=450)

#! MOD DEĞİŞİM UYGULAMA
def apply_mode():
    selected_mode = modes_dropbox.get()    
    change_mode(selected_mode)
    engine.setProperty('voice', voices[23].id)  # erkek sesi
    engine.setProperty('rate', 160)
    speak(f"flight mode {selected_mode}")
mode_change_button = tk.Button(text='Change Mode', fg='white', bg="#494949", bd=5, relief='ridge', command=apply_mode)
mode_change_button.place(x=360, y=380)

#! ARM KISMI
        

arm_button = tk.Button(text='ARM VEHICLE', fg='white', bg='red', bd=5, relief='ridge', command=arm_vehicle)
arm_button.place(x=10, y=430)

#! YÜKSEKLİK DEĞİŞTİRME

height_title = tk.Label(root, text="CHANGE ALTITUDE", bg='#2e2e2e', fg='white')
height_title.place(x=300, y=430)
height_entry = tk.Entry(root, validate="key", validatecommand=vcmd, font='Helvetica 16', width=10)
height_entry.place(x=300, y=450)
def button_action():
    change_alt(int(height_entry.get()))
    engine.setProperty('voice', voices[23].id)  # erkek sesi
    engine.setProperty('rate', 160)
    speak("changing altitude")
    if int(height_entry.get()) <= 119:
        change_button.config(bg='green')
        height_title.config(text='CHANGE ALTITUDE', fg='white')
        height_entry.config(bg='white')
    elif int(height_entry.get()) >= 120 and int(height_entry.get()) <=200:
        change_button.config(bg='orange')
        height_title.config(text='CHANGE ALTITUDE', fg='orange')
        height_entry.config(bg='orange')
    elif int(height_entry.get()) >= 201:
        change_button.config(bg='red')
        height_title.config(text='CHANGE ALTITUDE', fg='red')
        height_entry.config(bg='red')
change_button = tk.Button(root, text='CHANGE', font='Helvetica 11', command=button_action, bg='green', fg='white')
change_button.place(x=440, y=450)

#! HIZ DEĞİŞTİRME
speed_title = tk.Label(root, text="CHANGE AIRSPEED", bg='#2e2e2e', fg='white')
speed_title.place(x=300, y=530)
speed_entry = tk.Entry(root, validate="key", validatecommand=vcmd, font='Helvetica 16', width=10)
speed_entry.place(x=300, y=550)
def button_action():
    change_airspeed(int(speed_entry.get()))
    engine.setProperty('voice', voices[23].id)  # erkek sesi
    engine.setProperty('rate', 160)
    speak("changing speed")
    if int(speed_entry.get()) <= 19:
        changespeed_button.config(bg='green')
        speed_title.config(text='CHANGE AIRSPEED', fg='white')
        speed_entry.config(bg='white')
    elif int(speed_entry.get()) >= 20 and int(height_entry.get()) <=40:
        changespeed_button.config(bg='orange')
        speed_title.config(text='CHANGE AIRSPEED', fg='orange')
        speed_entry.config(bg='orange')
    elif int(speed_entry.get()) >= 40:
        changespeed_button.config(bg='red')
        speed_title.config(text='CHANGE AIRSPEED', fg='red')
        speed_entry.config(bg='red')
changespeed_button = tk.Button(root, text='CHANGE', font='Helvetica 11', command=button_action, bg='green', fg='white')
changespeed_button.place(x=440, y=550)


#! KALİBRASYONLAR
calibrate_level_button = tk.Button(text='Calibrate LEVEL', fg='white', bg='green', bd=5, command=level_horizon)
level_calibrated = tk.Label(text="", fg='white', bg='#2e2e2e')
level_calibrated.place(x=10, y=520)
calibrate_level_button.place(x=10, y=480)

# maploop Toplevel oluştur
maploop = tk.Toplevel(root)
maploop.geometry("1100x900")
maploop.title('MAP')

map_widget = TkinterMapView(maploop, width=800, height=600, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# Uydu görüntüsü
map_widget.set_tile_server(
    "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    max_zoom=25
)

# İlk marker'ı araç pozisyonunda başlat
initial_lat = vehicle.location.global_frame.lat
initial_lon = vehicle.location.global_frame.lon

if vehicletype == 1:
    mapmarker = tk.PhotoImage(file='images/plane.png')
elif vehicletype == 2:
    mapmarker = tk.PhotoImage(file='images/copter.png')
elif vehicletype == 10:
    mapmarker = tk.PhotoImage(file='images/rover.png')

marker = map_widget.set_marker(
    initial_lat, initial_lon,
    text="Vehicle",
    icon=marker_img
)
homepoint_img_open = Image.open('images/home.png')
homepoint_img = ImageTk.PhotoImage(homepoint_img_open)
homepoint = map_widget.set_marker(
    vehicle.home_location.lat, vehicle.home_location.lon,
    text="Home",
    icon=homepoint_img
)
rotated_img = plane_img.rotate(-yaw, expand=True)
marker_img = ImageTk.PhotoImage(rotated_img)

# Tıklama ile konum görme
def on_map_click(coords):
    lat, lon = coords  # tuple (latitude, longitude)
    print(f"Tıklanan konum: Enlem = {lat}, Boylam = {lon}")

def goto_click(coords):
    lat, lon = coords
    vmode = vehicle.mode.name
    valt = vehicle.location.global_relative_frame.alt
    if vmode == 'GUIDED':
        target_point = LocationGlobalRelative(lat,lon,valt)
        print('Hedefe gidiliyor...')
        engine.setProperty('voice', voices[23].id)  # erkek sesi
        engine.setProperty('rate', 160)
        speak("going to the target")
        vehicle.simple_goto(target_point)
    else:
        print('GUIDED mod olmadan manuel bir şekilde bir konuma gidilemez!')

#! Ev noktasını güncelleme
def set_home(coords):
    try:
        lat, lon = coords
        new_home = LocationGlobal(lat, lon, vehicle.home_location.alt)
        vehicle.home_location = new_home
        print('Home konumu güncellendi!')
        engine.setProperty('voice', voices[23].id)  # erkek sesi
        engine.setProperty('rate', 160)
        speak("home point updated")
    except Exception as e:
        print(e)
        time.sleep(0.5)

# Haritayı marker ile merkezle
map_widget.set_position(lat, lon)
map_widget.add_right_click_menu_command(label='Buraya Git...', command=goto_click, pass_coords=True)
map_widget.add_right_click_menu_command(label='Ev noktası yap', command=set_home, pass_coords=True)
def gui_update_map():
    try:
        global marker, marker_img, lat, lon, yaw, plane_img, homepoint, homepoint_img

        try:
            marker.delete()
            homepoint.delete()

            marker = map_widget.set_marker(
                lat, lon,
                text="Vehicle",
                icon=marker_img
    )
            homepoint = map_widget.set_marker(
                vehicle.home_location.lat, vehicle.home_location.lon,
                text="Home",
                icon=homepoint_img
            )


            if 'lat' in globals() and 'lon' in globals() and 'yaw' in globals():
                

                rotated_img = plane_img.rotate(-yaw, expand=True)
                marker_img = ImageTk.PhotoImage(rotated_img, master=maploop)  
                

                marker.set_position(lat, lon)
                homepoint.set_position(vehicle.home_location.lat, vehicle.home_location.lon)
                map_widget.add_left_click_map_command(on_map_click)
                

        except Exception as e:
            print("Map update error:", e)

        maploop.after(200, gui_update_map)

    except Exception as e:
        print(e)
        time.sleep(0.5)

gui_update_map()


root.mainloop()
