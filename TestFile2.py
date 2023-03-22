"""""
Chat GPT Flashcards To Anki Converter

Created by Alex Toumayan, a self study project created at UC Berkeley during 2023.
Copyright (c) 2023 Alex Toumayan. All rights reserved.
"""

import re
import os
import tkinter as tk
from tkinter import filedialog
import genanki

def parse_chatgpt_output(text):
    cards = []
    fronts = re.findall(r'Front: (.*?)\n', text)
    backs = re.findall(r'Back: (.*?)\n', text)

    if len(fronts) != len(backs):
        raise ValueError("Mismatched fronts and backs count")

    for front, back in zip(fronts, backs):
        cards.append((front, back))

    return cards

def create_anki_deck(cards, output_file='output.apkg'):
    deck_name = os.path.splitext(os.path.basename(output_file))[0]

    my_model = genanki.Model(
        model_id=1607392319,
        name='Simple Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card',
                'qfmt': '{{Front}}',
                'afmt': '{{Front}}<hr id="answer">{{Back}}',
            },
        ])

    my_deck = genanki.Deck(deck_id=2059400110, name=deck_name)

    for front, back in cards:
        my_note = genanki.Note(model=my_model, fields=[front, back])
        my_deck.add_note(my_note)

    genanki.Package(my_deck).write_to_file(output_file)

def create_gui():
    def on_submit():
        chatgpt_output = text_input.get("1.0", "end-1c")

        try:
            cards = parse_chatgpt_output(chatgpt_output)
        except ValueError as e:
            status_label.config(text=f"Error: {e}")
            return

        if cards:
            output_file = filedialog.asksaveasfilename(defaultextension=".apkg", filetypes=[("Anki Package", "*.apkg")])
            if output_file:
                create_anki_deck(cards, output_file=output_file)
                status_label.config(text="Anki deck created successfully!")
        else:
            status_label.config(text="Invalid input. Please check the text and try again.")

    root = tk.Tk()
    root.title("ChatGPT Flashcards to Anki")

    text_input_label = tk.Label(root, text="Paste ChatGPT output here:")
    text_input_label.pack()

    text_input = tk.Text(root, wrap="word", width=60, height=20)
    text_input.pack()

    submit_button = tk.Button(root, text="Create Anki Deck", command=on_submit)
    submit_button.pack()

    status_label = tk.Label(root, text="")
    status_label.pack()

    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()
