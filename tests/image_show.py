import tkinter as tk
import os

root = tk.Tk()

vehicleTypeIndicator = tk.PhotoImage(file="images/plane.png")
vehicleTypeLabel = tk.Label(root, image=vehicleTypeIndicator)
vehicleTypeLabel.image = vehicleTypeIndicator  # referansı koru!
vehicleTypeLabel.pack()


root.mainloop()
