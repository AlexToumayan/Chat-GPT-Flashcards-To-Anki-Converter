"""
Chat GPT Flashcards To Anki Converter
Created by Alex Toumayan, a self study project created at UC Berkeley during 2023.
Copyright (c) 2023 Alex Toumayan. All rights reserved.
"""

import re
import genanki
import os
import json
import csv
from tkinter import Tk, Label, Button, Text, filedialog, messagebox, Menu, Entry, OptionMenu, StringVar
from tkinter.ttk import Frame, Combobox
from pathlib import Path
from PIL import Image, ImageTk
import markdown2
import latex2mathml.converter
import io
import base64
from pydub import AudioSegment

def parse_flashcards(content):
    flashcard_formats = [
        r'(?i)(?:front(?:\s+of\s+card)?\s*:\s*(.+?))(?:(?:back(?:\s+of\s+card)?\s*:\s*(.+?))?(?=front(?:\s+of\s+card)?\s*:|\Z))',
    ]

    for format_regex in flashcard_formats:
        flashcards_raw = re.findall(format_regex, content, re.DOTALL)
        if flashcards_raw:
            break

    flashcards = []
    for front, back in flashcards_raw:
        front = front.strip()
        if back is None:
            back = ""
        else:
            back = back.strip()
        flashcards.append((front, back))

    return flashcards

def convert_images_latex_audio(front, back):
    front = markdown2.markdown(front, extras=["inline-images", "latex"])
    back = markdown2.markdown(back, extras=["inline-images", "latex"])

    front_mathml = re.findall(r'<span class="math">\$(.*?)\$', front)
    back_mathml = re.findall(r'<span class="math">\$(.*?)\$', back)

    for latex in front_mathml:
        mathml = latex2mathml.converter.convert(latex)
        front = front.replace(f'<span class="math">${latex}$', mathml)

    for latex in back_mathml:
        mathml = latex2mathml.converter.convert(latex)
        back = back.replace(f'<span class="math">${latex}$', mathml)

    front = re.sub(r'<img src="([^"]+)"', '<img src="{}\\1"', front)
    back = re.sub(r'<img src="([^"]+)"', '<img src="{}\\1"', back)

    front = front.replace("\n", "<br>")
    back = back.replace("\n", "<br>")

    def process_image_tag(match):
        img_path = match.group(1)
        try:
            with open(img_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{img_data}" />'
        except Exception as e:
            print(f"Error processing image: {e}")
            return ""

    def process_audio_tag(match):
        audio_path = match.group(1)
        try:
            audio = AudioSegment.from_file(audio_path)
            audio_data = io.BytesIO()
            audio.export(audio_data, format="mp3")
            audio_base64 = base64.b64encode(audio_data.getvalue()).decode("utf-8")
            return f'<audio controls><source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg"></audio>'
        except Exception as e:
            print(f"Error processing audio: {e}")
            return ""

    front = re.sub(r'\[img:([^]]+)\]', process_image_tag, front)
    back = re.sub(r'\[img:([^]]+)\]', process_image_tag, back)

    front = re.sub(r'\[audio:([^]]+)\]', process_audio_tag, front)
    back = re.sub(r'\[audio:([^]]+)\]', process_audio_tag, back)

    return front, back


def process_text(content, window, export_format):
    flashcards = parse_flashcards(content)

    if not flashcards:
        messagebox.showerror("Error", "Invalid format. Please follow the instructions and try again.", parent=window)
        return

    output_file = filedialog.asksaveasfilename(parent=window, defaultextension=f".{export_format}", title="Save Flashcard File")
    if not output_file:
        return

    deck_name = os.path.splitext(os.path.basename(output_file))[0]

    if export_format == 'apkg':
        export_to_apkg(flashcards, output_file, deck_name)
    elif export_format == 'csv':
        export_to_csv(flashcards, output_file)
    elif export_format == 'json':
        export_to_json(flashcards, output_file)

def export_to_apkg(flashcards, output_file, deck_name):
    model = genanki.Model(
        1607392319,
            'Enhanced Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ])

    deck = genanki.Deck(
        2059400110,
        deck_name)

    for front, back in flashcards:
        front, back = convert_images_latex_audio(front, back)
        note = genanki.Note(
            model=model,
            fields=[front, back])
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_file)

def export_to_csv(flashcards, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Front', 'Back'])
        for front, back in flashcards:
            csv_writer.writerow([front, back])

def export_to_json(flashcards, output_file):
    flashcards_json = [{"front": front, "back": back} for front, back in flashcards]
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(flashcards_json, jsonfile, ensure_ascii=False, indent=4)

def create_customization_frame(parent, text_widget):
    frame = Frame(parent)

    # Font size
    font_size_var = StringVar(frame)
    font_size_var.set("12")
    font_size_label = Label(frame, text="Font size:")
    font_size_label.pack(side="left", padx=(0, 5))
    font_size_combobox = Combobox(frame, textvariable=font_size_var, values=[str(x) for x in range(8, 25)], width=4)
    font_size_combobox.pack(side="left", padx=(0, 10))

    # Color scheme
    color_scheme_var = StringVar(frame)
    color_scheme_var.set("Default")
    color_scheme_label = Label(frame, text="Color scheme:")
    color_scheme_label.pack(side="left", padx=(0, 5))
    color_scheme_combobox = Combobox(frame, textvariable=color_scheme_var, values=["Default", "Dark", "Light"], width=10)
    color_scheme_combobox.pack(side="left", padx=(0, 10))

    # Update customization
    update_button = Button(frame, text="Update", command=lambda: update_text_widget_style(text_widget, font_size_var, color_scheme_var))
    update_button.pack(side="left")

    frame.pack(side="top", padx=10, pady=(0, 10))


def update_text_widget_style(text_widget, font_size_var, color_scheme_var):
    # Update font size
    font_size = int(font_size_var.get())
    text_widget.configure(font=("TkDefaultFont", font_size))

    # Update color scheme
    color_scheme = color_scheme_var.get()
    if color_scheme == "Default":
        text_widget.configure(bg="white", fg="black", insertbackground="black")
    elif color_scheme == "Dark":
        text_widget.configure(bg="#282c34", fg="#abb2bf", insertbackground="#abb2bf")
    elif color_scheme == "Light":
        text_widget.configure(bg="#f0f0f0", fg="#3c3c3c", insertbackground="#3c3c3c")


def create_gui():
    try:
        import pydub
    except ImportError:
        messagebox.showerror("Error", "pydub is not installed. Please install it by running `pip install pydub`.")
        return
    window = Tk()
    window.title('Chat GPT Flashcards To Anki Converter')

    frame = Frame(window)
    frame.pack(fill="both", expand=True)

    Label(frame, text='Paste your text here:').pack(side="top", anchor="w", padx=10, pady=10)

    text_widget = Text(frame, wrap='word', width=60, height=20)
    create_customization_frame(frame, text_widget)
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)

    context_menu = Menu(text_widget, tearoff=0)
    context_menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))

    def show_context_menu(event):
        if event.num == 3 or (event.num == 2 and window.tk.call("tk", "windowingsystem") == "aqua"):
            context_menu.tk_popup(event.x_root, event.y_root)

    text_widget.bind("<Button-2>", show_context_menu)
    text_widget.bind("<Button-3>", show_context_menu)

    export_format_var = StringVar(window)
    export_format_var.set("apkg")
    export_format_menu = OptionMenu(frame, export_format_var, "apkg", "csv", "json")
    export_format_menu.pack(side="bottom", pady=10)

    Button(frame, text='Convert', command=lambda: process_text(text_widget.get(1.0, "end-1c"), window, export_format_var.get())).pack(side="bottom", pady=10)

    instructions = (
        "Instructions:\n\n"
        "1. Use the following format for your text:\n"
        "   Front: Your question\n"
        "   Back: Your answer\n\n"
        "2. You can also use 'Front of card:' and 'Back of card:' as labels.\n\n"
        "Example:\n\n"
        "   Front of card: What is the capital of France?\n"
        "   Back of card: Paris"
    )

    Label(frame, text=instructions, justify="left").pack(side="bottom", anchor="w", padx=10, pady=10)

    window.mainloop()

if __name__ == '__main__':
    create_gui()


