import sys
sys.path.append(".")
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import math
from core.auth import register, login
from core.storage import save_password, get_password, list_labels, delete_password
from core.password_gen import generate_strong_password

BG       = "#080810"
CARD     = "#0e0e1c"
BORDER   = "#1a1a2e"
ACCENT   = "#00d4ff"
ACCENT2  = "#7c3aed"
SUCCESS  = "#00ff88"
DANGER   = "#ff4757"
WARNING  = "#ffa502"
TEXT     = "#e2e8f0"
SUBTEXT  = "#64748b"
ENTRY_BG = "#0a0a18"


def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,  extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,   extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="pieslice", **kwargs)
    canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
    canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)


def password_strength(pw):
    score = 0
    if len(pw) >= 8:  score += 1
    if len(pw) >= 12: score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c.islower() for c in pw): score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in pw): score += 1
    if score <= 2: return score, "WEAK",   DANGER
    if score <= 4: return score, "MEDIUM", WARNING
    return score,               "STRONG", SUCCESS


class ParticleCanvas(tk.Canvas):
    def __init__(self, parent, width, height):
        super().__init__(parent, width=width, height=height,
                         bg=BG, highlightthickness=0)
        self.w = width
        self.h = height
        self.particles = [{
            "x": random.uniform(0, width),
            "y": random.uniform(0, height),
            "vx": random.uniform(-0.4, 0.4),
            "vy": random.uniform(-0.4, 0.4),
            "r": random.uniform(1, 2.5),
        } for _ in range(40)]
        self._animate()

    def _animate(self):
        self.delete("particle")
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0 or p["x"] > self.w: p["vx"] *= -1
            if p["y"] < 0 or p["y"] > self.h: p["vy"] *= -1
            for q in self.particles:
                dist = math.hypot(p["x"]-q["x"], p["y"]-q["y"])
                if dist < 80:
                    a = int(255*(1-dist/80)*0.3)
                    col = f"#{a:02x}{min(a+50,255):02x}{min(a+80,255):02x}"
                    self.create_line(p["x"], p["y"], q["x"], q["y"],
                                     fill=col, tags="particle")
            r = p["r"]
            self.create_oval(p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r,
                             fill=ACCENT, outline="", tags="particle")
        self.after(30, self._animate)


class PulsingTitle(tk.Canvas):
    def __init__(self, parent, text, width=420, height=60):
        super().__init__(parent, width=width, height=height,
                         bg=BG, highlightthickness=0)
        self.text = text
        self.w = width
        self.h = height
        self.t = 0
        self._animate()

    def _animate(self):
        self.delete("all")
        self.t += 0.05
        glow = int(180 + 75 * math.sin(self.t))
        color = f"#{glow:02x}{min(glow+40,255):02x}ff"
        for offset in [4, 3, 2, 1]:
            a = 40 + offset * 15
            sc = f"#00{a:02x}{min(a+80,255):02x}"
            self.create_text(self.w//2+offset, self.h//2+offset,
                             text=self.text, fill=sc,
                             font=("Courier New", 24, "bold"))
        self.create_text(self.w//2, self.h//2, text=self.text,
                         fill=color, font=("Courier New", 24, "bold"))
        self.after(50, self._animate)


class TypingLabel(tk.Canvas):
    def __init__(self, parent, text, width=420, height=25):
        super().__init__(parent, width=width, height=height,
                         bg=BG, highlightthickness=0)
        self.full_text = text
        self.current = 0
        self.w = width
        self.h = height
        self.cursor_visible = True
        self._type()

    def _type(self):
        self.delete("all")
        shown = self.full_text[:self.current]
        cursor = "█" if self.cursor_visible else " "
        self.create_text(self.w//2, self.h//2, text=shown+cursor,
                         fill=SUBTEXT, font=("Courier New", 8))
        if self.current < len(self.full_text):
            self.current += 1
            self.after(80, self._type)
        else:
            self.cursor_visible = not self.cursor_visible
            self.after(500, self._blink)

    def _blink(self):
        self.delete("all")
        cursor = "█" if self.cursor_visible else " "
        self.create_text(self.w//2, self.h//2,
                         text=self.full_text+cursor,
                         fill=SUBTEXT, font=("Courier New", 8))
        self.cursor_visible = not self.cursor_visible
        self.after(500, self._blink)


class GlowButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 color=ACCENT, width=320, height=44):
        super().__init__(parent, width=width, height=height,
                         bg=BG, highlightthickness=0, cursor="hand2")
        self.command = command
        self.color = color
        self.text = text
        self.w = width
        self.h = height
        self._draw(color)
        self.bind("<Enter>",    self._hover)
        self.bind("<Leave>",    self._leave)
        self.bind("<Button-1>", lambda e: command())

    def _draw(self, color):
        self.delete("all")
        rounded_rect(self, 2, 2, self.w-2, self.h-2, 8,
                     fill=color, outline="")
        self.create_text(self.w//2, self.h//2, text=self.text,
                         fill=BG, font=("Courier New", 11, "bold"))

    def _hover(self, e):
        self.delete("all")
        for i in range(3, 0, -1):
            rounded_rect(self, 2-i, 2-i, self.w-2+i, self.h-2+i, 8+i,
                         fill=self.color, outline="")
        self.create_text(self.w//2, self.h//2, text=self.text,
                         fill=BG, font=("Courier New", 11, "bold"))

    def _leave(self, e):
        self._draw(self.color)


class GlowEntry(tk.Canvas):
    def __init__(self, parent, show=None, width=320):
        super().__init__(parent, width=width, height=44,
                         bg=BG, highlightthickness=0)
        self.w = width
        self.show_char = show
        self.entry = tk.Entry(self, bg=ENTRY_BG, fg=TEXT,
                              insertbackground=ACCENT,
                              font=("Courier New", 11),
                              relief="flat", show=show,
                              highlightthickness=0, bd=0)
        self.create_window(width//2, 22, window=self.entry,
                           width=width-20, height=28)
        self._draw_border(BORDER)
        self.entry.bind("<FocusIn>",
                        lambda e: self._draw_border(ACCENT))
        self.entry.bind("<FocusOut>",
                        lambda e: self._draw_border(BORDER))

    def _draw_border(self, color):
        self.delete("border")
        rounded_rect(self, 1, 1, self.w-1, 43, 6,
                     fill=ENTRY_BG, outline=color, tags="border")
        self.tag_raise("border")
        self.entry.lift()

    def get(self):
        return self.entry.get()

    def toggle_show(self):
        if self.entry.cget("show") == "":
            self.entry.config(show="●")
        else:
            self.entry.config(show="")


class StrengthMeter(tk.Canvas):
    def __init__(self, parent, width=320):
        super().__init__(parent, width=width, height=28,
                         bg=BG, highlightthickness=0)
        self.w = width
        self._update("")

    def _update(self, pw):
        self.delete("all")
        if not pw:
            return
        score, label, color = password_strength(pw)
        bar_w = int((self.w - 20) * score / 6)
        # Background bar
        rounded_rect(self, 0, 8, self.w-80, 20, 4,
                     fill=BORDER, outline="")
        # Filled bar
        if bar_w > 0:
            rounded_rect(self, 0, 8, bar_w, 20, 4,
                         fill=color, outline="")
        self.create_text(self.w-35, 14, text=label,
                         fill=color, font=("Courier New", 8, "bold"))

    def attach(self, entry_widget):
        entry_widget.entry.bind(
            "<KeyRelease>",
            lambda e: self._update(entry_widget.get())
        )


class DataVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Vault")
        self.root.geometry("460x700")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.master_password = None
        self.last_activity = time.time()
        self.show_login_screen()

    def reset_timer(self, event=None):
        self.last_activity = time.time()

    def start_auto_lock(self):
        def check():
            while self.master_password:
                if time.time() - self.last_activity > 120:
                    self.master_password = None
                    self.root.after(0, self._lock)
                    return
                time.sleep(5)
        threading.Thread(target=check, daemon=True).start()

    def _lock(self):
        messagebox.showwarning("Auto-Lock",
            "Session locked due to inactivity!")
        self.show_login_screen()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.bind("<Motion>", self.reset_timer)
        self.root.bind("<Key>",    self.reset_timer)

    def lbl(self, text, size=11, bold=False, color=TEXT):
        return tk.Label(self.root, text=text, bg=BG,
                        fg=color, font=("Courier New", size,
                        "bold" if bold else "normal"))

    def gap(self, h=10):
        tk.Frame(self.root, bg=BG, height=h).pack()

    def divider(self):
        c = tk.Canvas(self.root, width=380, height=1,
                      bg=BG, highlightthickness=0)
        c.create_line(0, 0, 380, 0, fill=BORDER, width=1)
        c.pack(pady=10)

    # ── Login ─────────────────────────────────────────────
    def show_login_screen(self):
        self.clear()
        p = ParticleCanvas(self.root, 460, 700)
        p.place(x=0, y=0)
        self.gap(25)
        PulsingTitle(self.root, "DATA VAULT").pack()
        TypingLabel(self.root,
                    "SECURE OFFLINE PASSWORD MANAGER").pack()
        self.divider()
        self.lbl("MASTER PASSWORD", size=9, color=SUBTEXT).pack()
        self.gap(6)

        pw_frame = tk.Frame(self.root, bg=BG)
        pw_frame.pack()
        self.pw_entry = GlowEntry(pw_frame, show="●", width=270)
        self.pw_entry.pack(side="left")

        # Show/hide toggle
        self.eye_btn = tk.Button(pw_frame, text="👁",
                                  bg=CARD, fg=SUBTEXT,
                                  font=("Courier New", 12),
                                  relief="flat", cursor="hand2",
                                  command=self._toggle_pw)
        self.eye_btn.pack(side="left", padx=5)

        self.gap(20)
        GlowButton(self.root, "▶  LOGIN",
                   self.handle_login, SUCCESS).pack()
        self.gap(8)
        GlowButton(self.root, "+  REGISTER",
                   self.handle_register, ACCENT).pack()
        self.divider()
        self.lbl("OFFLINE  •  AES-256-GCM  •  ZERO CLOUD",
                 size=8, color=SUBTEXT).pack()

    def _toggle_pw(self):
        self.pw_entry.toggle_show()

    def handle_login(self):
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showerror("Error", "Enter password!")
            return
        if login(pw):
            self.master_password = pw
            self.last_activity = time.time()
            self.start_auto_lock()
            self.show_main_screen()
        else:
            messagebox.showerror("Access Denied", "Wrong password!")

    def handle_register(self):
        pw = self.pw_entry.get()
        if not pw or len(pw) < 8:
            messagebox.showerror("Error", "Min 8 characters!")
            return
        if register(pw):
            messagebox.showinfo("Done", "Registered! Login now.")
        else:
            messagebox.showerror("Error", "Already registered!")

    # ── Main ──────────────────────────────────────────────
    def show_main_screen(self):
        self.clear()
        self.gap(20)
        PulsingTitle(self.root, "DATA VAULT").pack()

        # Vault stats
        count = len(list_labels())
        stats = tk.Canvas(self.root, width=420, height=30,
                          bg=BG, highlightthickness=0)
        stats.create_text(210, 10,
                          text=f"● VAULT UNLOCKED  │  {count} PASSWORDS STORED",
                          fill=SUCCESS, font=("Courier New", 8))
        stats.pack()

        self.divider()

        # Search bar
        self.lbl("🔍 SEARCH LABELS", size=9, color=SUBTEXT).pack()
        self.gap(4)
        search_entry = GlowEntry(self.root, width=320)
        search_entry.pack()
        self.gap(5)

        result_lbl = self.lbl("", size=9, color=ACCENT)
        result_lbl.pack()
        self.gap(5)

        def do_search():
            q = search_entry.get().lower()
            matches = [l for l in list_labels() if q in l.lower()]
            if matches:
                result_lbl.config(
                    text="Found: " + "  •  ".join(matches))
            else:
                result_lbl.config(text="No matches found")

        search_entry.entry.bind("<KeyRelease>",
                                lambda e: do_search())

        self.divider()

        btns = [
            ("💾  SAVE PASSWORD",     self.show_save,     ACCENT),
            ("🔑  GET PASSWORD",      self.show_get,      "#00b4d8"),
            ("📋  LIST ALL LABELS",   self.show_labels,   ACCENT2),
            ("🗑   DELETE PASSWORD",  self.show_delete,   DANGER),
            ("⚡  GENERATE PASSWORD", self.show_generate, WARNING),
        ]
        for txt, cmd, col in btns:
            GlowButton(self.root, txt, cmd, col).pack(pady=4)

        self.divider()
        GlowButton(self.root, "⏻  LOGOUT",
                   self.show_login_screen, SUBTEXT, width=160).pack()

    # ── Save ──────────────────────────────────────────────
    def show_save(self):
        self.clear()
        self.gap(25)
        self.lbl("SAVE PASSWORD", 16, bold=True,
                 color=ACCENT).pack()
        self.divider()
        self.lbl("LABEL", 9, color=SUBTEXT).pack()
        self.gap(5)
        le = GlowEntry(self.root)
        le.pack()
        self.gap(12)
        self.lbl("PASSWORD", 9, color=SUBTEXT).pack()
        self.gap(5)

        pw_frame = tk.Frame(self.root, bg=BG)
        pw_frame.pack()
        pe = GlowEntry(pw_frame, width=270)
        pe.pack(side="left")
        tk.Button(pw_frame, text="👁", bg=CARD, fg=SUBTEXT,
                  font=("Courier New", 12), relief="flat",
                  cursor="hand2",
                  command=pe.toggle_show).pack(side="left", padx=5)

        self.gap(6)
        meter = StrengthMeter(self.root)
        meter.pack()
        meter.attach(pe)
        self.gap(14)

        def save():
            if not le.get() or not pe.get():
                messagebox.showerror("Error", "Fill all fields!")
                return
            save_password(self.master_password, le.get(), pe.get())
            messagebox.showinfo("Saved", f"'{le.get()}' saved!")

        GlowButton(self.root, "💾  SAVE", save, SUCCESS).pack()
        self.gap(8)
        GlowButton(self.root, "←  BACK",
                   self.show_main_screen, SUBTEXT, width=160).pack()

    # ── Get ───────────────────────────────────────────────
    def show_get(self):
        self.clear()
        self.gap(25)
        self.lbl("GET PASSWORD", 16, bold=True,
                 color="#00b4d8").pack()
        self.divider()
        self.lbl("LABEL", 9, color=SUBTEXT).pack()
        self.gap(5)
        le = GlowEntry(self.root)
        le.pack()
        self.gap(15)

        result = tk.Label(self.root, text="", bg=CARD,
                          fg=SUCCESS, font=("Courier New", 11),
                          width=35, pady=10)
        result.pack()
        timer_lbl = self.lbl("", 8, color=SUBTEXT)
        timer_lbl.pack(pady=4)

        def get():
            try:
                pwd = get_password(self.master_password, le.get())
                result.config(text=pwd)

                def countdown(s):
                    for i in range(s, 0, -1):
                        timer_lbl.config(text=f"Auto-hide in {i}s")
                        time.sleep(1)
                    result.config(text="")
                    timer_lbl.config(text="")

                threading.Thread(target=countdown,
                                 args=(30,), daemon=True).start()
            except KeyError:
                messagebox.showerror("Error", "Label not found!")

        GlowButton(self.root, "🔑  RETRIEVE",
                   get, "#00b4d8").pack(pady=5)
        GlowButton(self.root, "←  BACK",
                   self.show_main_screen, SUBTEXT, width=160).pack()

    # ── Labels ────────────────────────────────────────────
    def show_labels(self):
        labels = list_labels()
        if labels:
            messagebox.showinfo("Vault Labels",
                               "\n".join(f"  • {l}" for l in labels))
        else:
            messagebox.showinfo("Empty", "No passwords saved yet!")

    # ── Delete ────────────────────────────────────────────
    def show_delete(self):
        self.clear()
        self.gap(25)
        self.lbl("DELETE PASSWORD", 16, bold=True,
                 color=DANGER).pack()
        self.divider()
        self.lbl("LABEL", 9, color=SUBTEXT).pack()
        self.gap(5)
        le = GlowEntry(self.root)
        le.pack()
        self.gap(20)

        def delete():
            if not le.get():
                messagebox.showerror("Error", "Enter label!")
                return
            if messagebox.askyesno("Confirm",
                    f"Delete '{le.get()}'? Cannot be undone."):
                try:
                    delete_password(le.get())
                    messagebox.showinfo("Deleted", "Removed!")
                except KeyError:
                    messagebox.showerror("Error", "Not found!")

        GlowButton(self.root, "🗑  DELETE", delete, DANGER).pack()
        self.gap(8)
        GlowButton(self.root, "←  BACK",
                   self.show_main_screen, SUBTEXT, width=160).pack()

    # ── Generate ──────────────────────────────────────────
    def show_generate(self):
        self.clear()
        self.gap(25)
        self.lbl("GENERATE PASSWORD", 16, bold=True,
                 color=WARNING).pack()
        self.divider()
        self.lbl("LENGTH (default 16)", 9, color=SUBTEXT).pack()
        self.gap(5)
        le = GlowEntry(self.root, width=160)
        le.pack()
        self.gap(15)

        result = tk.Label(self.root, text="", bg=CARD,
                          fg=SUCCESS, font=("Courier New", 10),
                          width=38, pady=10, wraplength=360)
        result.pack()

        meter = StrengthMeter(self.root)
        meter.pack()
        self.gap(10)

        def generate():
            length = int(le.get()) if le.get() else 16
            pwd = generate_strong_password(length)
            result.config(text=pwd)
            meter._update(pwd)

        GlowButton(self.root, "⚡  GENERATE",
                   generate, WARNING).pack(pady=5)
        GlowButton(self.root, "←  BACK",
                   self.show_main_screen, SUBTEXT, width=160).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVaultApp(root)
    root.mainloop()