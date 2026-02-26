import tkinter as tk
import customtkinter as ctk
import threading
import os
import json
import webbrowser
from pathlib import Path
from launcher.logger import logger
from launcher.i18n import _, i18n
from launcher.updater import ToonixUpdater

class ToonixUI(ctk.CTk):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.updater = ToonixUpdater(current_v=version)

        self.title(_("app_title") + f" v{version}")
        self.geometry("650x450")
        self.configure(fg_color="#0f1117")
        self.resizable(False, False)
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f'+{x}+{y}')

        self._build_ui()
        self._bind_keys()
        
        # Iniciar verificação em background após o carregamento da UI
        self.after(500, self._start_boot_sequence)

    def _build_ui(self):
        # Painel Lateral
        self.side_panel = ctk.CTkFrame(self, width=180, fg_color="#161b22", corner_radius=0)
        self.side_panel.pack(side="left", fill="y")
        
        # Logo placeholder
        self.logo_label = ctk.CTkLabel(self.side_panel, text="TOONIX", font=("Product Sans", 24, "bold"), text_color="#58a6ff")
        self.logo_label.pack(pady=30)

        # Botões
        self.btn_start = ctk.CTkButton(
            self.side_panel, 
            text=_("btn_start"), 
            fg_color="#238636", 
            hover_color="#2ea043",
            state="disabled",
            command=self._on_start_clicked
        )
        self.btn_start.pack(pady=20, padx=20, fill="x")
        
        self.btn_settings = ctk.CTkButton(
            self.side_panel, 
            text=_("btn_settings"), 
            fg_color="#21262d",
            hover_color="#30363d",
            command=self._open_settings
        )
        self.btn_settings.pack(pady=10, padx=20, fill="x")
        
        self.btn_support = ctk.CTkButton(
            self.side_panel, 
            text=_("btn_support"), 
            fg_color="#21262d",
            hover_color="#30363d"
        )
        self.btn_support.pack(side="bottom", pady=20, padx=20, fill="x")

        # Área Principal
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(expand=True, fill="both", padx=20, pady=20)

        # Barra de Progresso / Status
        self.status_label = ctk.CTkLabel(self.main_area, text=_("status_checking"), font=("Inter", 12), text_color="gray")
        self.status_label.pack(side="bottom", pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.main_area, fg_color="#161b22", progress_color="#58a6ff")
        self.progress_bar.pack(side="bottom", fill="x", pady=10)
        self.progress_bar.set(0)

    def _start_boot_sequence(self):
        threading.Thread(target=self._boot_worker, daemon=True).start()

    def _boot_worker(self):
        try:
            # 1. Verificar Updates
            logger.info("Checando atualizações...")
            self.progress_bar.set(0.2)
            remote = self.updater.check_for_updates()
            
            if remote and remote.get("version") != self.version:
                self.after(0, lambda: self._show_update_popup(remote))
                return
            
            # 2. Verificar Integridade
            self.progress_bar.set(0.6)
            self._set_status(_("status_checking"), "gray")
            
            # Simulação de hash esperado (no futuro vem do version.json)
            expected_hash = remote.get("files", {}).get("windows", {}).get("sha256") if remote else None
            
            if not self.updater.validate_integrity(expected_hash):
                # Por enquanto apenas logamos para não travar o dev
                logger.error("Falha silenciosa de integridade (dev mode)")
            
            # 3. Finalizar
            def finish_boot():
                self.progress_bar.set(1.0)
                self._set_status(_("status_idle"), "#238636")
                self.btn_start.configure(state="normal")
                logger.info("Botão Iniciar liberado.")
                
            self.after(0, finish_boot)
            
        except Exception as e:
            logger.error(f"Erro no boot worker: {e}")
            self._set_status(_("status_error"), "red")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def _show_update_popup(self, remote_data):
        """Janela popup para notificar sobre a nova versão."""
        update_win = ctk.CTkToplevel(self)
        update_win.title(_("btn_update"))
        update_win.geometry("500x400")
        update_win.attributes("-topmost", True)
        update_win.configure(fg_color="#0f1117")
        update_win.resizable(False, False)

        # Header
        ctk.CTkLabel(update_win, text=_("btn_update"), font=("Inter", 20, "bold"), text_color="#58a6ff").pack(pady=15)
        
        info_text = f"Versão Atual: {self.version}\nNova Versão: {remote_data['version']}"
        ctk.CTkLabel(update_win, text=info_text, font=("Inter", 13)).pack(pady=5)

        # Changelog Scrollable
        changelog_frame = ctk.CTkTextbox(update_win, width=440, height=180, fg_color="#161b22", border_color="#30363d", border_width=1)
        changelog_frame.pack(pady=15, padx=20)
        changelog_frame.insert("0.0", f"Novidades:\n\n{remote_data.get('changelog', 'Nenhum log fornecido.')}")
        changelog_frame.configure(state="disabled")

        btn_frame = ctk.CTkFrame(update_win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20, fill="x")

        # Lógica de Update
        def start_update_flow():
            update_win.destroy()
            self._set_status("Iniciando download...", "#58a6ff")
            self.progress_bar.set(0)
            threading.Thread(target=self._update_worker, args=(remote_data,), daemon=True).start()

        btn_update = ctk.CTkButton(btn_frame, text=_("btn_update"), fg_color="#238636", hover_color="#2ea043", command=start_update_flow)
        btn_update.pack(side="right", padx=20)

        # Se não for obrigatório, permite cancelar
        if not remote_data.get("mandatory", False):
            btn_later = ctk.CTkButton(btn_frame, text="Depois", fg_color="#21262d", hover_color="#30363d", command=lambda: [update_win.destroy(), self._set_status(_("status_idle"), "#238636"), self.btn_start.configure(state="normal")])
            btn_later.pack(side="left", padx=20)
        else:
            update_win.protocol("WM_DELETE_WINDOW", lambda: self.quit()) # Força fechar o app se fechar o popup

    def _update_worker(self, remote_data):
        """Thread que gerencia o download e a troca do executável."""
        try:
            def progress_hook(percentage):
                # Atualizar UI na thread principal
                self.after(0, lambda: self.progress_bar.set(percentage))
                self.after(0, lambda: self._set_status(f"Baixando... {int(percentage*100)}%", "#58a6ff"))

            success = self.updater.perform_update(remote_data, progress_callback=progress_hook)
            if not success:
                self.after(0, lambda: self._set_status("Falha na atualização!", "red"))
                self.after(0, lambda: self.btn_start.configure(state="normal"))
        except Exception as e:
            logger.error(f"Erro fatal no update_worker: {e}")
            self.after(0, lambda: self._set_status("Erro Crítico!", "red"))

    def _on_start_clicked(self):
        logger.info("Iniciando App principal...")
        self._set_status("Iniciando Backend...", "#58a6ff")
        
        try:
            # 1. Iniciar Backend Interno
            from launcher.backend_server import start_backend
            start_backend() # Inicia em thread separada
            
            # 2. Esconder o launcher e abrir o WebView
            from launcher.desktop_window import launch_desktop
            
            # Precisamos esconder esta janela antes de abrir o webview
            # pois o webview.start() bloqueia a thread principal.
            self.withdraw() 
            
            # launch_desktop irá aguardar o server ficar pronto e bloquear aqui
            launch_desktop("http://127.0.0.1:5000")
            
            # Quando a janela webview fechar, fechamos tudo
            self.quit()
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar app nativo: {e}")
            self.deiconify() # Trazer de volta em caso de erro
            self._set_status("Erro ao iniciar!", "red")

    def _open_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title(_("btn_settings"))
        settings_win.geometry("400x300")
        settings_win.attributes("-topmost", True)
        settings_win.configure(fg_color="#0f1117")
        
        # Carregar config atual
        from .utils import get_resource_path
        config_path = get_resource_path("config/config.json")
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            config = {"language": "pt-br", "analytics": True}

        # UI de Config
        ctk.CTkLabel(settings_win, text=_("settings_lang"), font=("Inter", 12)).pack(pady=(20, 5))
        
        langs = i18n.get_available_languages()
        lang_var = tk.StringVar(value=config.get("language", "pt-br"))
        lang_menu = ctk.CTkOptionMenu(settings_win, values=langs, variable=lang_var, fg_color="#21262d", button_color="#30363d")
        lang_menu.pack(pady=5)

        analytics_var = tk.BooleanVar(value=config.get("analytics", True))
        analytics_check = ctk.CTkCheckBox(settings_win, text=_("settings_analytics"), variable=analytics_var, fg_color="#21262d")
        analytics_check.pack(pady=20)

        def save_and_close():
            new_config = {
                "language": lang_var.get(),
                "analytics": analytics_var.get(),
                "last_check": config.get("last_check", "")
            }
            with open(config_path, "w") as f:
                json.dump(new_config, f, indent=4)
            
            logger.info("Configurações salvas. Reinicie para aplicar o idioma.")
            settings_win.destroy()

        ctk.CTkButton(settings_win, text=_("settings_save"), command=save_and_close, fg_color="#238636").pack(pady=20)

    def _bind_keys(self):
        self.bind("<Control-Shift-L>", lambda e: self._show_log_viewer())

    def _show_log_viewer(self):
        log_win = ctk.CTkToplevel(self)
        log_win.title(_("log_viewer_title"))
        log_win.geometry("600x450")
        log_win.attributes("-topmost", True)
        
        text_area = tk.Text(log_win, bg="#0d1117", fg="#58a6ff", font=("Consolas", 10), padx=10, pady=10)
        text_area.pack(expand=True, fill="both")
        text_area.insert("1.0", logger.get_buffer())
        text_area.configure(state="disabled")

def start_ui(version):
    ctk.set_appearance_mode("dark")
    app = ToonixUI(version)
    app.mainloop()
