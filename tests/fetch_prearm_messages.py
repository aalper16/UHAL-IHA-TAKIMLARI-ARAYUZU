from dronekit import connect
from pymavlink import mavutil

# Bağlantı (örnek: serial, TCP veya UDP)
vehicle = connect('tcp:127.0.0.1:5762', baud=115200, wait_ready=True)

# STATUSTEXT mesajlarını dinle
def statustext_listener(self, name, message):
    text = message.text
    severity = message.severity

    # Sadece prearm ile ilgili olanları filtrele
    if "PreArm" in text or "prearm" in text:
        print(f"[PREARM UYARISI] {text}")
        print(severity)
    else:
        # Diğer sistem mesajlarını da görmek istersen:
        print(f"[{severity}] {text}")
        pass

# Listener ekle
vehicle.add_message_listener('STATUSTEXT', statustext_listener)

print("Prearm uyarılarını dinliyorum... (Ctrl+C ile çık)")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Çıkılıyor...")
    vehicle.close()
