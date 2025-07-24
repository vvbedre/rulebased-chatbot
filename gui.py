import sqlite3
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from collections import Counter

# Database setup
def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            question TEXT UNIQUE, 
            answer TEXT)"""
    )
    conn.commit()
    conn.close()

init_db()  # Initialize database

# Function to find the best matching response
def get_best_match(user_input):
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat")
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return "I'm sorry, I don't have an answer for that."

    user_terms = re.findall(r'\w+', user_input.lower())
    max_score = 0
    best_answer = "I'm sorry, I don't have an answer for that."

    for question, answer in data:
        question_terms = re.findall(r'\w+', question.lower())
        common_terms = Counter(user_terms) & Counter(question_terms)
        score = sum(common_terms.values())

        if score > max_score:
            max_score = score
            best_answer = answer

    return best_answer

# Function to get autocomplete suggestions
def get_suggestions(query):
    if not query:
        return []
    
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM chat WHERE question LIKE ?", (query + "%",))
    results = sorted([row[0] for row in cursor.fetchall()])
    conn.close()
    return results

# GUI setup
def update_suggestions(event):
    query = entry.get().strip()
    suggestions = get_suggestions(query)
    suggestion_list.delete(0, tk.END)
    for item in suggestions:
        suggestion_list.insert(tk.END, item)

def fill_entry(event):
    selected = suggestion_list.get(tk.ACTIVE)
    entry.delete(0, tk.END)
    entry.insert(tk.END, selected)
    suggestion_list.delete(0, tk.END)

def send_message():
    user_message = entry.get().strip()
    if user_message:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "You: " + user_message + "\n", "user")
        response = get_best_match(user_message)
        chat_window.insert(tk.END, "Bot: " + response + "\n", "bot")
        chat_window.config(state=tk.DISABLED)
        entry.delete(0, tk.END)
        suggestion_list.delete(0, tk.END)

# Creating main window
root = tk.Tk()
root.title("Chatbot GUI")
root.geometry("500x500")

# Chat display area
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_window.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
chat_window.tag_config("user", foreground="blue")
chat_window.tag_config("bot", foreground="green")

# Input field and send button frame
input_frame = tk.Frame(root)
input_frame.pack(pady=5, padx=10, fill=tk.X)

entry = tk.Entry(input_frame, width=50)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<KeyRelease>", update_suggestions)

send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5)

# Suggested questions listbox
suggestion_list = tk.Listbox(root, height=15, width=70)  # Increased size
suggestion_list.pack(pady=5)
suggestion_list.bind("<Double-Button-1>", fill_entry)

# Run the application
root.mainloop()
