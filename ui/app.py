import sys
sys.path.append(".")
import tkinter as tk
from tkinter import messagebox
import threading
import time
from core.auth import register, login
from core.storage import save_password, get_password, list_labels, delete_password
from core.password_gen import generate_strong_password


class DataVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Data Vault")
        self.root.geometry("500x600")
        self.root.configure(bg="#1e1e2e")
        self.master_password = None
        self.show_login_screen()

    # ---------- Helpers ----------

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def label(self, text, size=12, bold=False):
        font = ("Helvetica", size, "bold" if bold else "normal")
        return tk.Label(self.root, text=text, bg="#1e1e2e",
                        fg="#cdd6f4", font=font)

    def entry(self, show=None):
        return tk.Entry(self.root, bg="#313244", fg="#cdd6f4",
                        insertbackground="white", font=("Helvetica", 11),
                        show=show)

    def button(self, text, command, color="#89b4fa"):
        return tk.Button(self.root, text=text, command=command,
                         bg=color, fg="#1e1e2e", font=("Helvetica", 11, "bold"),
                         relief="flat", padx=10, pady=5)

    # ---------- Login Screen ----------

    def show_login_screen(self):
        self.clear()

        self.label("🔐 Data Vault", size=20, bold=True).pack(pady=30)

        self.label("Master Password:").pack()
        self.pw_entry = self.entry(show="*")
        self.pw_entry.pack(pady=5, ipadx=5, ipady=5)

        self.button("Login", self.handle_login, "#a6e3a1").pack(pady=5)
        self.button("Register", self.handle_register, "#89b4fa").pack(pady=5)

    def handle_login(self):
        pw = self.pw_entry.get()
        if login(pw):
            self.master_password = pw
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Wrong password!")

    def handle_register(self):
        pw = self.pw_entry.get()
        if register(pw):
            messagebox.showinfo("Success", "Registered! Please login.")
        else:
            messagebox.showerror("Error", "User already registered!")

    # ---------- Main Screen ----------

    def show_main_screen(self):
        self.clear()

        self.label("🔐 Data Vault", size=20, bold=True).pack(pady=20)

        self.button("💾 Save Password", self.show_save_screen).pack(pady=5)
        self.button("🔑 Get Password", self.show_get_screen).pack(pady=5)
        self.button("📋 List Labels", self.show_labels).pack(pady=5)
        self.button("🗑️ Delete Password", self.show_delete_screen).pack(pady=5)
        self.button("⚡ Generate Password", self.show_generate_screen).pack(pady=5)
        self.button("🚪 Logout", self.show_login_screen, "#f38ba8").pack(pady=20)

    # ---------- Save ----------

    def show_save_screen(self):
        self.clear()
        self.label("💾 Save Password", size=16, bold=True).pack(pady=20)

        self.label("Label:").pack()
        label_entry = self.entry()
        label_entry.pack(pady=5, ipadx=5, ipady=5)

        self.label("Password:").pack()
        pw_entry = self.entry()
        pw_entry.pack(pady=5, ipadx=5, ipady=5)

        def save():
            save_password(self.master_password, label_entry.get(), pw_entry.get())
            messagebox.showinfo("Success", f"Password saved for '{label_entry.get()}'!")

        self.button("Save", save, "#a6e3a1").pack(pady=10)
        self.button("← Back", self.show_main_screen, "#585b70").pack()

    # ---------- Get ----------

    def show_get_screen(self):
        self.clear()
        self.label("🔑 Get Password", size=16, bold=True).pack(pady=20)

        self.label("Label:").pack()
        label_entry = self.entry()
        label_entry.pack(pady=5, ipadx=5, ipady=5)

        result_label = self.label("")
        result_label.pack(pady=10)

        def get():
            try:
                pwd = get_password(self.master_password, label_entry.get())
                result_label.config(text=f"🔑 {pwd}")

                def hide():
                    time.sleep(30)
                    result_label.config(text="🔒 Hidden")

                threading.Thread(target=hide, daemon=True).start()
            except KeyError:
                messagebox.showerror("Error", "Label not found!")

        self.button("Get", get, "#a6e3a1").pack(pady=5)
        self.button("← Back", self.show_main_screen, "#585b70").pack()

    # ---------- List ----------

    def show_labels(self):
        labels = list_labels()
        if labels:
            messagebox.showinfo("Labels", "\n".join(labels))
        else:
            messagebox.showinfo("Labels", "No passwords saved yet!")

    # ---------- Delete ----------

    def show_delete_screen(self):
        self.clear()
        self.label("🗑️ Delete Password", size=16, bold=True).pack(pady=20)

        self.label("Label:").pack()
        label_entry = self.entry()
        label_entry.pack(pady=5, ipadx=5, ipady=5)

        def delete():
            try:
                delete_password(label_entry.get())
                messagebox.showinfo("Success", "Deleted!")
            except KeyError:
                messagebox.showerror("Error", "Label not found!")

        self.button("Delete", delete, "#f38ba8").pack(pady=10)
        self.button("← Back", self.show_main_screen, "#585b70").pack()

    # ---------- Generate ----------

    def show_generate_screen(self):
        self.clear()
        self.label("⚡ Generate Password", size=16, bold=True).pack(pady=20)

        self.label("Length (default 16):").pack()
        len_entry = self.entry()
        len_entry.pack(pady=5, ipadx=5, ipady=5)

        result_label = self.label("")
        result_label.pack(pady=10)

        def generate():
            length = int(len_entry.get()) if len_entry.get() else 16
            pwd = generate_strong_password(length)
            result_label.config(text=pwd)

        self.button("Generate", generate, "#a6e3a1").pack(pady=5)
        self.button("← Back", self.show_main_screen, "#585b70").pack()


# ---------- Run ----------

if __name__ == "__main__":
    root = tk.Tk()
    app = DataVaultApp(root)
    root.mainloop()