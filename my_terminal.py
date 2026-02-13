#!/usr/bin/env python3
# ==============================================================================
# H3V3N TERMINAL v12.6 - FINAL STABLE (FIXED SHORTCUTS & CONTEXT MENU)
# ==============================================================================

import gi
import os
import json
import psutil
import random
import platform
from datetime import datetime

gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, Gdk, Pango, GLib, GObject

APP_ID = "h3v3n-terminal-v12"
GObject.set_prgname(APP_ID)

CONFIG_DIR = os.path.expanduser("~/.config/h3v3n-terminal")
CONFIG_FILE = os.path.join(CONFIG_DIR, "master_config.json")
EXEC_PATH = os.path.abspath(__file__)

class H3V3N_Architect(Gtk.Window):
    def __init__(self):
        super().__init__(title="H3V3N TERMINAL - Pro Edition")
        
        self.set_wmclass(APP_ID, APP_ID)
        self.integrate_system()

        self.set_default_size(1200, 850)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.themes = {
            "Matrix Rain": {"fg": "#00ff41", "bg": "#000000"},
            "Cyberpunk": {"fg": "#f0e68c", "bg": "#28003c"},
            "Dracula": {"fg": "#bd93f9", "bg": "#282a36"},
            "Nordic": {"fg": "#88c0d0", "bg": "#2e3440"},
            "Glitch Red": {"fg": "#ff0000", "bg": "#0f0505"},
            "Ocean Blue": {"fg": "#00d4ff", "bg": "#051020"},
            "Retro Gold": {"fg": "#ffcc00", "bg": "#151000"},
            "Neon Pink": {"fg": "#ff00ff", "bg": "#100010"},
            "Ghost White": {"fg": "#ffffff", "bg": "#111111"},
            "Toxic Waste": {"fg": "#adff2f", "bg": "#001a00"},
            "Blood Moon": {"fg": "#ff4d4d", "bg": "#1a0505"},
            "Ice Castle": {"fg": "#afeeee", "bg": "#002b36"},
            "Deep Forest": {"fg": "#2ecc71", "bg": "#0a1f0a"},
            "Lava Flows": {"fg": "#e67e22", "bg": "#1a0900"},
            "Midnight Sky": {"fg": "#34495e", "bg": "#010a14"},
            "Monokai Pro": {"fg": "#a6e22e", "bg": "#272822"},
            "Vampire": {"fg": "#9b59b6", "bg": "#1a001a"},
            "Slate": {"fg": "#94a3b8", "bg": "#0f172a"}
        }

        self.config = {
            "alpha": 0.75,
            "text_color": {"r": 0.2, "g": 1.0, "b": 0.6},
            "bg_color": {"r": 0.0, "g": 0.0, "b": 0.0},
            "font": "Monospace Bold 12",
            "rgb_speed": 4,
            "show_clock": True,
            "show_sys": True
        }
        
        self.load_config()
        self.current_fg = Gdk.RGBA(self.config["text_color"]["r"], self.config["text_color"]["g"], self.config["text_color"]["b"], 1.0)
        self.current_bg = Gdk.RGBA(self.config["bg_color"]["r"], self.config["bg_color"]["g"], self.config["bg_color"]["b"], self.config["alpha"])
        
        self.hue = 0

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual: self.set_visual(visual)
        self.set_app_paintable(True)

        self.setup_ui_skeleton()
        self.add_new_terminal_tab()
        self.start_timers()
        
        self.show_all()

    def integrate_system(self):
        desktop_entry = f"""[Desktop Entry]
Name=H3V3N Terminal
Comment=Transparent Terminal Emulator
Exec=python3 {EXEC_PATH}
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=System;TerminalEmulator;
StartupWMClass={APP_ID}
"""
        app_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(app_dir, exist_ok=True)
        with open(os.path.join(app_dir, f"{APP_ID}.desktop"), "w") as f:
            f.write(desktop_entry)

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f: self.config.update(json.load(f))
        except: pass

    def save_config(self):
        self.config["text_color"] = {"r": self.current_fg.red, "g": self.current_fg.green, "b": self.current_fg.blue}
        self.config["bg_color"] = {"r": self.current_bg.red, "g": self.current_bg.green, "b": self.current_bg.blue}
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f, indent=4)

    def setup_ui_skeleton(self):
        self.main_overlay = Gtk.Overlay()
        self.add(self.main_overlay)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.vbox.set_name("main_container")
        self.main_overlay.add(self.vbox)

        self.toolbar = Gtk.Toolbar()
        self.toolbar.get_style_context().add_class("h3v3n-bar")
        btn_add = Gtk.ToolButton(icon_name="tab-new-symbolic")
        btn_add.connect("clicked", lambda _: self.add_new_terminal_tab())
        self.toolbar.insert(btn_add, -1)
        
        sep = Gtk.SeparatorToolItem(); sep.set_expand(True); sep.set_draw(False)
        self.toolbar.insert(sep, -1)
        
        btn_settings = Gtk.ToolButton(icon_name="emblem-system-symbolic")
        btn_settings.connect("clicked", lambda _: self.open_master_settings())
        self.toolbar.insert(btn_settings, -1)
        self.vbox.pack_start(self.toolbar, False, False, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.vbox.pack_start(self.notebook, True, True, 0)

        self.statusbar = Gtk.Statusbar()
        self.statusbar.get_style_context().add_class("h3v3n-bar")
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.status_ctx = self.statusbar.get_context_id("h3v3n_hud")

    def add_new_terminal_tab(self):
        term = Vte.Terminal()
        term.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        # Przywrócenie obsługi klawiatury
        term.connect("key-press-event", self.on_terminal_key_press)
        term.connect("button-press-event", self.on_terminal_right_click)
        term.connect("child-exited", lambda v, s: self.close_current_tab())
        
        term.spawn_async(Vte.PtyFlags.DEFAULT, os.environ.get("HOME"), ["/bin/bash"], [], GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None, -1, None, None)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(term)
        
        tab_label = Gtk.Label(label=f"Tab {self.notebook.get_n_pages() + 1}")
        page_num = self.notebook.append_page(scrolled, tab_label)
        self.notebook.show_all()
        self.notebook.set_current_page(page_num)
        self.apply_visual_styles()

    def close_current_tab(self):
        if self.notebook.get_n_pages() > 1:
            self.notebook.remove_page(self.notebook.get_current_page())
        else: self.destroy()

    def apply_visual_styles(self):
        vte_bg = Gdk.RGBA(self.current_bg.red, self.current_bg.green, self.current_bg.blue, self.config["alpha"])
        
        for i in range(self.notebook.get_n_pages()):
            scrolled = self.notebook.get_nth_page(i)
            term = scrolled.get_child()
            term.set_colors(self.current_fg, vte_bg, [])
            term.set_font(Pango.FontDescription(self.config["font"]))

        fg_hex = self.rgba_to_hex(self.current_fg)
        bg_css = f"rgba({int(vte_bg.red*255)}, {int(vte_bg.green*255)}, {int(vte_bg.blue*255)}, {self.config['alpha']})"
        
        css = f"""
        #main_container {{
            background-color: {bg_css};
            border: 3px solid {fg_hex};
            border-radius: 12px;
            margin: 6px;
        }}
        .h3v3n-bar {{
            background-color: rgba(10, 10, 10, 0.3);
            color: {fg_hex};
        }}
        notebook tab {{
            background: rgba(30, 30, 30, 0.4);
            color: {fg_hex};
        }}
        notebook tab:checked {{
            background: {fg_hex};
            color: #000;
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, 800)
        self.queue_draw()

    def update_animations(self):
        self.hue = (self.hue + self.config["rgb_speed"]) % 360
        r, g, b = self.hsv_to_rgb(self.hue / 360, 0.7, 1.0)
        rgb_hex = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

        dyn_css = f"#main_container {{ border-color: {rgb_hex}; margin: 6px; }}"
        p = Gtk.CssProvider(); p.load_from_data(dyn_css.encode())
        self.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        return True

    def update_hud(self):
        now = datetime.now()
        hud = " [H3V3N HUD] "
        if self.config["show_clock"]: hud += f"| {now.strftime('%H:%M:%S')} "
        if self.config["show_sys"]: 
            hud += f"| CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% "
        
        self.statusbar.pop(self.status_ctx)
        self.statusbar.push(self.status_ctx, hud)
        return True

    def start_timers(self):
        GLib.timeout_add(40, self.update_animations)
        GLib.timeout_add_seconds(1, self.update_hud)

    # --- PRZYWRÓCONE: Skróty klawiszowe Ctrl+Shift+C/V ---
    def on_terminal_key_press(self, widget, event):
        state = event.state & Gtk.accelerator_get_default_mod_mask()
        if state == (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK):
            if event.keyval in [Gdk.KEY_C, Gdk.KEY_c]:
                widget.copy_clipboard()
                return True
            if event.keyval in [Gdk.KEY_V, Gdk.KEY_v]:
                widget.paste_clipboard()
                return True
        return False

    def on_terminal_right_click(self, widget, event):
        if event.button == 3:
            menu = Gtk.Menu()
            
            item_copy = Gtk.MenuItem(label="📋 Copy")
            item_copy.connect("activate", lambda _: widget.copy_clipboard())
            menu.append(item_copy)

            item_paste = Gtk.MenuItem(label="📥 Paste")
            item_paste.connect("activate", lambda _: widget.paste_clipboard())
            menu.append(item_paste)
            
            menu.append(Gtk.SeparatorMenuItem())
            
            item_clear = Gtk.MenuItem(label="🧹 Clear Terminal")
            item_clear.connect("activate", lambda _: widget.feed_child(b"\x0c"))
            menu.append(item_clear)
            
            menu.show_all()
            menu.popup_at_pointer(event)
            return True
        return False

    def open_master_settings(self):
        dialog = Gtk.Dialog(title="H3V3N Master Control", transient_for=self, modal=True)
        dialog.set_default_size(550, 600)
        nb = Gtk.Notebook()
        dialog.get_content_area().pack_start(nb, True, True, 0)

        # 🎨 THEMES
        box_t = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
        combo = Gtk.ComboBoxText()
        for t in sorted(self.themes.keys()): combo.append_text(t)
        def change_t(c):
            t_name = c.get_active_text()
            if t_name in self.themes:
                t = self.themes[t_name]
                self.current_fg.parse(t["fg"])
                self.current_bg.parse(t["bg"])
                self.apply_visual_styles()
                self.save_config()
        combo.connect("changed", change_t)
        box_t.pack_start(Gtk.Label(label="Color Profile:", xalign=0), False, False, 0)
        box_t.pack_start(combo, False, False, 0)
        nb.append_page(box_t, Gtk.Label(label="🎨 Themes"))

        # 🖌️ APPEARANCE
        box_l = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15, margin=15)
        box_l.pack_start(Gtk.Label(label="Global Transparency:", xalign=0), False, False, 0)
        sc_a = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.05, 1.0, 0.05)
        sc_a.set_value(self.config["alpha"])
        sc_a.connect("value-changed", self.on_alpha_slider_changed)
        box_l.pack_start(sc_a, False, False, 0)

        f_btn = Gtk.FontButton(font=self.config["font"])
        f_btn.connect("font-set", lambda b: [self.config.update({"font": b.get_font()}), self.apply_visual_styles(), self.save_config()])
        box_l.pack_start(Gtk.Label(label="Font:", xalign=0), False, False, 0)
        box_l.pack_start(f_btn, False, False, 0)
        
        c_btn = Gtk.ColorButton(rgba=self.current_fg)
        c_btn.connect("color-set", lambda b: [setattr(self, 'current_fg', b.get_rgba()), self.apply_visual_styles(), self.save_config()])
        box_l.pack_start(Gtk.Label(label="Text Color:", xalign=0), False, False, 0)
        box_l.pack_start(c_btn, False, False, 0)
        nb.append_page(box_l, Gtk.Label(label="🖌️ Look"))

        # ⚙️ FEATURES
        box_f = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
        for l, k in [("Clock", "show_clock"), ("System Monitor", "show_sys")]:
            hb = Gtk.Box(spacing=10); sw = Gtk.Switch(active=self.config[k])
            sw.connect("notify::active", lambda s, ps, key=k: [self.config.update({key: s.get_active()}), self.save_config()])
            hb.pack_start(Gtk.Label(label=l, xalign=0), True, True, 0); hb.pack_start(sw, False, False, 0)
            box_f.pack_start(hb, False, False, 0)
        nb.append_page(box_f, Gtk.Label(label="⚙️ Features"))

        # ℹ️ INFO
        box_i = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=20)
        txt = f"<b>H3V3N TERMINAL</b>\n\nVersion 12.6\nSystem: {platform.system()}\nArchitecture: {platform.machine()}"
        l_i = Gtk.Label(xalign=0); l_i.set_markup(txt); box_i.pack_start(l_i, True, True, 0)
        nb.append_page(box_i, Gtk.Label(label="ℹ️ Info"))

        dialog.add_button("CLOSE", Gtk.ResponseType.OK); dialog.show_all(); dialog.run(); dialog.destroy()

    def on_alpha_slider_changed(self, scale):
        self.config["alpha"] = scale.get_value()
        self.current_bg.alpha = self.config["alpha"]
        self.apply_visual_styles()
        self.save_config()

    def rgba_to_hex(self, rgba):
        return "#{:02x}{:02x}{:02x}".format(int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))

    def hsv_to_rgb(self, h, s, v):
        i = int(h*6); f = h*6-i; p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
        return [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i%6]

if __name__ == "__main__":
    GObject.threads_init()
    app = H3V3N_Architect(); app.connect("destroy", Gtk.main_quit); Gtk.main()
