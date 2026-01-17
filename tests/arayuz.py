from tkinter import *
import tkinter as tk

isim="alper"
sifre="3131"

arayuz = tk.Tk()
arayuz.geometry('300x100')
arayuz.title('kullanici')
arayuz.configure(bg='#2e2e2e')

isiminput = tk.Entry(width=10,bg='#2e2e2e', fg='white')
isiminput.pack()
sifreinput = tk.Entry(width=10,bg='#2e2e2e', fg='white')
sifreinput.pack()
sonuc = tk.Label(arayuz, bg='#2e2e2e', fg='white')
sonuc.pack()
def kontrol():
    global isim, sifre, isiminput, sifreinput
    if isim == str(isiminput.get()) and sifre == str(sifreinput.get()):
        print('giris basarili')
        sonuc.config(text='basarili')
    else:
        print('hatalı')
        sonuc.config(text='hatali')

gir = tk.Button(text='gir', command=kontrol,bg='#2e2e2e',fg='white')
gir.pack()



arayuz.mainloop()