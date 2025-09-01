# -*- coding: utf-8 -*- 
import time
import random
import cv2
import pygame
import tkinter as tk
from tkinter import messagebox
import mediapipe as mp
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os
import sys

# Música de fondo
pygame.mixer.init()
pygame.mixer.music.load("C:/Users/bryan/OneDrive - IPCHILE - Instituto Profesional de Chile/Escritorio/IA/living_on_video.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1, start=0.0)

circle_radius = 30
score = 0
correct_words = 0
incorrect_words = 0
circles = []
player_name = ""

frame_width = 1920
frame_height = 1080

word_list = [
    "gato", "casa", "flor", "luna", "mesa", "pino", "nuez", "zeta",
    "vaca", "pato", "bote", "cubo", "rosa", "loro", "vaso", "tren"
]

word_hints = {
    "gato": "Animal doméstico que maúlla.",
    "casa": "Lugar donde vives.",
    "flor": "Planta colorida con pétalos.",
    "luna": "Satélite natural de la Tierra.",
    "mesa": "Mueble con patas para comer.",
    "pino": "Árbol de hojas perennes.",
    "nuez": "Fruto seco con cáscara dura.",
    "zeta": "Última letra del abecedario.",
    "vaca": "Animal que da leche.",
    "pato": "Ave que nada y grazna.",
    "bote": "Vehículo para viajar por agua.",
    "cubo": "Figura con seis caras cuadradas.",
    "rosa": "Flor con espinas.",
    "loro": "Ave que puede imitar sonidos.",
    "vaso": "Objeto donde se bebe líquido.",
    "tren": "Vehículo que corre sobre rieles."
}

extra_hints = {
    "gato": "Tiene bigotes y le gusta cazar ratones.",
    "casa": "Tiene puertas, ventanas y a veces jardín.",
    "flor": "Se regala en San Valentín.",
    "luna": "Sale de noche y cambia de forma.",
    "mesa": "Se usa para comer o estudiar.",
    "pino": "Muy común en Navidad.",
    "nuez": "Está dentro de una cáscara dura y se come.",
    "zeta": "Empieza la palabra 'zorro'.",
    "vaca": "Muge y vive en el campo.",
    "pato": "Hace cuac cuac y tiene pico.",
    "bote": "Flota en el agua, pero no es un pez.",
    "cubo": "Tiene 6 caras iguales.",
    "rosa": "Flor con espinas y pétalos suaves.",
    "loro": "Puede repetir lo que dices.",
    "vaso": "Contiene líquido, pero no lo derrama.",
    "tren": "Corre sobre rieles y lleva pasajeros."
}

def draw_text_with_border(img, text, position, font_path="C:/Windows/Fonts/arial.ttf",
                          font_size=32, text_color=(255,255,255), border_color=(0,0,0), border_thickness=2):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    x, y = position
    for dx in range(-border_thickness, border_thickness+1):
        for dy in range(-border_thickness, border_thickness+1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=border_color)
    draw.text((x, y), text, font=font, fill=text_color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def generate_circles_for_word(selected_word):
    global circles
    circles = []
    for letter in selected_word:
        x = random.randint(circle_radius, frame_width - circle_radius)
        y = random.randint(circle_radius + 100, frame_height - circle_radius)
        circles.append((x, y, letter))

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cv2.namedWindow("Mini Juego", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Mini Juego", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def save_score(name, score):
    with open("score.txt", "a", encoding="utf-8") as f:
        f.write(f"{name},{score}\n")

def read_scores():
    scores = []
    if os.path.exists("score.txt"):
        with open("score.txt", "r", encoding="utf-8") as f:
            for line in f:
                try:
                    n, s = line.strip().split(",")
                    scores.append((n, int(s)))
                except:
                    pass
    return scores

def show_final_screen(played_words):
    global player_name, score
    save_score(player_name, score)
    scores = read_scores()
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    final_window = tk.Tk()
    final_window.title("🏆 Resultado del Juego")
    final_window.state("zoomed")
    final_window.config(bg='black')

    tk.Label(final_window, text="🎉 ¡Juego Finalizado! 🎉", font=("Comic Sans MS", 48, "bold"), fg="white", bg="black").pack(pady=20)
    tk.Label(final_window, text="📜 Palabras del juego:", font=("Comic Sans MS", 36, "bold"), fg="white", bg="black").pack(pady=10)
    tk.Label(final_window, text="\n".join(played_words), font=("Comic Sans MS", 28), fg="white", bg="black").pack(pady=10)
    tk.Label(final_window, text="⭐ Historial de puntajes:", font=("Comic Sans MS", 36, "bold"), fg="white", bg="black").pack(pady=20)

    scores_text = "\n".join([f"{i+1}. {n}: {s}" for i, (n, s) in enumerate(scores[:10])])
    tk.Label(final_window, text=scores_text, font=("Comic Sans MS", 28), fg="white", bg="black", justify="left").pack(pady=10)
    tk.Label(final_window, text="👉 Presiona ENTER para salir", font=("Comic Sans MS", 28), fg="#FF4C29", bg="black").pack(pady=40)

    final_window.bind("<Return>", lambda e: (final_window.destroy(), sys.exit()))
    final_window.mainloop()

def show_welcome_screen():
    def start_tutorial(event=None):
        global player_name
        player_name = entry.get().strip()
        if player_name == "":
            messagebox.showwarning("Error", "Por favor ingresa un nombre válido.")
            return
        welcome_window.destroy()
        show_tutorial()

    welcome_window = tk.Tk()
    welcome_window.title("🎮 ¡Adivina la Palabra Oculta!")
    welcome_window.state("zoomed")

    frame = tk.Frame(welcome_window, bg='#87CEEB', bd=5, relief='ridge')
    frame.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(frame, text="🔥 ¡Bienvenido al juego Adivina la Palabra Oculta! 🔥", font=("Comic Sans MS", 40, "bold"), fg="#1E3A8A", bg='#87CEEB').pack(pady=30, padx=50)
    tk.Label(frame, text="👤 Ingresa tu nombre y presiona Enter:", font=("Comic Sans MS", 24), fg="#0B3D91", bg='#87CEEB').pack(pady=20)

    entry = tk.Entry(frame, font=("Comic Sans MS", 24))
    entry.pack(pady=10)
    entry.focus_set()
    entry.bind("<Return>", start_tutorial)

    welcome_window.mainloop()

def show_tutorial():
    def start_game(event=None):
        tutorial_window.destroy()
        main_game()

    tutorial_window = tk.Tk()
    tutorial_window.title("📖 Tutorial")
    tutorial_window.state("zoomed")

    instructions = (
        "📖 Instrucciones del juego:\n\n"
        "1️ Las palabras aparecerán como círculos con letras.\n"
        "2️ Usa tu dedo índice para tocar las letras de la palabra correcta.\n"
        "3️ Tienes 30 segundos por palabra.\n"
        "4️ Presiona 'P' si necesitas una pista extra.\n"
        "5️ Presiona 'S' para pasar a la siguiente palabra.\n"
        "6️ Presiona 'ESC' para salir del juego.\n"
        "7️ Completa todas las palabras para ganar 🏆.\n\n"
        "👉 Presiona ENTER para empezar"
    )
    tk.Label(tutorial_window, text=instructions, font=("Comic Sans MS", 26), justify="left").pack(pady=100, padx=50)
    tutorial_window.bind("<Return>", start_game)
    tutorial_window.mainloop()

def main_game():
    global score, correct_words, incorrect_words, circles, player_name
    played_words = []
    words = random.sample(word_list, 4)

    while words:
        start_time = time.time()
        game_duration = 30
        selected_word = words.pop(0)
        played_words.append(selected_word)
        hint = word_hints.get(selected_word, "Sin pista disponible")
        second_hint = extra_hints.get(selected_word, "No hay más pistas.")
        use_second_hint = False
        generate_circles_for_word(selected_word)
        touched_letters = []
        forced_incorrect = False  # Flag para presionar 'S'

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (frame_width, frame_height))
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            current_hint = second_hint if use_second_hint else hint
            frame = draw_text_with_border(frame, f"Pista: {current_hint}", (675, 20), font_size=36, text_color=(255,255,255))

            elapsed_time = time.time() - start_time
            remaining_time = max(0, int(game_duration - elapsed_time))
            frame = draw_text_with_border(frame, f"Tiempo restante: {remaining_time} seg", (760, 60), font_size=32, text_color=(255,255,255))

            for i, (cx, cy, letter) in enumerate(circles):
                cv2.circle(frame, (cx, cy), circle_radius, (255, 0, 0), -1)
                cv2.putText(frame, letter.upper(), (cx-10, cy+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            # Detección de mano
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    index_x = int(index_finger.x * frame_width)
                    index_y = int(index_finger.y * frame_height)
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    for i, (cx, cy, letter) in enumerate(circles):
                        distance = ((index_x - cx) ** 2 + (index_y - cy) ** 2) ** 0.5
                        if distance < circle_radius and letter != '':
                            touched_letters.append(letter)
                            circles[i] = (-150, -150, '')
                            break

            # Mostrar score
            frame = draw_text_with_border(frame, f"Puntuación: {score}", (10, 10), font_size=28, text_color=(0,0,255))
            frame = draw_text_with_border(frame, f"Correctas: {correct_words}", (10, 50), font_size=28, text_color=(0,255,0))
            frame = draw_text_with_border(frame, f"Erróneas: {incorrect_words}", (10, 90), font_size=28, text_color=(255,0,0))

            cv2.imshow("Mini Juego", frame)
            key = cv2.waitKey(10) & 0xFF
            if key == 27:
                words.clear()
                break
            elif key == ord('p'):
                use_second_hint = True
            elif key == ord('s'):
                forced_incorrect = True  # Presionar 'S' marca palabra incorrecta
                

            # Fin de palabra
            if all(letter == '' for _, _, letter in circles) or remaining_time <= 0 or forced_incorrect:
                formed_word = ''.join(touched_letters)
                if forced_incorrect:
                    incorrect_words += 1
                    result_text = f"¡Palabra oculta incorrecta!"
                    color_result = (0,0,255)
                    score -= 7
                elif formed_word == selected_word:
                    correct_words += 1
                    result_text = f"¡Palabra oculta correcta!"
                    color_result = (0,255,0)
                    score += 5 * len(selected_word)
                else:
                    incorrect_words += 1
                    result_text = f"¡Palabra oculta incorrecta!"
                    color_result = (0,0,255)
                    score -= 7

                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (frame_width, frame_height))
                frame = draw_text_with_border(frame, result_text, (frame_width//2 - 400, frame_height//2), font_size=40, text_color=color_result)
                cv2.imshow("Mini Juego", frame)
                cv2.waitKey(1500)
                break

    cap.release()
    cv2.destroyAllWindows()
    show_final_screen(played_words)

if __name__ == "__main__":
    show_welcome_screen()

