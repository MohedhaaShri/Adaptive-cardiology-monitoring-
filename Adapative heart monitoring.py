import tkinter as tk
import pandas as pd
import winsound
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  # For image handling

# Load CSV
df = pd.read_csv("heart.csv")

# Parameters
params = ['cp', 'trtbps', 'chol', 'fbs', 'restecg', 'thalachh', 'exng', 'oldpeak', 'slp', 'caa', 'thall']
df = df[[col for col in params if col in df.columns]]

# Normal ranges for alert
normal_ranges = {
    'cp': (0, 3),
    'trtbps': (90, 140),
    'chol': (125, 200),
    'fbs': (0, 1),
    'restecg': (0, 2),
    'thalachh': (90, 200),
    'exng': (0, 1),
    'oldpeak': (0, 5),
    'slp': (0, 2),
    'caa': (0, 3),
    'thall': (1, 7)
}

# Category mappings
category_map = {
    'cp': {0: "Typical angina", 1: "Atypical angina", 2: "Non-anginal pain", 3: "Asymptomatic"},
    'fbs': {0: "<=120 mg/dL", 1: ">120 mg/dL"},
    'restecg': {0: "Normal", 1: "ST-T wave abnormality", 2: "Left ventricular hypertrophy"},
    'exng': {0: "No", 1: "Yes"},
    'slp': {0: "Upsloping", 1: "Flat", 2: "Downsloping"},
    'caa': {0: "0 vessels", 1: "1 vessel", 2: "2 vessels", 3: "3 vessels"},
    'thall': {3: "Normal", 6: "Fixed defect", 7: "Reversible defect"}
}

# Graph data
graph_data = {param: [] for param in params}
time_data = []

# Color coding
def get_color(value, low, high):
    if value < low:
        return "#FFD700"  # Yellow
    elif value > high:
        return "#FF4500"  # Red
    else:
        return "#32CD32"  # Green

# Feedback
def remedy_text(param, value):
    if param == 'chol':
        if value > normal_ranges['chol'][1]: return "High! Avoid fatty foods."
        elif value < normal_ranges['chol'][0]: return "Low! Eat balanced diet."
    if param == 'trtbps':
        if value > normal_ranges['trtbps'][1]: return "High BP! Relax."
        elif value < normal_ranges['trtbps'][0]: return "Low BP! Drink fluids."
    if param == 'thalachh':
        if value > normal_ranges['thalachh'][1]: return "High Heart Rate!"
        elif value < normal_ranges['thalachh'][0]: return "Low Heart Rate!"
    if param == 'oldpeak':
        if value > normal_ranges['oldpeak'][1]: return "High ST depression!"
    return ""

# GUI setup
root = tk.Tk()
root.title("Real-Time Heart Dashboard")
root.geometry("1400x950")
root.configure(bg="#f0f0f0")

# Time label
time_label = tk.Label(root, text="Time: --:--:--", font=("Helvetica", 16), bg="#f0f0f0", fg="red")
time_label.pack(side=tk.TOP, pady=5)

# Add PNG image below time
image_path = "logo1.png"  # Your image file
img = Image.open(image_path)
img = img.resize((200, 200), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)
image_label = tk.Label(root, image=photo, bg="#f0f0f0")
image_label.image = photo  # Keep reference
image_label.pack(side=tk.TOP, pady=5)

# Parameter cards
card_frame = tk.Frame(root, bg="#f0f0f0")
card_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

lbls = {}
feedbacks = {}
for i, param in enumerate(params):
    frame = tk.Frame(card_frame, bd=2, relief="ridge", padx=10, pady=5)
    frame.grid(row=i//4, column=i%4, padx=5, pady=5)
    lbl = tk.Label(frame, text=param.upper(), font=("Helvetica", 12), width=20, height=2, bg="#ddd")
    lbl.pack()
    fb = tk.Label(frame, text="", font=("Helvetica", 10), fg="blue")
    fb.pack()
    lbls[param] = lbl
    feedbacks[param] = fb

# Graphs setup
fig, axes_grid = plt.subplots(4, 3, figsize=(12,10))
plt.tight_layout(pad=3)
axes = axes_grid.flatten()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Real-time update
def update(index=0):
    if index >= len(df):
        index = 0  # loop back
    row = df.iloc[index]

    # Update current time
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.config(text=f"Time: {current_time}")

    for param in params:
        value = row[param]
        display_value = category_map[param].get(int(value), value) if param in category_map else value
        lbls[param]['text'] = f"{param.upper()}: {display_value}"
        lbls[param]['bg'] = get_color(float(value), *normal_ranges[param])
        feedbacks[param]['text'] = remedy_text(param, float(value))

        # Graph data (numeric only)
        try:
            graph_data[param].append(float(value))
        except:
            graph_data[param].append(0)
        if len(graph_data[param]) > 20:
            graph_data[param].pop(0)

    # Update graphs with numeric X-axis (0..19)
    for ax in axes:
        ax.cla()
    for i, param in enumerate(params):
        x_index = list(range(len(graph_data[param])))  # 0,1,2,...
        axes[i].plot(x_index, graph_data[param], marker='o', color='dodgerblue')
        axes[i].set_title(param.upper())
        axes[i].grid(True)
        axes[i].set_xticks(x_index)
        axes[i].set_xticklabels(x_index, fontsize=8)

    canvas.draw()

    # Alert beep for out-of-range
    for param in params:
        try:
            val_float = float(row[param])
            if val_float < normal_ranges[param][0] or val_float > normal_ranges[param][1]:
                winsound.Beep(1000, 200)
        except:
            pass

    # Call again after 1 second
    root.after(1000, update, index + 1)

update(0)
root.mainloop()
