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
raiz.config(bg="black")

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
canvas.place(x=0, y=0)  # Colocamos la imagen de fondo en la parte superior de la ventana

# Funciones para la descarga y conversión de video
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
    messagebox.showinfo("Conversión completada", "Tu canción está lista!!")
    if os.name != 'nt':
        os.system(f'open "{os.path.realpath(os.path.expanduser("~/Documents/videoconverter"))}"')
    else:
        os.system(f'start explorer "{os.path.realpath(os.path.join(os.path.expanduser("~"), "Documents", "videoconverter"))}"')

# Elementos de la interfaz
font_style_label = ("Helvetica", 11, "bold")  # Tipo de fuente: Helvetica, tamaño 14, negrita
url_label = Label(raiz, text="URL de youtube:", fg="white", bg="black", font=font_style_label)
url_label.place(x=20, y=10)  # Etiqueta de URL en la parte superior
url = Entry(raiz, width=60)
url.place(x=150, y=10)  # Campo de entrada de URL justo debajo de la etiqueta

bar_label = Label(raiz, text="Conversión:", fg="white", bg="black", font=font_style_label)
bar_label.place(x=20, y=40)  # Etiqueta de progreso justo debajo del campo de URL

progressbar = ttk.Progressbar(raiz, orient='horizontal', length=200, mode='determinate', maximum=100)
progressbar.place(x=150, y=40)  # Barra de progreso debajo de su etiqueta

# Botones
font_style = ("verdana", 20, "bold")  # Tipo de fuente: Arial, tamaño 14, negrita
font_style_salir = ("Tahoma", 11, "bold")  # Tipo de fuente: Arial, tamaño 14, negrita
convert_button = Button(raiz, text="Convertir", height=1, width=12, font=font_style, command=lambda: download_video(url.get(), progressbar))
convert_button.place(x=200, y=380)  # Botón "Convertir" debajo de la barra de progreso

salir_button = Button(raiz, text="Salir", font=font_style_salir, command=raiz.quit)
salir_button.place(x=550, y=400)  # Botón "Salir" al lado del botón "Convertir"

# Iniciamos el bucle principal de la ventana
if __name__ == "__main__":
    raiz.mainloop()
