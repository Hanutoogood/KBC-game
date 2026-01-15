import tkinter as tk
from tkinter import messagebox
import random
import json
from google import genai
from google.genai import types
import pygame

GEMINI_API_KEY = "AIzaSyDE63WJLTlUoJJ3IeMvab-DGXe31HQ4uyM"   
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash-lite"

pygame.mixer.init()

BACKGROUND_MUSIC = "C:\\Users\\admin\\Downloads\\Background music.mp3"
WIN_MUSIC = "C:\\Users\\admin\\Downloads\\7 crores.mp3"

pygame.mixer.music.load(BACKGROUND_MUSIC)

MONEY_LADDER = [
    "₹5,000", "₹10,000", "₹15,000", "₹20,000", "₹25,000",
    "₹50,000", "₹1,00,000", "₹2,00,000", "₹3,00,000", "₹5,00,000",
    "₹10,00,000", "₹25,00,000", "₹50,00,000", "₹1 Crore", "₹7 Crore"
]

class KBCGame:
    def __init__(self, root):
        self.root = root
        self.root.title("KBC 2026: AI Edition")
        self.root.geometry("800x600")
        self.root.configure(bg="#020617")

        # Game State
        self.current_idx = 0
        self.question_bank = []
        self.current_q_data = None
        self.lifelines = {"50:50": True, "Flip": True}

        self.setup_ui()

    def setup_ui(self):
        """Initial Screen to enter topics"""
        self.main_frame = tk.Frame(self.root, bg="#020617")
        self.main_frame.pack(expand=True, fill="both")

        tk.Label(
            self.main_frame,
            text="KAUN BANEGA CROREPATI",
            font=("Arial", 28, "bold"),
            bg="#020617",
            fg="#fbbf24"
        ).pack(pady=30)

        tk.Label(
            self.main_frame,
            text="Enter 3 Topics for your Quiz:",
            font=("Arial", 12),
            bg="#020617",
            fg="white"
        ).pack()

        self.topic_entry = tk.Entry(
            self.main_frame,
            font=("Arial", 14),
            width=40,
            justify="center"
        )
        self.topic_entry.insert(0, "Indian History, Space, Cricket")
        self.topic_entry.pack(pady=10)

        self.start_btn = tk.Button(
            self.main_frame,
            text="START GAME",
            font=("Arial", 14, "bold"),
            bg="#1e40af",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_game
        )
        self.start_btn.pack(pady=20)

    def start_game(self):
        topics = self.topic_entry.get()
        self.start_btn.config(text="Generating Questions...", state="disabled")
        self.root.update()

        pygame.mixer.music.stop()
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.play(-1)

        prompt = f"""
        Generate 15 KBC questions on {topics}.
        Increasing difficulty (5 Easy, 5 Medium, 5 Hard).
        Return ONLY a JSON list of objects:
        {{
          "question": "",
          "options": ["", "", "", ""],
          "answer_idx": 0
        }}
        """

        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            self.question_bank = json.loads(response.text)

            if not isinstance(self.question_bank, list) or len(self.question_bank) < len(MONEY_LADDER):
                raise ValueError("AI returned insufficient questions.")

            self.show_quiz_ui()
            self.load_question()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to AI: {e}")
            self.start_btn.config(text="START GAME", state="normal")
            pygame.mixer.music.stop()

    def show_quiz_ui(self):
        self.main_frame.pack_forget()
        self.quiz_frame = tk.Frame(self.root, bg="#020617")
        self.quiz_frame.pack(expand=True, fill="both")

        self.money_label = tk.Label(
            self.quiz_frame,
            text="Amount: ₹0",
            font=("Arial", 18, "bold"),
            bg="#020617",
            fg="#fbbf24"
        )
        self.money_label.pack(pady=10)

        self.q_text = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 16),
            bg="#020617",
            fg="white",
            wraplength=700,
            justify="center",
            height=4
        )
        self.q_text.pack(pady=20)

        self.ll_frame = tk.Frame(self.quiz_frame, bg="#020617")
        self.ll_frame.pack(pady=10)

        self.btn_5050 = tk.Button(
            self.ll_frame,
            text="50:50",
            width=12,
            bg="#fbbf24",
            command=self.use_5050
        )
        self.btn_5050.grid(row=0, column=0, padx=10)

        self.btn_flip = tk.Button(
            self.ll_frame,
            text="Flip Question",
            width=12,
            bg="#fbbf24",
            command=self.use_flip
        )
        self.btn_flip.grid(row=0, column=1, padx=10)
        self.opt_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.quiz_frame,
                text="",
                font=("Arial", 12),
                width=50,
                pady=10,
                bg="#1e293b",
                fg="white",
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.pack(pady=5)
            self.opt_buttons.append(btn)

    def load_question(self):
        if self.current_idx >= len(MONEY_LADDER):
            self.win_game()
            return

        self.current_q_data = self.question_bank[self.current_idx]

        self.q_text.config(
            text=f"Q{self.current_idx+1}: {self.current_q_data['question']}"
        )
        self.money_label.config(
            text=f"For {MONEY_LADDER[self.current_idx]}"
        )

        for i, opt in enumerate(self.current_q_data['options']):
            self.opt_buttons[i].config(
                text=opt,
                state="normal",
                bg="#1e293b"
            )

    def check_answer(self, user_idx):
        correct_idx = self.current_q_data['answer_idx']

        if user_idx == correct_idx:
            messagebox.showinfo(
                "CORRECT",
                f"Correct! You won {MONEY_LADDER[self.current_idx]}"
            )
            self.current_idx += 1
            self.load_question()
        else:
            pygame.mixer.music.stop()
            self.show_game_over()

    def show_game_over(self):
        self.quiz_frame.pack_forget()

        earned = "₹0"
        if self.current_idx > 0:
            earned = MONEY_LADDER[self.current_idx - 1]

        self.gameover_frame = tk.Frame(self.root, bg="#020617")
        self.gameover_frame.pack(expand=True, fill="both")

        tk.Label(
            self.gameover_frame,
            text="GAME OVER",
            font=("Arial", 32, "bold"),
            fg="red",
            bg="#020617"
        ).pack(pady=40)

        tk.Label(
            self.gameover_frame,
            text=f"You Won: {earned}",
            font=("Arial", 22, "bold"),
            fg="#fbbf24",
            bg="#020617"
        ).pack(pady=20)

        tk.Button(
            self.gameover_frame,
            text="EXIT",
            font=("Arial", 14, "bold"),
            bg="#1e40af",
            fg="white",
            command=self.root.quit
        ).pack(pady=30)

    def use_5050(self):
        if not self.lifelines["50:50"]:
            return

        self.lifelines["50:50"] = False
        self.btn_5050.config(state="disabled", bg="gray")

        correct_idx = self.current_q_data['answer_idx']
        wrong_indices = [i for i in range(4) if i != correct_idx]
        to_remove = random.sample(wrong_indices, 2)

        for idx in to_remove:
            self.opt_buttons[idx].config(text="", state="disabled")

    def use_flip(self):
        if not self.lifelines["Flip"]:
            return

        self.lifelines["Flip"] = False
        self.btn_flip.config(state="disabled", bg="gray")

        prompt = f"""
        Generate ONE MCQ question for a KBC game.
        Difficulty Level: {self.current_idx + 1}/15
        Topics: {self.topic_entry.get()}

        Return STRICT JSON only:
        {{
          "question": "...",
          "options": ["A","B","C","D"],
          "answer_idx": 0
        }}
        """

        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            new_q = json.loads(response.text)

            # Replace current question
            self.question_bank[self.current_idx] = new_q
            self.current_q_data = new_q

            self.q_text.config(
                text=f"Q{self.current_idx+1}: {new_q['question']}"
            )

            for i, opt in enumerate(new_q["options"]):
                self.opt_buttons[i].config(
                    text=opt,
                    state="normal",
                    bg="#1e293b"
                )

        except Exception as e:
            messagebox.showwarning("AI Error", f"Could not flip question: {e}")
            self.lifelines["Flip"] = True
            self.btn_flip.config(state="normal", bg="#fbbf24")

    def win_game(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(WIN_MUSIC)
        pygame.mixer.music.play()

        messagebox.showinfo(
            "VICTORY",
            "Congratulations! You have won ₹7 Crore!"
        )
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = KBCGame(root)
    root.mainloop()
