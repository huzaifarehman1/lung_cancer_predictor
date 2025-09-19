import tkinter as tk
from tkinter import messagebox
import os
import pandas
from pyro.distributions import Categorical



class Bayesian_network:
    # given , given_value , tofind , value
    def __init__(self,answer_dict):
        self.data = pandas.read_csv("survey lung cancer.csv")
        attributes = self.data.columns
        for i in attributes:
            if i != "LUNG_CANCER":
                setattr(self,i,answer_dict[i])
        
        P_dict = {}
        for i in attributes:
            if i == "LUNG_CANCER":
                continue
            
            ans = getattr(self,i)
            if (isinstance(ans,int) or isinstance(ans,str)):
                # not needed in if gender or age
                continue
            # calculate required probabilities direct to lungcancer
            # not actually needed for most part but i loved doing it
            prob = self.find_P(i,ans,"LUNG_CANCER","YES")
            P_dict[i] = prob
        
        print(P_dict)
        self.P_dict = P_dict
        
        
            
    def DependenciesOther(self):
        # given , given_value , tofind , tofind_value but here tofing is not cancer
        """self.depend = [("SMOKING","2","ANXIETY","2"),
                       ("ALCOHOL","2","ANXIETY","2"),
                       ("CHRONIC_DISEASE","2","ANXIETY","2"),
                       ("SMOKING","2","PEER_PRESSURE","2"),
                       ("ALCOHOL","2","PEER_PRESSURE","2"),
                       ("CHRONIC_DISEASE","2","PEER_PRESSURE","2"),]
                       but we will combine it to use it"""
                       
        self.depend =  [("SMOKING","2","ALCOHOL","2","CHRONIC_DISEASE","2",
                         "ANXIETY","2"),
                        ("SMOKING","2","ALCOHOL","2","CHRONIC_DISEASE","2",
                         "PEER_PRESSURE","2")]          
        True_prob = {}
        for tup  in self.depend:
            
            pa1, pa2, pa3, pa4, pa5, pa6, v1, v2 = tup
            prob = 0
            filtered_rows = self.data[(self.data[pa1] == pa2) & (self.data[pa3] == pa4) & (self.data[pa5] == pa6)]
            match_count = (filtered_rows[v1] == v2).sum()
            total_count = len(filtered_rows)
            if total_count == 0:
                prob = 0.0
            prob = round(match_count / total_count,6)

            True_prob[v1] = prob #all non negated Prob where anxiety = 2
        return True_prob   
    
    def create_network(self):
        true_P = self.DependenciesOther()
        strings = [] # exact value
        self.remain = []# remianing
        for i in self.data.columns:
            if i == "LUNG_CANCER":
                continue
            
            ans = getattr(self,i)
            if (isinstance(ans,int) or isinstance(ans,str)):
                # not needed in if gender or age
                continue
            if i not in ["ANXIETY","PEER_PRESSURE"]:
                strings.append((i,ans))
            else:
                P = [1-true_P[i],true_P[i]]
                model = Categorical(P) # 0 = no  , 1 = yes 
                self.remain.append((i,model))

    def infer(self,step = 100):
        conditions = []
        cancer_true = 0 
        total = 0
        for i in step:
            pass
              
        
            
        
        
         
                 
                    
                    
            
                   
        #self.P_smoking = None # if he smoke or not than P of lungcancer
        
    def find_P(self, given, given_value, tofind, tofind_value):
        """
        Find the probability P(tofind=tofind_value | given=given_value)
        using frequency counts from self.data.
        """
        # Filter rows where given == given_value
        filtered = self.data[self.data[given] == given_value]
        # Count where tofind == tofind_value in filtered
        match_count = (filtered[tofind] == tofind_value).sum()
        total_count = len(filtered)
        if total_count == 0:
            return 0.0
        probability = round(match_count / total_count,6)
        return probability
        


class HealthSurveyGUI:
    def __init__(self):
        self.questions = {
            "GENDER": ["Male", "Female"],
            "AGE": None,  # Free text (numeric only)
            "SMOKING": ["YES", "NO"],
            "YELLOW_FINGERS": ["YES", "NO"],
            "ANXIETY": ["YES", "NO"],
            "PEER_PRESSURE": ["YES", "NO"],
            "CHRONIC_DISEASE": ["YES", "NO"],
            "FATIGUE": ["YES", "NO"],
            "ALLERGY": ["YES", "NO"],
            "WHEEZING": ["YES", "NO"],
            "ALCOHOL": ["YES", "NO"],
            "COUGHING": ["YES", "NO"],
            "SHORTNESS_BREATH": ["YES", "NO"],
            "SWALLOWING": ["YES", "NO"],
            "CHEST_PAIN": ["YES", "NO"]
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
            if ans in ["YES","NO"]:
                converter = {"YES":True,"NO":False}
                ans = converter[ans]
                
            self.answers[q] = ans

        # Final summary
        summary = "\n".join(f"{k}: {v}" for k, v in self.answers.items())
        messagebox.showinfo("Survey Completed", summary)
        self.root.quit()
        return self.answers


if __name__ == "__main__":
    gui = HealthSurveyGUI()
    ans = gui.start()
    BN = Bayesian_network(ans)