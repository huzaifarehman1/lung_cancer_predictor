import tkinter as tk
from tkinter import ttk, messagebox
import pandas
import torch
import pyro
from pyro.distributions import Bernoulli,constraints,Beta,Binomial
from pyro.infer import SVI, Trace_ELBO,Importance, EmpiricalMarginal
from pyro.optim import Adam



class network:
    def __init__(self,data:pandas.DataFrame):
        
        self.data = data
        
        lis = [
    "smoking", "yellow_fingers", "anxiety", "peer_pressure",
    "chronic_disease", "fatigue", "allergy", "wheezing",
    "alcohol", "coughing", "shortness_breath",
    "swallowing", "chest_pain"
]
        accuracy_lis = [0.98 , 0.95 , 0.78 , 0.84,
                        0.978, 0.93 , 0.97 , 0.98,
                        0.97 , 0.94 , 0.98 ,
                        0.85 , 0.987
                        ]
        for i in lis:
            name1 = i + "_T"
            name2 = i + "_O"
            value1,value2  = self.find_T_O(i.upper())# column name
            setattr(self, name1, value1)
            setattr(self, name2, value2)
        
        self.P_distribution = {}
        k = 0
        for i in lis:
            name1 = i + "_T"
            name2 = i + "_O"
            temp1 = getattr(self,name1)
            temp2 = getattr(self,name2)
            self.P_distribution[i] = self.do_svi_boolean(i.upper(),temp1,temp2,accuracy_lis[k],100)
            k += 1
            
    
    def find_T_O(self,name):
        # 2 = yes 1  = no
        if name not in self.data.columns:
            raise Exception(f"Wrong column name {name}")
        yes_count = (self.data[name] == 2).sum()  # count how many = 2
        no_count  = (self.data[name] == 1).sum()  # count how many = 1
        total     = yes_count + no_count
        return total,yes_count 
    
    
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

        
    
    def create_network(self,features):
        P_age = 0 #hard part
        age = pyro.sample("age",P_age)
        lis = [
    "smoking", "yellow_fingers", "anxiety", "peer_pressure",
    "chronic_disease", "fatigue", "allergy", "wheezing",
    "alcohol", "coughing", "shortness_breath",
    "swallowing", "chest_pain"
]
        nodes = {"AGE":age}
        for i in lis:
            name = i.upper() 
            observed = 0. if features[i.upper()]==0 else 1.0 #here
            temp = pyro.sample(name,self.P_distribution[i],obs=torch.tensor(observed))
            nodes[i] = temp
            
        
        
    def predict(self):   
        pass

class CancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lung Cancer Predictor")
        # reading data
        path = "survey lung cancer.csv"
        data = pandas.read_csv(path)

        self.network = network(data)
        
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

            self.network.create_network(features)
            result = self.network.predict()
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
        
        