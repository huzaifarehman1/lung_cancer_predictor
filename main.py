import tkinter as tk
from tkinter import messagebox
import os
import pandas
from pyro.distributions import Categorical
from torch import tensor


class Bayesian_network:
    # given , given_value , tofind , value
    def __init__(self,answer_dict):
        self.data = pandas.read_csv("survey lung cancer.csv")
        attributes = self.data.columns
        for i in attributes:
            if i != "LUNG_CANCER":
                ans = answer_dict[i]
                if (ans == "YES") or (ans == True):
                    ans = 2
                elif (ans == 'NO') or (ans == False):
                    ans = 1    
                setattr(self,i,ans)
        
        P_dict = {}
        for i in attributes:
            if i == "LUNG_CANCER":
                continue
            
            ans = getattr(self,i)
            if i in ["LUNG_CANCER","GENDER","AGE"]:
                # not needed in if gender or age
                continue
            # calculate required probabilities direct to lungcancer
            # not actually needed for most part but i loved doing it
            prob = self.find_P(i,ans,"LUNG_CANCER","YES")
            P_dict[i] = prob  
        
        print("dictionary:", P_dict)
        self.P_dict = P_dict
        self.create_network()
        self.answer = self.infer_way_1(100)
        
        
            
    def DependenciesOther(self):
        # given , given_value , tofind , tofind_value but here tofing is not cancer
        """self.depend = [("SMOKING","2","ANXIETY","2"),
                       ("ALCOHOL","2","ANXIETY","2"),
                       ("CHRONIC_DISEASE","2","ANXIETY","2"),
                       ("SMOKING","2","PEER_PRESSURE","2"),
                       ("ALCOHOL","2","PEER_PRESSURE","2"),
                       ("CHRONIC_DISEASE","2","PEER_PRESSURE","2"),]
                       but we will combine it to use it and use user data only instead
                       of calculating entire probability"""
        convert = lambda x: 1 if not(x) else 2
        self.depend =  [("SMOKING",convert(getattr(self,"SMOKING")),"ALCOHOL",convert(getattr(self,"ALCOHOL")),"CHRONIC_DISEASE",convert(getattr(self,"CHRONIC_DISEASE")),
                         "ANXIETY","2"),
                        ("SMOKING",convert(getattr(self,"SMOKING")),"ALCOHOL",convert(getattr(self,"ALCOHOL")),"CHRONIC_DISEASE",convert(getattr(self,"CHRONIC_DISEASE")),
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
        self.strings = [] # exact value
        self.remain = {}# remianing
        for i in self.data.columns:
            if i == "LUNG_CANCER":
                continue
            
            ans = getattr(self,i)
            if i in ["LUNG_CANCER","GENDER","AGE"]:
                # not needed in if gender or age
                continue
            if i not in ["ANXIETY","PEER_PRESSURE"]:
                assert ans in [1,2]
                self.strings.append((i,ans)) #
            else:
                P = tensor([1-true_P[i],true_P[i]])
                model = Categorical(P) # 0 = no  , 1 = yes 
                self.remain[i] = model

    def infer_way_2(self):
        """
        Naive Bayes inference:
        Compute P(LUNG_CANCER="YES" | evidence) ∝ P(LUNG_CANCER="YES") * ∏_attrs P(attr=val | YES)
        For uncertain attributes in self.remain (ANXIETY, PEER_PRESSURE) marginalize:
        ∑_v P(attr=v) * P(attr=v | class)
        """
        # Prior
        total = len(self.data)
        yes_count = (self.data["LUNG_CANCER"] == "YES").sum()
        # simple prior (no smoothing needed)
        prior_yes = yes_count / total
        prior_no = 1.0 - prior_yes # this was for P(lung_cancer = "YES")

        # Likelihoods
        like_yes = 1.0
        like_no = 1.0

        # Fully observed attributes collected in self.strings
        # no need of marganalization
        for col, val in self.strings:
            p_yes = self.find_P("LUNG_CANCER", "YES", col, val) # p(lung = Yes | attr = v)
            p_no = self.find_P("LUNG_CANCER", "NO", col, val)
            like_yes *= p_yes # product of all 
            like_no *= p_no

        # Partially observed attributes in self.remain (Categorical models)
        for attr, model in self.remain.items():
            probs = model.probs if hasattr(model, "probs") else model.p
            # probs[0] corresponds to value 1, probs[1] to value 2
            marginal_yes = 0.0
            marginal_no = 0.0
            for idx, v in enumerate([1, 2]):
                p_attr_given_yes = self.find_P("LUNG_CANCER", "YES", attr, v) 
                p_attr_given_no = self.find_P("LUNG_CANCER", "NO", attr, v)
                p_v = float(probs[idx])
                marginal_yes += p_attr_given_yes * p_v
                marginal_no += p_attr_given_no * p_v
            like_yes *= marginal_yes
            like_no *= marginal_no

        num = prior_yes * like_yes
        den = num + prior_no * like_no
        if den == 0:
            return 0.0
        posterior_yes = num / den
        return round(posterior_yes, 9)
    
    def infer_way_1(self,step = 100):
        # calculate average of probabilities
        # chnage this way
        anxiety_model:Categorical = self.remain["ANXIETY"]
        pressure_model:Categorical = self.remain["PEER_PRESSURE"]
        
        count = 0
        seen = {}
        converter = [1,2] # +1
        # filter data
        data = self.data
        for i in self.strings:
            col,val = i
            data = data[data[col] == val]
        memorized_data = data    
        for i in range(step):
            value_anxiety = converter[anxiety_model.sample().item()]
            value_pressure = converter[pressure_model.sample().item()]
            if (value_anxiety,value_pressure) not in seen:
                data = data[(data["ANXIETY"] == value_anxiety) & (data["PEER_PRESSURE"] == value_pressure)]
                match_count = (data["LUNG_CANCER"] == "YES").sum()
                total_count = len(data)
                
                # Apply (safe even if total_count > 0)
                if total_count == 0:
                    return self.infer_way_2()
                else:
                    probability = match_count / total_count
                seen[(value_anxiety,value_pressure)] = round(probability,6)    
            else:
                probability = seen[(value_anxiety,value_pressure)]
                
            count += probability
            data = memorized_data
            
        return round(count/step,9)
                   
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
        
        alpha = 1  # smoothing
        k = self.data[tofind].nunique()  # number of possible classes for `tofind`

        # Apply Laplace smoothing (safe even if total_count > 0)
       
        if total_count == 0:
            probability = (match_count + alpha) / (total_count + k * alpha)
        else:
            probability = match_count / total_count
            
        return round(probability, 6)
        


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
        answer =  answer_var.get()
        if question=="AGE":
            return int(answer)
        else:
            return answer

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
                pass
                
            self.answers[q] = ans

        # Final summary
        summary = "\n".join(f"{k}: {v}" for k, v in self.answers.items())
        messagebox.showinfo("Survey Completed", summary)
        self.root.quit()
        return self.answers
    def show_answer(self,ans):
        assert ans<=1
        """
        Takes the survey answers and shows
        Lung Cancer probability in a popup.
        """
        messagebox.showinfo("Prediction Result",
                            f"You have {ans*100}% chance of having Lung Cancer")

if __name__ == "__main__":
    # probabilities are always 0.5 why
    gui = HealthSurveyGUI()
    ans = gui.start()
    BN = Bayesian_network(ans)
    gui.show_answer(BN.answer)