"""""
Chat GPT Flashcards To Anki Converter

Created by Alex Toumayan, a self study project created at UC Berkeley during 2023.
Copyright (c) 2023 Alex Toumayan. All rights reserved.
"""

import re
import genanki
import os
from tkinter import Tk, Label, Button, Text, filedialog, messagebox, Menu
from tkinter.ttk import Frame

def parse_flashcards(content):
    flashcards_raw = re.findall(r'(?i)(?:front(?:\s+of\s+card)?\s*:\s*(.+?)(?:\s*back(?:\s+of\s+card)?\s*:\s*|(?=front(?:\s+of\s+card)?\s*:)))(?:back(?:\s+of\s+card)?\s*:\s*(.+?)(?=\s*front(?:\s+of\s+card)?\s*:|$))?', content, re.DOTALL)

    flashcards = []
    for front, back in flashcards_raw:
        front = front.strip()
        back = back.strip()
        flashcards.append((front, back))

    return flashcards

def process_text(content, window):
   flashcards = parse_flashcards(content)

   if not flashcards:
       messagebox.showerror("Error", "Invalid format. Please follow the instructions and try again.", parent=window)
       return

   output_file = filedialog.asksaveasfilename(parent=window, defaultextension=".apkg", title="Save Anki Package")
   if not output_file:
       return

   deck_name = os.path.splitext(os.path.basename(output_file))[0]
   export_to_apkg(flashcards, output_file, deck_name)

def export_to_apkg(flashcards, output_file, deck_name):
    model = genanki.Model(
        1607392319,
        'Simple Model',
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
        note = genanki.Note(
            model=model,
            fields=[front, back])
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_file)

def create_gui():
   window = Tk()
   window.title('Chat GPT Flashcards To Anki Converter')


   frame = Frame(window)
   frame.pack(fill="both", expand=True)


   Label(frame, text='Paste your text here:').pack(side="top", anchor="w", padx=10, pady=10)


   text_widget = Text(frame, wrap='word', width=60, height=20)
   text_widget.pack(fill="both", expand=True, padx=10, pady=10)


   # Create the right-click context menu for the text widget
   context_menu = Menu(text_widget, tearoff=0)
   context_menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
   context_menu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))


   def show_context_menu(event):
       # macOS uses Button-2 for right-click
       if event.num == 3 or (event.num == 2 and window.tk.call("tk", "windowingsystem") == "aqua"):
           context_menu.tk_popup(event.x_root, event.y_root)


   text_widget.bind("<Button-2>", show_context_menu)
   text_widget.bind("<Button-3>", show_context_menu)


   Button(frame, text='Convert', command=lambda: process_text(text_widget.get(1.0, "end-1c"), window)).pack(side="bottom", pady=10)


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
