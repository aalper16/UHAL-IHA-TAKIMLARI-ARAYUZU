import tkinter as tk

# Ana pencereyi oluştur
pencere = tk.Tk()
pencere.title("Canvas Üzerinde Çizgi")

# Canvas oluştur
canvas = tk.Canvas(pencere, width=400, height=300, bg="white")
canvas.pack()

# Çizgi çiz (x1, y1, x2, y2)
canvas.create_line(50, 50, 300, 200, fill="blue", width=3)

# Pencereyi çalıştır
pencere.mainloop()
