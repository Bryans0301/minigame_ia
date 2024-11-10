import cv2
import mediapipe as mp
import random
import time
from screeninfo import get_monitors
import tkinter as tk
from tkinter import messagebox
import pygame  

# Inicializar Pygame y configurar la música
pygame.mixer.init()  # Inicializa el mezclador de audio de Pygame
pygame.mixer.music.load("C:/Users/bryan/OneDrive - IPCHILE - Instituto Profesional de Chile/Escritorio/IA/living_on_video.mp3")  # Carga la música
pygame.mixer.music.set_volume(0.5)  # Establece el volumen (de 0.0 a 1.0)
pygame.mixer.music.play(loops=-1, start=0.0)  # Reproduce la música en bucle (-1 significa bucle infinito)

# Configuración de la resolución
screen_width = 1920
screen_height = 1080

# Configuración del juego
circle_radius = 30
score = 0
correct_words = 0  # Contador de palabras correctas
incorrect_words = 0  # Contador de palabras incorrectas
circles = [] 
num_circles = 4  # Número de círculos (4 para formar una palabra)

# Palabras para el juego
words = ["mama", "papa", "pepe"]

# Guardamos una copia de las palabras originales
original_words = words.copy()

# Inicialización de MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Función para generar círculos con letras aleatorias de una palabra
def generate_circles_for_word(selected_word):
    global circles
    circles = []  # Resetear los círculos
    letters = list(selected_word)  # Convertir la palabra en una lista de letras
    for i in range(num_circles):
        x = random.randint(circle_radius, screen_width - circle_radius)
        y = random.randint(circle_radius, screen_height - circle_radius)
        circles.append((x, y, letters[i]))  # Asignar letra a cada círculo

# Inicialización de la cámara
cap = cv2.VideoCapture(0)

# Configura la cámara para capturar en 1280x720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Configura la ventana de OpenCV para pantalla completa o tamaño específico
cv2.namedWindow("Mini Juego", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Mini Juego", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def show_final_score():
    """Mostrar la puntuación final al usuario."""
    global correct_words, incorrect_words, score
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    messagebox.showinfo("Juego Terminado", f"Puntuación final: {score}\nPalabras correctas: {correct_words}\nPalabras incorrectas: {incorrect_words}")
    root.destroy()

def show_words_screen():
    """Mostrar las palabras originales del juego en pantalla negra con letras blancas al final."""
    words_window = tk.Tk()
    words_window.title("Palabras del Juego")
    words_window.geometry(f"{screen_width}x{screen_height}")
    words_window.config(bg='black')  # Fondo negro

    # Etiqueta que muestra las palabras en el centro de la pantalla
    words_label = tk.Label(words_window, text="Palabras del juego:", font=("Helvetica", 36, "bold"), fg="white", bg="black")
    words_label.pack(pady=50)

    # Mostrar las palabras en la pantalla
    words_text = "\n".join(original_words)  # Unir todas las palabras con saltos de línea
    words_display = tk.Label(words_window, text=words_text, font=("Helvetica", 24), fg="white", bg="black")
    words_display.pack(pady=20)

    # Botón para cerrar la ventana y salir del juego
    close_button = tk.Button(words_window, text="Cerrar", font=("Helvetica", 20, "bold"), fg="white", bg="#39FF14", relief="raised", command=words_window.destroy)
    close_button.pack(pady=50)

    # Ejecutar la ventana para mostrar las palabras
    words_window.mainloop()

def show_welcome_screen():
    """Mostrar la pantalla de bienvenida y tutorial del juego."""
    def close_tutorial():
        tutorial_window.destroy()
        main_game()  # Comienza el juego cuando se cierra el tutorial

    # Crear ventana de bienvenida
    tutorial_window = tk.Tk()
    tutorial_window.title("Bienvenido al Juego")
    tutorial_window.geometry(f"{screen_width}x{screen_height}")
    tutorial_window.config(bg='black')

    # Crear etiqueta de bienvenida
    welcome_label = tk.Label(tutorial_window, text="¡Bienvenido al Mini Juego!", font=("Helvetica", 36, "bold"), fg="white", bg="black")
    welcome_label.pack(pady=50)

    # Crear instrucciones del juego
    instructions = (
        "Instrucciones del juego:\n\n"
        "1. Las palabras aparecerán como círculos con letras.\n"
        "2. Usa tu dedo índice para tocar las letras de la palabra correcta.\n"
        "3. Tienes 30 segundos por palabra.\n"
        "4. Cada letra correcta te dará puntos. Evita tocar letras incorrectas.\n"
        "5. Completa todas las palabras para ganar.\n"
    )
    instructions_label = tk.Label(tutorial_window, text=instructions, font=("Helvetica", 20), fg="white", bg="black")
    instructions_label.pack(pady=20)

    # Crear un botón verde neon para cerrar el tutorial
    close_button = tk.Button(tutorial_window, text="Cerrar Tutorial", font=("Helvetica", 20, "bold"), fg="white", bg="#39FF14", relief="raised", command=close_tutorial)
    close_button.pack(pady=50)

    # Ejecutar la ventana de tutorial
    tutorial_window.mainloop()

# Función principal del juego
def main_game():
    global score, correct_words, incorrect_words
    # Mientras haya palabras disponibles en la lista
    while words:
        start_time = time.time()  # Reiniciar el temporizador al comenzar con una nueva palabra
        game_duration = 30  # Duración de 15 segundos por palabra

        # Seleccionar una palabra aleatoria
        selected_word = random.choice(words)
        generate_circles_for_word(selected_word)
        words.remove(selected_word)  # Eliminar la palabra de la lista de palabras disponibles

        word_completed = False  # Controlador para saber si la palabra fue completada correctamente
        touched_letters = []  # Lista de letras tocadas por el jugador

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Voltea la imagen para que actúe como un espejo
            frame = cv2.flip(frame, 1)

            # Redimensiona el frame para que coincida con el tamaño de la pantalla
            frame = cv2.resize(frame, (screen_width, screen_height))

            # Convierte el marco de BGR a RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Dibuja los círculos en la pantalla con las letras
            for (cx, cy, letter) in circles:
                cv2.circle(frame, (cx, cy), circle_radius, (255, 0, 0), -1)
                cv2.putText(frame, letter.upper(), (cx - 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Si se detecta una mano
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Obtén las coordenadas de la punta del dedo índice
                    index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    index_x = int(index_finger.x * screen_width)
                    index_y = int(index_finger.y * screen_height)

                    # Dibuja la mano
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Verifica si la punta del dedo índice toca algún círculo
                    for i, (cx, cy, letter) in enumerate(circles):
                        distance = ((index_x - cx) ** 2 + (index_y - cy) ** 2) ** 0.5
                        if distance < circle_radius and letter != '':
                            # Si la letra tocada está en la palabra correcta
                            if letter in selected_word:
                                score += 5  # Sumar 5 puntos por cada letra correcta
                                touched_letters.append(letter)  # Añadir la letra tocada a la lista
                                circles[i] = (-150, -150, '')  # Eliminar la letra del círculo tocado
                            else:
                                score -= 2  # Restar 2 puntos por cada letra incorrecta
                                circles[i] = (-150, -150, '')  # Eliminar la letra tocada
                            break  # Sal de la búsqueda para evitar contar múltiples círculos

            # Verifica si todas las letras han sido tocadas
            if all(letter == '' for _, _, letter in circles):
                word_completed = True  # La palabra fue completada correctamente
                cv2.putText(frame, "Palabra completada", (screen_width // 2 - 150, screen_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Mini Juego", frame)
                cv2.waitKey(1000)  # Espera un segundo para mostrar el mensaje
                break  # Salir del bucle y pasar a la siguiente palabra

            # Verifica el tiempo del juego
            elapsed_time = time.time() - start_time
            if elapsed_time > game_duration:
                break  # Terminar el juego si se acabó el tiempo

            # Muestra el puntaje y los contadores en la pantalla
            cv2.putText(frame, f"Score: {score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"Correctas: {correct_words}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Erroneas: {incorrect_words}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Muestra el cuadro en la ventana de OpenCV
            cv2.imshow("Mini Juego", frame)

            # Presiona 'q' para salir
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Verifica si la palabra fue completada correctamente
        if word_completed:
            # Si las letras tocadas son iguales a la palabra seleccionada
            if ''.join(touched_letters) == selected_word:
                correct_words += 1
            else:
                incorrect_words += 1
                score -= 7  # Restar 7 puntos por cada palabra errónea
                cv2.putText(frame, "Palabra erronea", (screen_width // 2 - 150, screen_height // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Mini Juego", frame)
                cv2.waitKey(1000)  # Espera un segundo para mostrar el mensaje
        else:
            incorrect_words += 1
            score -= 7  # Restar 7 puntos por cada palabra errónea
            cv2.putText(frame, "Palabra erronea", (screen_width // 2 - 150, screen_height // 2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Mini Juego", frame)
            cv2.waitKey(1000)  # Espera un segundo para mostrar el mensaje

        # Si ya no hay palabras en la lista, termina el juego
        if not words:
            break

    # Cuando no haya más palabras en la lista, termina el juego
    show_final_score()
    show_words_screen()  # Mostrar las palabras después de terminar el juego
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_welcome_screen()