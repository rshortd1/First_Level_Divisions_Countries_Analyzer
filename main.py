import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from shapely.geometry import Point
import tkinter as tk
from tkinter import ttk, colorchooser
import time

# Function to load data and update progress bar
def load_data(progress_bar, root):
    data_path = r"C:\Users\User\Desktop\Data\ne_10m_admin_1_states_provinces\ne_10m_admin_1_states_provinces.shp"

    steps = 10
    for step in range(steps):
        root.update_idletasks()
        progress_bar['value'] += 10
        time.sleep(0.1)

    global states_provinces
    states_provinces = gpd.read_file(data_path)[['geometry', 'name', 'admin']]
    states_provinces['color'] = 'cornflowerblue'  # Initialize with default color
    root.destroy()

root = tk.Tk()
root.title("Loading")

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=0, column=0, pady=10)

label = ttk.Label(frame, text="Loading data, please wait...")
label.grid(row=1, column=0)

root.after(100, load_data, progress_bar, root)
root.mainloop()

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
ax.set_facecolor('lightgoldenrodyellow')
states_provinces.plot(ax=ax, color=states_provinces['color'], edgecolor='black', alpha=0.7)

# Enhance the map appearance
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

clicked_text = ax.text(0.5, 1.01, '', transform=ax.transAxes, ha='center', fontsize=14, color='red', fontweight='bold')

current_color = 'cornflowerblue'
info_mode = False

def on_click(event):
    global current_color, info_mode, clicked_text
    if event.xdata is not None and event.ydata is not None:
        point = Point(event.xdata, event.ydata)
        for idx, row in states_provinces.iterrows():
            if row['geometry'].contains(point):
                if info_mode:
                    clicked_text.set_text(f"You clicked on {row['name']}, {row['admin']}")
                else:
                    states_provinces.at[idx, 'color'] = current_color

                # Store current zoom and pan settings
                curr_xlim = ax.get_xlim()
                curr_ylim = ax.get_ylim()

                ax.clear()  # Clear the axes
                ax.set_facecolor('lightgoldenrodyellow')
                states_provinces.plot(ax=ax, color=states_provinces['color'], edgecolor='black', alpha=0.7)
                ax.set_xlim(curr_xlim)
                ax.set_ylim(curr_ylim)
                clicked_text = ax.text(0.5, 1.01, clicked_text.get_text(), transform=ax.transAxes, ha='center', fontsize=14, color='red', fontweight='bold')

                # Enhance the map appearance
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.set_xticks([])
                ax.set_yticks([])

                fig.canvas.draw()
                break

cid = fig.canvas.mpl_connect('button_press_event', on_click)

def zoom_in(event):
    scale_factor = 1.2
    curr_xlim = ax.get_xlim()
    curr_ylim = ax.get_ylim()
    new_width = (curr_xlim[1] - curr_xlim[0]) / scale_factor
    new_height = (curr_ylim[1] - curr_ylim[0]) / scale_factor
    ax.set_xlim([curr_xlim[0] + new_width / 2, curr_xlim[1] - new_width / 2])
    ax.set_ylim([curr_ylim[0] + new_height / 2, curr_ylim[1] - new_height / 2])
    fig.canvas.draw()

def zoom_out(event):
    scale_factor = 1.2
    curr_xlim = ax.get_xlim()
    curr_ylim = ax.get_ylim()
    new_width = (curr_xlim[1] - curr_xlim[0]) * scale_factor
    new_height = (curr_ylim[1] - curr_ylim[0]) * scale_factor
    ax.set_xlim([curr_xlim[0] - new_width / 2, curr_xlim[1] + new_width / 2])
    ax.set_ylim([curr_ylim[0] - new_height / 2, curr_ylim[1] + new_height / 2])
    fig.canvas.draw()

button_width = 0.08
button_height = 0.05
axzoom_in = plt.axes([0.85, 0.92, button_width, button_height])
axzoom_out = plt.axes([0.85, 0.86, button_width, button_height])
btn_zoom_in = Button(axzoom_in, '+', color='white', hovercolor='skyblue')
btn_zoom_out = Button(axzoom_out, '-', color='white', hovercolor='skyblue')
btn_zoom_in.on_clicked(zoom_in)
btn_zoom_out.on_clicked(zoom_out)

def pick_color(event):
    global current_color, info_mode, clicked_text
    info_mode = False
    clicked_text.set_text("Info Mode: OFF")
    fig.canvas.draw()
    color = colorchooser.askcolor()[1]
    if color:
        current_color = color

axcolor_picker = plt.axes([0.85, 0.80, button_width, button_height])
btn_color_picker = Button(axcolor_picker, 'Pick Color', color='white', hovercolor='skyblue')
btn_color_picker.on_clicked(pick_color)

def toggle_info_mode(event):
    global info_mode, clicked_text
    info_mode = not info_mode
    if info_mode:
        clicked_text.set_text("Info Mode: ON")
    else:
        clicked_text.set_text("Info Mode: OFF")
    fig.canvas.draw()

axinfo_toggle = plt.axes([0.85, 0.74, button_width, button_height])
btn_info_toggle = Button(axinfo_toggle, 'Info Mode', color='white', hovercolor='skyblue')
btn_info_toggle.on_clicked(toggle_info_mode)

pan_start = None

def on_press(event):
    global pan_start
    if event.button == 1:
        pan_start = (event.x, event.y)

def on_release(event):
    global pan_start
    pan_start = None

def on_motion(event):
    global pan_start
    if pan_start is None:
        return
    dx = event.x - pan_start[0]
    dy = event.y - pan_start[1]
    curr_xlim = ax.get_xlim()
    curr_ylim = ax.get_ylim()
    scale_x = (curr_xlim[1] - curr_xlim[0]) / ax.bbox.width
    scale_y = (curr_ylim[1] - curr_ylim[0]) / ax.bbox.height
    ax.set_xlim(curr_xlim[0] - dx * scale_x, curr_xlim[1] - dx * scale_x)
    ax.set_ylim(curr_ylim[0] - dy * scale_y, curr_ylim[1] - dy * scale_y)
    pan_start = (event.x, event.y)
    fig.canvas.draw()

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

plt.show()
