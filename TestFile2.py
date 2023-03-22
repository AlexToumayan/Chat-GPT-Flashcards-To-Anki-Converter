import os
import re
import tempfile
import zipfile
from tkinter import *
from tkinter import filedialog
from genanki import Deck, Model, Note, Package

MODEL = Model(
    1607392319,
    "Simple Model",
    fields=[
        {"name": "Front"},
        {"name": "Back"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": "{{Front}}<hr id='answer'>{{Back}}",
        },
    ],
)

def parse_flashcards(text):
    flashcards = []
    for line in text.split('\n'):
        if ':' in line:
            front, back = [s.strip() for s in line.split(':', 1)]
            if front and back:
                flashcards.append((front, back))
    return flashcards

def create_anki_deck(flashcards, deck_name):
    deck = Deck(deck_id=os.urandom(8).hex(), name=deck_name)
    for front, back in flashcards:
        note = Note(model=MODEL, fields=[front, back])
        deck.add_note(note)
    return deck

def export_deck(deck, filename):
    package = Package(deck)
    package.write_to_file(filename)

def on_submit():
    text = input_text.get(1.0, END).strip()
    flashcards = parse_flashcards(text)
    if not flashcards:
        status_label.config(text="Please enter flashcards in the correct format.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".apkg", filetypes=[("Anki Package", "*.apkg")])
    if not filename:
        return
    deck_name = os.path.splitext(os.path.basename(filename))[0]
    deck = create_anki_deck(flashcards, deck_name)
    export_deck(deck, filename)
    status_label.config(text="Flashcards exported successfully!")

root = Tk()
root.title("Flashcard Generator")

Label(root, text="Enter Flashcards (Front: Back)").grid(row=0, column=0, padx=5, pady=5, sticky=W)
input_text = Text(root, wrap=WORD, width=60, height=10)
input_text.grid(row=0, column=1, padx=5, pady=5, sticky=W)

Button(root, text="Submit", command=on_submit).grid(row=1, column=1, padx=5, pady=5, sticky=E)
status_label = Label(root, text="")
status_label.grid(row=2, column=1, padx=5, pady=5, sticky=W)

root.mainloop()
