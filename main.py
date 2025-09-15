import tkinter as tk
from tkinter import messagebox
import os


class Bayesian_network:
    pass



class HealthSurveyGUI:
    def __init__(self):
        self.questions = {
            "GENDER": ["Male", "Female"],
            "AGE": None,  # Free text (numeric only)
            "SMOKING": ["Yes", "No"],
            "YELLOW_FINGERS": ["Yes", "No"],
            "ANXIETY": ["Yes", "No"],
            "PEER_PRESSURE": ["Yes", "No"],
            "CHRONIC_DISEASE": ["Yes", "No"],
            "FATIGUE": ["Yes", "No"],
            "ALLERGY": ["Yes", "No"],
            "WHEEZING": ["Yes", "No"],
            "ALCOHOL": ["Yes", "No"],
            "COUGHING": ["Yes", "No"],
            "SHORTNESS_BREATH": ["Yes", "No"],
            "SWALLOWING": ["Yes", "No"],
            "CHEST_PAIN": ["Yes", "No"]
        }

        self.answers = {}
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

    def ask_question(self, question, options):
        """Ask a single question. User cannot cancel or skip."""
        win = tk.Toplevel()
        win.title("Health Survey")
        win.geometry("320x180")
        win.protocol("WM_DELETE_WINDOW", lambda: os._exit(23))

        label = tk.Label(win, text=f"{question}?", font=("Arial", 12))
        label.pack(pady=10)

        answer_var = tk.StringVar()

        def set_answer(value):
            answer_var.set(value)
            win.destroy()

        if options:  # Yes/No or Male/Female
            for opt in options:
                btn = tk.Button(win, text=opt, width=12,
                                command=lambda o=opt: set_answer(o))
                btn.pack(pady=3)
        else:  # AGE input
            entry = tk.Entry(win, font=("Arial", 12))
            entry.pack(pady=5)

            def confirm():
                val = entry.get()
                if not val.isdigit():
                    messagebox.showwarning("Invalid Input", "Please enter a valid number for AGE")
                else:
                    set_answer(val)

            btn = tk.Button(win, text="OK", command=confirm)
            btn.pack(pady=5)

        win.wait_window()  # Wait until answered
        return answer_var.get()

    def start(self):
        for q, opts in self.questions.items():
            if q in ["GENDER",'AGE']:
                tex = q
            elif q == "SMOKING":
                tex = "DO YOU SMOKE?"
            elif q == "ALCOHOL":
                tex = "DO YOU USE ALCOHOL"
            elif q == "SWALLOWING":
                tex = "DO YOU HAVE SWALLOWING PROBLEM"        
            else:
                tex = f"DO YOU HAVE {q}?"    
            ans = self.ask_question(tex, opts)
            self.answers[q] = ans

        # Final summary
        summary = "\n".join(f"{k}: {v}" for k, v in self.answers.items())
        messagebox.showinfo("Survey Completed", summary)
        self.root.quit()


if __name__ == "__main__":
    gui = HealthSurveyGUI()
    gui.start()
