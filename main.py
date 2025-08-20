import tkinter as tk
from tkinter import ttk, messagebox
import pandas
import torch
import pyro
from pyro.distributions import Bernoulli,constraints,Beta,Binomial
from pyro.infer import SVI, Trace_ELBO,Importance, EmpiricalMarginal
from pyro.optim import Adam


# reading data
path = "survey lung cancer.csv"
data = pandas.read_csv(path)

class network:
    def __init__(self):
        lis = [
    "smoking", "yellow_fingers", "anxiety", "peer_pressure",
    "chronic_disease", "fatigue", "allergy", "wheezing",
    "alcohol", "coughing", "shortness_breath",
    "swallowing", "chest_pain"
]
        self.smoking_T = 0
        self.smoking_O = 0
        
        for i in lis:
            name1 = i + "_T"
            name2 = i + "_O"
            value1,value2  = self.find_T_O()# column name
            setattr(self, name1, value1)
            setattr(self, name2, value2)
        
        P_distribution = {}
        
        for i in lis:
            pass
            
    
    
    def do_svi_boolean(self,name,total,observed,accuracy,steps=3000):
        pyro.clear_param_store()
        #model part
        def make_model(observed, accuracy):
            def modelEXE():
                true_prob = pyro.sample(f"P_{name}", Beta(2.0, 2.0))
                
                # We assume observed proportion is a noisy measurement of the true probability
                # So we model it as Beta-distributed around true_prob (with fixed concentration)
                eff_total = int(round(total * accuracy))
                eff_observed = int(round(observed * accuracy))

                pyro.sample(f"obs_{name}",Binomial(total_count=eff_total, probs=true_prob),obs=torch.tensor(eff_observed, dtype=torch.long))

            return modelEXE
        #guide part
        def guideEXE():
            alpha_q = pyro.param(f"alpha_P_{name}", torch.tensor(2.0), constraint=constraints.positive)
            beta_q = pyro.param(f"beta_P_{name}", torch.tensor(2.0), constraint=constraints.positive)
            pyro.sample(f"P_{name}", Beta(alpha_q, beta_q))
            
        #svi part
        modelEXE = make_model(observed, accuracy)
        svi = SVI(model=modelEXE, guide=guideEXE,
                optim=Adam({"lr": 0.01}), loss=Trace_ELBO())

        for _ in range(steps):
            svi.step()

        alpha_val = pyro.param(f"alpha_P_{name}").item()
        beta_val = pyro.param(f"beta_P_{name}").item()
        posterior = Beta(alpha_val, beta_val)
        sample_p = posterior.sample()
        return sample_p

        
    
    def create_network(self):
        P_age = 0 #hard part
        age = pyro.sample("age",P_age)
        
        P_smoking = self.do_svi_boolean("SMOKING",self.smoking_T,self.smoking_O,0.94,2000)
        smoking = pyro.sample("smoking",P_smoking)
        
        P_yellow_fingers = self.do_svi_boolean("YELLOW_FINGERS", self.yellow_fingers_T, self.yellow_fingers_O, 0.94, 2000)
        yellow_fingers = pyro.sample("yellow_fingers", P_yellow_fingers)

        P_anxiety = self.do_svi_boolean("ANXIETY", self.anxiety_T, self.anxiety_O, 0.94, 2000)
        anxiety = pyro.sample("anxiety", P_anxiety)

        P_peer_pressure = self.do_svi_boolean("PEER_PRESSURE", self.peer_pressure_T, self.peer_pressure_O, 0.94, 2000)
        peer_pressure = pyro.sample("peer_pressure", P_peer_pressure)

        P_chronic_disease = self.do_svi_boolean("CHRONIC_DISEASE", self.chronic_disease_T, self.chronic_disease_O, 0.94, 2000)
        chronic_disease = pyro.sample("chronic_disease", P_chronic_disease)

        P_fatigue = self.do_svi_boolean("FATIGUE", self.fatigue_T, self.fatigue_O, 0.94, 2000)
        fatigue = pyro.sample("fatigue", P_fatigue)

        P_allergy = self.do_svi_boolean("ALLERGY", self.allergy_T, self.allergy_O, 0.94, 2000)
        allergy = pyro.sample("allergy", P_allergy)

        P_wheezing = self.do_svi_boolean("WHEEZING", self.wheezing_T, self.wheezing_O, 0.94, 2000)
        wheezing = pyro.sample("wheezing", P_wheezing)

        P_alcohol = self.do_svi_boolean("ALCOHOL_CONSUMING", self.alcohol_T, self.alcohol_O, 0.94, 2000)
        alcohol = pyro.sample("alcohol", P_alcohol)

        P_coughing = self.do_svi_boolean("COUGHING", self.coughing_T, self.coughing_O, 0.94, 2000)
        coughing = pyro.sample("coughing", P_coughing)

        P_shortness_breath = self.do_svi_boolean("SHORTNESS_OF_BREATH", self.shortness_breath_T, self.shortness_breath_O, 0.94, 2000)
        shortness_breath = pyro.sample("shortness_breath", P_shortness_breath)

        P_swallowing = self.do_svi_boolean("SWALLOWING_DIFFICULTY", self.swallowing_T, self.swallowing_O, 0.94, 2000)
        swallowing = pyro.sample("swallowing", P_swallowing)

        P_chest_pain = self.do_svi_boolean("CHEST_PAIN", self.chest_pain_T, self.chest_pain_O, 0.94, 2000)
        chest_pain = pyro.sample("chest_pain", P_chest_pain)
        
        
        
        
    def predict(self,features):
        print(features)
        return "50"    

class CancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lung Cancer Predictor")
        self.network = network()
        self.show_welcome_screen()


    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)


        title = ttk.Label(frame, text="Lung Cancer Prediction", font=("Arial", 18, "bold"))
        title.pack(pady=20)


        start_btn = ttk.Button(frame, text="Start Survey", command=self.show_form_screen)
        start_btn.pack(pady=10)


    def show_form_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)


        self.inputs = {}
        fields = [
        "AGE", "SMOKING", "YELLOW_FINGERS", "ANXIETY",
        "PEER_PRESSURE", "CHRONIC DISEASE", "FATIGUE ", "ALLERGY ",
        "WHEEZING", "ALCOHOL CONSUMING", "COUGHING",
        "SHORTNESS OF BREATH", "SWALLOWING DIFFICULTY", "CHEST PAIN"
        ]


        row = 0
        for field in fields:
            label = ttk.Label(frame, text=field)
            label.grid(row=row, column=0, sticky="w", pady=5)


            if field == "AGE":
                entry = ttk.Entry(frame)
                entry.grid(row=row, column=1, pady=5)
                self.inputs[field] = entry
            else:
                combo = ttk.Combobox(frame, values=["No", "Yes"], state="readonly")
                combo.current(0)
                combo.grid(row=row, column=1, pady=5)
                self.inputs[field] = combo
            row += 1


        submit_btn = ttk.Button(frame, text="Predict", command=self.predict_cancer)
        submit_btn.grid(row=row, columnspan=2, pady=20)


    def predict_cancer(self):
        try:
            features = {}
            for field, widget in self.inputs.items():
                if field == "AGE":
                    features[field] = int(widget.get())
                else:
                    temp =  widget.get()
                    if temp == "No":
                        features[field] = 0
                    else:
                        features[field] = 1    


            result = self.network.predict(features)
            self.show_result_screen(result)


        except Exception as e:
            messagebox.showerror("Error", str(e))


    def show_result_screen(self, result):
        for widget in self.root.winfo_children():
            widget.destroy()


        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)


        msg = ttk.Label(frame, text=f"Prediction Result: {result}", font=("Arial", 16))
        msg.pack(pady=20)


        back_btn = ttk.Button(frame, text="Back to Start", command=self.show_welcome_screen)
        back_btn.pack(pady=10)


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CancerApp(root)
    root.mainloop()        
        
        