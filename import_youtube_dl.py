from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from pytubefix import YouTube
from moviepy import *
from tkinter import messagebox
from threading import Thread
import os
import sys

# Definimos la variable raiz que es nuestra ventana.
raiz = Tk()
# Le damos título a la ventana.
raiz.title("Youtube to mp3 converter by Marcos Jabalquinto. 2023. V.1.1")
# Especificamos que se puede modificar el tamaño de la ventana. Ancho x alto. Es booleano. 0 = no. 1 = sí.
raiz.resizable(0, 0)
# También podemos especificar el tamaño de la ventana.
raiz.geometry("640x480")
# Color de fondo.
#raiz.config(bg="black")

# Verificar el entorno de ejecución para cargar recursos.
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Insertamos logo de fondo:
image_path = os.path.join(base_path, 'fondo.png')
image = PhotoImage(file=image_path)
canvas = Canvas(raiz, width=image.width(), height=image.height())
canvas.create_image(0, 0, image=image, anchor=NW)
canvas.place(x=200, y=100)

def download_video(url, progressbar):
    if os.name == 'nt':  # Windows
        user_documents = os.path.join(os.path.expanduser("~"), "Documents")
        video_path = os.path.join(user_documents, "videoconverter")
    else:  # macOS y Linux
        video_path = os.path.expanduser("~/Documents/videoconverter")

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    try:
        video = YouTube(url)
        video_title = "".join(x for x in video.title if x.isalnum() or x in (' ', '-', '_')).strip()
        video_title = video_title.replace(" ", "_")
        print(f"Descargando: {video_title}")

        stream = video.streams.get_highest_resolution()
        stream.download(video_path, filename=video_title + ".mp4")

        thread = Thread(target=convert_to_mp3, args=(video_path, video_title + ".mp4", progressbar))
        thread.start()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el video: {e}")

def convert_to_mp3(video_path, video_filename, progressbar):
    video_filename = os.path.join(video_path, video_filename)

    if not os.path.exists(video_filename):
        messagebox.showerror("Error", f"El archivo {video_filename} no se encontró.")
        return

    try:
        audio_filename = f"{os.path.splitext(video_filename)[0]}.mp3"
        video = VideoFileClip(video_filename)
        audio = video.audio
        audio.write_audiofile(audio_filename)
        update_progressbar(progressbar, 99)
        audio.close()  # Cerramos el archivo de audio
        video.close()  # Cerramos el archivo de video

        # Eliminar el archivo de vídeo original
        os.remove(video_filename)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir o eliminar el archivo: {e}")



def update_progressbar(progressbar, remaining_steps):
    if remaining_steps > 0:
        progressbar.step(1)
        progressbar.after(100, update_progressbar, progressbar, remaining_steps - 1)
    elif remaining_steps == 0:
        on_conversion_complete()

def on_conversion_complete():
    messagebox.showinfo("Conversión completada", "La conversión del archivo de video a audio se ha completado con éxito.")
    if os.name != 'nt':
        os.system(f'open "{os.path.realpath(os.path.expanduser("~/Documents/videoconverter"))}"')
    else:
        os.system(f'start explorer "{os.path.realpath(os.path.join(os.path.expanduser("~"), "Documents", "videoconverter"))}"')

bar_label = Label(raiz, text="Progreso:")
bar_label.grid(row=0, column=6, padx=2, pady=0)
progressbar = ttk.Progressbar(raiz, orient='horizontal', length=200, mode='determinate', maximum=100)
progressbar.grid(row=0, column=7)

def on_button_click():
    raiz.destroy()

v = StringVar()

url_label = Label(raiz, text="URL de youtube:")
url_label.grid(row=0, column=3, padx=2, pady=0)
url = Entry(raiz, textvariable=v, width=60)
url.grid(row=0, column=4, padx=2, pady=0)

convert_button = Button(raiz, text="Convertir", command=lambda: download_video(url.get(), progressbar))
convert_button.grid(row=9, column=4, padx=3, pady=0)

salir = Button(raiz, text="Salir", command=on_button_click)
salir.grid(row=0, column=8, padx=4, pady=0)

if __name__ == "__main__":
    raiz.mainloop()
