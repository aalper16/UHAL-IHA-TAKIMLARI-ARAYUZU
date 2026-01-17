# UHAL-IHA-TAKIMLARI-ARAYÜZÜ

<img width="1925" height="1077" alt="Screenshot from 2025-10-09 21-19-47" src="https://github.com/user-attachments/assets/c190b007-b5ad-489e-927f-6396d1077b82" />

**UHAL-IHA-TAKIMLARI-ARAYÜZÜ**, insansız hava araçları (İHA) takımlarının entegrasyonunu ve kontrolünü kolaylaştıran bir Python tabanlı arayüzdür. Bu proje, ArduPilot tabanlı İHA sistemleriyle uyumlu olup, kullanıcıların uçuş parametrelerini gerçek zamanlı olarak izlemelerini ve yönetmelerini sağlar.

## Özellikler

- **Gerçek Zamanlı Veri İzleme:** Uçuş verilerini anlık olarak görüntüleme
- **Çoklu Protokol Desteği:** MAVLink ve diğer protokollerle uyumluluk
- **Kullanıcı Dostu Arayüz:** Tkinter tabanlı grafiksel kullanıcı arayüzü
- **Esnek Yapı:** Modüler tasarım sayesinde kolay özelleştirme

## Kurulum

### Gereksinimler

- Python 3.6 veya üzeri
- pip paket yöneticisi
- Aşağıdaki Python kütüphaneleri:
  - `dronekit`
  - `pymavlink`
  - `tkinter`
  - `numpy`
  - `pygame`
  - `Pillow`
  - `tkintermapview`

### Adımlar

1. Sanal ortam kurun:
     ```bash
   sudo apt install python3 python3-venv

2. Sanal ortam oluşturun:
     ```bash
   python3 -m venv venv

3. Sanal ortamı aktive edin:
   ```bash
   source venv/bin/activate

4. Depoyu klonlayın:
   ```bash
   git clone https://github.com/aalper16/UHAL-IHA-TAKIMLARI-ARAYUZU.git
   
5. Uygulama dizinine geçin:
   ```bash
   cd UHAL-IHA-TAKIMLARI-ARAYUZU

6. Gerekli kütüphaneleri yükleyin:
      ```bash
   pip install -r requirements.txt
      
7. Uygulamayı başlatın:
   ```bash
   python3 run.py
