import os
import tkinter as tk
from core.encryption import encrypt_with_key, decrypt_with_key, encrypt, decrypt
from core.password_gen import generate_strong_password
from core.storage import load_vault, save_vault
from core.auth import (
    hash_master_password,
    verify_master_password,
    build_recovery_secret,
    verify_recovery_answers,
    derive_recovery_secret,
    encrypt_vault_key,
    decrypt_vault_key,
)

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#22c55e"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 20, "bold")


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Vault")
        self.root.geometry("650x750")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.master_password = None
        self.vault_data = load_vault()
        self.vault_key = None
        self.current_frame = None
        self.setup_items = []

        if self.vault_data["auth"] is None or self.vault_data["encrypted_key_master"] is None:
            self.show_screen(self.create_setup_screen)
        else:
            self.show_screen(self.create_login_screen)

    def show_screen(self, screen_func):
        if self.current_frame:
            self.current_frame.destroy()

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        self.fade_in(frame)
        screen_func(frame)

    def fade_in(self, frame, alpha=0):
        alpha += 0.1
        if alpha <= 1:
            self.root.attributes("-alpha", alpha)
            self.root.after(20, lambda: self.fade_in(frame, alpha))
        else:
            self.root.attributes("-alpha", 1)

    def create_header(self, parent, title, back=None):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", pady=10, padx=20)

        if back:
            tk.Button(
                header,
                text="←",
                command=back,
                bg=BG,
                fg=TEXT,
                relief="flat",
                font=("Segoe UI", 14)
            ).pack(side="left")

        tk.Label(
            header,
            text=title,
            font=TITLE_FONT,
            fg=TEXT,
            bg=BG
        ).pack(side="left", padx=10)

    def create_login_screen(self, parent):
        container = tk.Frame(parent, bg=BG)
        container.pack(expand=True)

        tk.Label(
            container,
            text="Data Vault",
            font=TITLE_FONT,
            fg=TEXT,
            bg=BG
        ).pack(pady=40)

        card = tk.Frame(container, bg=CARD, padx=30, pady=30)
        card.pack()

        tk.Label(card, text="Master Password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.password_entry = tk.Entry(
            card,
            show="*",
            font=FONT,
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat"
        )
        self.password_entry.pack(fill="x", pady=15, ipady=8)

        self.login_message = tk.Label(card, text="", fg="#f87171", bg=CARD, font=("Segoe UI", 10))
        self.login_message.pack(anchor="w", pady=(0, 10))

        btn = tk.Button(
            card,
            text="Unlock Vault",
            bg=ACCENT,
            fg="black",
            relief="flat",
            command=self.handle_login
        )
        btn.pack(fill="x", pady=10, ipady=6)
        self.add_hover(btn)

        if self.vault_data.get("recovery"):
            forgot = tk.Button(
                card,
                text="Forgot Password?",
                bg="#334155",
                fg=TEXT,
                relief="flat",
                command=lambda: self.show_screen(self.create_forgot_password_screen)
            )
            forgot.pack(fill="x", ipady=6)
            self.add_hover(forgot)

    def create_setup_screen(self, parent):
        container = tk.Frame(parent, bg=BG)
        container.pack(expand=True)

        tk.Label(
            container,
            text="Setup Master Password",
            font=TITLE_FONT,
            fg=TEXT,
            bg=BG
        ).pack(pady=20)

        card = tk.Frame(container, bg=CARD, padx=30, pady=30)
        card.pack(fill="x", padx=20)

        tk.Label(card, text="Choose a strong master password.", fg=TEXT, bg=CARD, font=FONT).pack(anchor="w", pady=(0, 10))

        tk.Label(card, text="New password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.setup_master_entry = tk.Entry(
            card,
            show="*",
            font=FONT,
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat"
        )
        self.setup_master_entry.pack(fill="x", pady=10, ipady=8)

        tk.Label(card, text="Confirm password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.setup_confirm_entry = tk.Entry(
            card,
            show="*",
            font=FONT,
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat"
        )
        self.setup_confirm_entry.pack(fill="x", pady=10, ipady=8)

        tk.Label(card, text="Recovery questions", fg=MUTED, bg=CARD).pack(anchor="w", pady=(10, 0))
        tk.Label(card, text="Answer the three fixed questions below to recover your vault if you forget the password.", fg=MUTED, bg=CARD, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))

        self.setup_area = tk.Frame(card, bg=CARD)
        self.setup_area.pack(fill="x", pady=(0, 10))
        self.render_recovery_fields(card)

        self.setup_message = tk.Label(card, text="", fg="#f87171", bg=CARD, font=("Segoe UI", 10))
        self.setup_message.pack(anchor="w", pady=(0, 10))

        save_btn = tk.Button(
            card,
            text="Save Vault Setup",
            bg=ACCENT,
            fg="black",
            relief="flat",
            command=self.handle_setup
        )
        save_btn.pack(fill="x", ipady=6)
        self.add_hover(save_btn)

    def render_recovery_fields(self, parent):
        self.setup_items = []
        if hasattr(self, "setup_area"):
            self.setup_area.destroy()
        self.setup_area = tk.Frame(parent, bg=CARD)
        self.setup_area.pack(fill="x", pady=(0, 10))

        questions = [
            "Your first school name",
            "Your nickname",
            "Your favourite fruit"
        ]

        for idx, question_text in enumerate(questions):
            block = tk.Frame(self.setup_area, bg=CARD)
            block.pack(fill="x", pady=10)

            tk.Label(block, text=question_text, fg=MUTED, bg=CARD).pack(anchor="w")
            answer_entry = tk.Entry(block, font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
            answer_entry.pack(fill="x", pady=5)
            self.setup_items.append({"q": question_text, "a": answer_entry})

    def handle_setup(self):
        password = self.setup_master_entry.get().strip()
        confirm = self.setup_confirm_entry.get().strip()

        if not password or not confirm:
            self.set_setup_message("Please fill both password fields.")
            return
        if password != confirm:
            self.set_setup_message("Passwords do not match.")
            return

        questions = []
        recovery_answers = []

        for item in self.setup_items:
            questions.append(item["q"])
            answer = item["a"].get().strip()
            if not answer:
                self.set_setup_message("Please answer all recovery questions.")
                return
            recovery_answers.append(answer)

        recovery_data = {
            "mode": "text",
            "questions": questions,
            "answers": recovery_answers
        }

        vault_key = os.urandom(32)
        vault_key_hex = vault_key.hex()
        encrypted_key_master = encrypt_vault_key(password, vault_key_hex)
        recovery_secret = build_recovery_secret("text", recovery_answers)
        encrypted_key_recovery = encrypt_vault_key(recovery_secret, vault_key_hex)

        self.vault_data["auth"] = hash_master_password(password)
        self.vault_data["recovery"] = recovery_data
        self.vault_data["encrypted_key_master"] = encrypted_key_master
        self.vault_data["encrypted_key_recovery"] = encrypted_key_recovery
        self.vault_data["vault_key"] = None
        self.vault_key = vault_key
        save_vault(self.vault_data)

        self.master_password = password
        self.show_screen(self.create_dashboard)

    def set_setup_message(self, text):
        if hasattr(self, "setup_message"):
            self.setup_message.config(text=text)

    def set_login_message(self, text):
        if hasattr(self, "login_message"):
            self.login_message.config(text=text)

    def handle_login(self):
        pwd = self.password_entry.get().strip()
        if not pwd:
            self.set_login_message("Enter your master password.")
            return
        if self.vault_data["auth"] is None:
            self.set_login_message("Vault must be configured first.")
            return
        if not verify_master_password(pwd, self.vault_data["auth"]):
            self.set_login_message("Incorrect password. Try again.")
            return

        try:
            vault_key_hex = decrypt_vault_key(pwd, self.vault_data["encrypted_key_master"])
            self.vault_key = bytes.fromhex(vault_key_hex)
        except Exception:
            self.set_login_message("Unable to decrypt vault data.")
            return

        self.master_password = pwd
        self.show_screen(self.create_dashboard)

    def create_dashboard(self, parent):
        self.create_header(parent, "Dashboard")

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, pady=20)

        self.create_card(container, "Password Manager", self.create_passwords)
        self.create_card(container, "ENV Vault", self.open_env)
        self.create_card(container, "Settings", self.create_settings_screen)

    def create_card(self, parent, text, command):
        card = tk.Frame(parent, bg=CARD, padx=20, pady=20)
        card.pack(fill="x", padx=40, pady=15)

        tk.Label(card, text=text, fg=TEXT, bg=CARD, font=FONT).pack(side="left")

        btn = tk.Button(
            card,
            text="Open",
            command=lambda: self.show_screen(command),
            bg=ACCENT,
            fg="black",
            relief="flat"
        )
        btn.pack(side="right", ipady=4, ipadx=10)
        self.add_hover(btn)

    def create_passwords(self, parent):
        self.create_header(parent, "Passwords", back=lambda: self.show_screen(self.create_dashboard))

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True)

        form = tk.Frame(container, bg=CARD, padx=15, pady=15)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Site / service", fg=MUTED, bg=CARD).grid(row=0, column=0, sticky="w")
        self.site_entry = tk.Entry(form, font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.site_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10), ipady=8)

        tk.Label(form, text="Password / passphrase", fg=MUTED, bg=CARD).grid(row=0, column=1, sticky="w")
        self.pass_entry = tk.Entry(form, font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.pass_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10), ipady=8)

        tk.Label(form, text="Length", fg=MUTED, bg=CARD).grid(row=0, column=2, sticky="w")
        self.password_length_entry = tk.Entry(form, width=4, font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.password_length_entry.grid(row=1, column=2, sticky="w", padx=5, pady=(0, 10), ipady=8)
        self.password_length_entry.insert(0, "16")

        gen_btn = tk.Button(form, text="Generate", command=self.generate_password, bg="#2563eb", fg="white", relief="flat")
        gen_btn.grid(row=1, column=3, sticky="ew", padx=(0, 5), pady=(0, 10), ipady=8)
        self.add_hover(gen_btn)

        tk.Label(form, text="Hint: add a label and a strong password.", fg=MUTED, bg=CARD, font=("Segoe UI", 10)).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 10))

        save_btn = tk.Button(form, text="Save", command=self.save_password, bg=ACCENT, fg="black", relief="flat")
        save_btn.grid(row=3, column=0, columnspan=4, sticky="ew", ipady=6)
        self.add_hover(save_btn)

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.list_frame = tk.Frame(container, bg=CARD)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.vault_data = load_vault()
        passwords = self.vault_data.get("passwords", [])

        if not passwords:
            tk.Label(self.list_frame, text="No passwords yet 🔐", bg=CARD, fg=TEXT).pack(pady=20)
            return

        for idx, item in enumerate(passwords):
            self.create_item(self.list_frame, item, idx)

    def save_password(self):
        site = self.site_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not site or not password:
            return
        if self.vault_key is None:
            return

        encrypted = encrypt_with_key(self.vault_key, password)
        self.vault_data = load_vault()
        self.vault_data["passwords"].append({
            "site": site,
            "data": encrypted
        })
        save_vault(self.vault_data)

        self.site_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.refresh_list()

    def generate_password(self):
        length_text = self.password_length_entry.get().strip()
        try:
            length = int(length_text)
            if length < 8:
                length = 8
        except ValueError:
            length = 16
        generated = generate_strong_password(length)
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.insert(0, generated)

    def delete_password(self, index):
        self.vault_data = load_vault()
        passwords = self.vault_data.get("passwords", [])
        if 0 <= index < len(passwords):
            del passwords[index]
            self.vault_data["passwords"] = passwords
            save_vault(self.vault_data)
            self.refresh_list()

    def create_item(self, parent, item, index):
        row = tk.Frame(parent, bg=CARD, pady=8)
        row.pack(fill="x", padx=10)

        tk.Label(row, text=item["site"], fg=TEXT, bg=CARD).pack(side="left")

        value_label = tk.Label(row, text="********", fg=MUTED, bg=CARD)
        value_label.pack(side="left", padx=10)

        is_hidden = True

        def hide_value():
            nonlocal is_hidden
            value_label.config(text="********")
            show_button.config(text="Show")
            is_hidden = True

        def toggle_password():
            nonlocal is_hidden
            if is_hidden:
                try:
                    decrypted = decrypt_with_key(self.vault_key, item["data"])
                    value_label.config(text=decrypted)
                    show_button.config(text="Hide")
                    is_hidden = False
                except Exception:
                    value_label.config(text="Error")
            else:
                hide_value()

        show_button = tk.Button(row, text="Show", command=toggle_password, bg=ACCENT, fg="black", relief="flat")
        show_button.pack(side="right", padx=(0, 4))
        self.add_hover(show_button)

        delete_button = tk.Button(row, text="Delete", command=lambda: self.delete_password(index), bg="#ef4444", fg="white", relief="flat")
        delete_button.pack(side="right")
        self.add_hover(delete_button)

    def open_env(self, parent):
        self.create_header(parent, "ENV Vault", back=lambda: self.show_screen(self.create_dashboard))
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True)
        tk.Label(container, text="ENV Vault is not available yet.", fg=TEXT, bg=BG, font=FONT).pack(pady=20)

    def create_settings_screen(self, parent):
        self.create_header(parent, "Settings", back=lambda: self.show_screen(self.create_dashboard))

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, pady=20)

        card = tk.Frame(container, bg=CARD, padx=20, pady=20)
        card.pack(fill="x", padx=40, pady=10)

        tk.Label(card, text="Master password recovery is configured.", fg=TEXT, bg=CARD, font=FONT).pack(anchor="w", pady=(0, 15))
        tk.Button(card, text="Reset Master Password", bg=ACCENT, fg="black", relief="flat", command=lambda: self.show_screen(self.create_password_change_screen)).pack(fill="x", ipady=6)
        self.add_hover(card.winfo_children()[-1])

        tk.Button(card, text="Logout", bg="#334155", fg=TEXT, relief="flat", command=lambda: self.show_screen(self.create_login_screen)).pack(fill="x", pady=10, ipady=6)
        self.add_hover(card.winfo_children()[-1])

    def create_password_change_screen(self, parent):
        self.create_header(parent, "Change Master Password", back=lambda: self.show_screen(self.create_settings_screen))

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, pady=20)
        card = tk.Frame(container, bg=CARD, padx=30, pady=30)
        card.pack(fill="x", padx=20)

        tk.Label(card, text="Current password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.current_password_entry = tk.Entry(card, show="*", font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.current_password_entry.pack(fill="x", pady=10, ipady=8)

        tk.Label(card, text="New password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.new_password_entry = tk.Entry(card, show="*", font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.new_password_entry.pack(fill="x", pady=10, ipady=8)

        tk.Label(card, text="Confirm new password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.confirm_new_password_entry = tk.Entry(card, show="*", font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.confirm_new_password_entry.pack(fill="x", pady=10, ipady=8)

        self.reset_message = tk.Label(card, text="", fg="#f87171", bg=CARD, font=("Segoe UI", 10))
        self.reset_message.pack(anchor="w", pady=(0, 10))

        tk.Button(card, text="Apply New Password", bg=ACCENT, fg="black", relief="flat", command=self.handle_password_change).pack(fill="x", ipady=6)
        self.add_hover(card.winfo_children()[-1])

    def handle_password_change(self):
        current = self.current_password_entry.get().strip()
        new = self.new_password_entry.get().strip()
        confirm = self.confirm_new_password_entry.get().strip()

        if not current or not new or not confirm:
            self.set_reset_message("Please fill all fields.")
            return
        if new != confirm:
            self.set_reset_message("New passwords do not match.")
            return
        if not verify_master_password(current, self.vault_data["auth"]):
            self.set_reset_message("Current password is incorrect.")
            return

        try:
            vault_key_hex = decrypt_vault_key(current, self.vault_data["encrypted_key_master"])
            self.vault_key = bytes.fromhex(vault_key_hex)
        except Exception:
            self.set_reset_message("Unable to decrypt vault key.")
            return

        self.vault_data["auth"] = hash_master_password(new)
        self.vault_data["encrypted_key_master"] = encrypt_vault_key(new, self.vault_key.hex())
        save_vault(self.vault_data)
        self.set_reset_message("Master password updated successfully.")

    def set_reset_message(self, text):
        if hasattr(self, "reset_message"):
            self.reset_message.config(text=text)

    def create_forgot_password_screen(self, parent):
        self.create_header(parent, "Recover Vault", back=lambda: self.show_screen(self.create_login_screen))

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, pady=20)

        if not self.vault_data.get("recovery"):
            tk.Label(container, text="No recovery questions are configured.", fg=TEXT, bg=BG, font=FONT).pack(pady=20)
            return

        self.recovery_entries = []
        recovery = self.vault_data["recovery"]
        tk.Label(container, text="Answer the recovery questions below.", fg=TEXT, bg=BG, font=FONT).pack(pady=(0, 15))
        form = tk.Frame(container, bg=CARD, padx=20, pady=20)
        form.pack(fill="x", padx=20)

        if recovery["mode"] == "text":
            for idx, question in enumerate(recovery["questions"]):
                tk.Label(form, text=question, fg=TEXT, bg=CARD).pack(anchor="w", pady=(10, 0))
                entry = tk.Entry(form, font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
                entry.pack(fill="x", pady=5)
                self.recovery_entries.append(entry)
        else:
            for idx, question in enumerate(recovery["questions"]):
                tk.Label(form, text=question, fg=TEXT, bg=CARD).pack(anchor="w", pady=(10, 0))
                selected = tk.StringVar(value="0")
                options = recovery.get("options", [])[idx]
                for opt_index, opt_text in enumerate(options):
                    tk.Radiobutton(
                        form,
                        text=opt_text,
                        variable=selected,
                        value=str(opt_index),
                        bg=CARD,
                        fg=TEXT,
                        selectcolor="#0f172a",
                        activebackground=CARD,
                        anchor="w",
                        justify="left",
                        relief="flat"
                    ).pack(fill="x", padx=10)
                self.recovery_entries.append(selected)

        self.recovery_message = tk.Label(form, text="", fg="#f87171", bg=CARD, font=("Segoe UI", 10))
        self.recovery_message.pack(anchor="w", pady=(10, 0))

        verify_btn = tk.Button(form, text="Verify Answers", bg=ACCENT, fg="black", relief="flat", command=self.handle_recovery_verify)
        verify_btn.pack(fill="x", pady=15, ipady=6)
        self.add_hover(verify_btn)

    def handle_recovery_verify(self):
        recovery = self.vault_data["recovery"]
        answers = []
        secret_values = []

        if recovery["mode"] == "text":
            for entry in self.recovery_entries:
                answer = entry.get().strip()
                if not answer:
                    self.recovery_message.config(text="Please answer every question.")
                    return
                answers.append(answer)
                secret_values.append(answer)
        else:
            for selected in self.recovery_entries:
                answers.append(selected.get())
                secret_values.append(recovery["options"][len(answers) - 1][int(selected.get())])

        if not verify_recovery_answers(recovery, answers):
            self.recovery_message.config(text="One or more answers are incorrect.")
            return

        try:
            recovery_secret = build_recovery_secret(recovery["mode"], secret_values)
            vault_key_hex = decrypt_vault_key(recovery_secret, self.vault_data["encrypted_key_recovery"])
            self.vault_key = bytes.fromhex(vault_key_hex)
        except Exception:
            self.recovery_message.config(text="Recovery failed. Please check your answers.")
            return

        self.show_screen(self.create_recovery_reset_screen)

    def create_recovery_reset_screen(self, parent):
        self.create_header(parent, "Reset Master Password", back=lambda: self.show_screen(self.create_login_screen))

        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True, pady=20)
        card = tk.Frame(container, bg=CARD, padx=30, pady=30)
        card.pack(fill="x", padx=20)

        tk.Label(card, text="New password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.recovery_new_entry = tk.Entry(card, show="*", font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.recovery_new_entry.pack(fill="x", pady=10, ipady=8)

        tk.Label(card, text="Confirm password", fg=MUTED, bg=CARD).pack(anchor="w")
        self.recovery_confirm_entry = tk.Entry(card, show="*", font=FONT, bg="#020617", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.recovery_confirm_entry.pack(fill="x", pady=10, ipady=8)

        self.recovery_reset_message = tk.Label(card, text="", fg="#f87171", bg=CARD, font=("Segoe UI", 10))
        self.recovery_reset_message.pack(anchor="w", pady=(0, 10))

        tk.Button(card, text="Save New Password", bg=ACCENT, fg="black", relief="flat", command=self.handle_recovery_reset).pack(fill="x", ipady=6)
        self.add_hover(card.winfo_children()[-1])

    def handle_recovery_reset(self):
        new_password = self.recovery_new_entry.get().strip()
        confirm = self.recovery_confirm_entry.get().strip()

        if not new_password or not confirm:
            self.recovery_reset_message.config(text="Please fill both password fields.")
            return
        if new_password != confirm:
            self.recovery_reset_message.config(text="Passwords do not match.")
            return

        self.vault_data["auth"] = hash_master_password(new_password)
        self.vault_data["encrypted_key_master"] = encrypt_vault_key(new_password, self.vault_key.hex())
        save_vault(self.vault_data)
        self.recovery_reset_message.config(text="Password reset successful. Please login.")

    def add_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg="#16a34a"))
        widget.bind("<Leave>", lambda e: widget.config(bg=ACCENT))

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
