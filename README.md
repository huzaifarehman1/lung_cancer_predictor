🫁 Lung Cancer Estimator (Naïve Bayes + GUI)

This project is a Bayesian Network–based health survey tool that predicts the probability of having lung cancer based on lifestyle and health factors.
It uses Naïve Bayes inference and a Tkinter GUI to collect user responses interactively.

✨ Features

📊 Dataset-driven: Uses survey lung cancer.csv for probability calculations.

🤖 Bayesian inference: Implements two inference strategies:

infer_way_1 → Sampling-based estimation.

infer_way_2 → Direct Naïve Bayes probability computation.

🖥️ GUI Survey: User-friendly Tkinter interface with Yes/No and Male/Female buttons.

🔎 Uncertain attributes (like ANXIETY and PEER_PRESSURE) are handled using probabilistic marginalization.

📈 Laplace smoothing ensures robust probability estimates.

🛑 Safe input handling for AGE and invalid entries.