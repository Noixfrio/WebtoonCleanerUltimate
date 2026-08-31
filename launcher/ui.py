import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import threading
import sys
from pathlib import Path
from launcher.logger import logger
from launcher.i18n import _, i18n
from launcher.updater import ToonixUpdater
from config.user_config import (
    format_bytes,
    get_free_space,
    get_models_dir,
    list_available_drives,
    load_user_config,
    save_user_config,
    set_models_dir,
)

class ToonixUI(ctk.CTk):
    def __init__(self, version, skip_update=False, binary_version=None, current_commit=None):
        super().__init__()
        self.version = version
        self.skip_update = skip_update
        self.current_commit = current_commit
        self.updater = ToonixUpdater(current_v=version, binary_v=binary_version or version)

        # Título com commit se disponível
        title = _("app_title") + f" v{version}"
        if current_commit:
            title += f" ({current_commit})"
        self.title(title)

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
        self.btn_support.pack(side="bottom", pady=10, padx=20, fill="x")

        # Label de versão/commit no rodapé
        version_text = f"v{self.version}"
        if self.current_commit:
            version_text += f" • {self.current_commit}"
        self.version_label = ctk.CTkLabel(
            self.side_panel,
            text=version_text,
            font=("Inter", 9),
            text_color="#6e7681"
        )
        self.version_label.pack(side="bottom", pady=(0, 10))

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
            if not self.skip_update:
                logger.info("Checando atualizações...")
                self.after(0, lambda: self._set_status(_("status_checking_updates"), "#58a6ff"))
                self.after(0, lambda: self.progress_bar.set(0.2))
                remote = self.updater.check_for_updates()

                if remote:
                    self.after(0, lambda: self._set_status(_("status_update_available"), "#58a6ff"))
                    self.after(0, lambda: self._show_update_popup(remote))
                    return
            else:
                logger.info("Verificação de update ignorada.")

            self._continue_boot()

        except Exception as e:
            logger.error(f"Erro no boot worker: {e}")
            self.after(0, lambda: self._set_status(_("status_error"), "red"))
            self._continue_boot()

    def _continue_boot(self):
        """Continua a sequência de boot (Modelos -> Ready)."""
        try:
            self.after(0, lambda: self._set_status(_("status_checking_models"), "#58a6ff"))
            self.after(0, lambda: self.progress_bar.set(0.6))

            from core.model_manager import ModelManager
            model_mgr = ModelManager()

            missing = model_mgr.get_missing_models()
            if missing:
                logger.info(f"Modelos ausentes detectados: {missing}")
                self.after(0, lambda: self._prompt_models_location(missing))
                return

            self.after(0, self._finish_boot)
        except Exception as e:
            logger.error(f"Erro no continue_boot: {e}")
            self.after(0, lambda: self._finish_boot(_("status_error"), "red"))

    def _prompt_models_location(self, missing):
        """Ask where AI models should be stored before downloading."""
        prompt = ctk.CTkToplevel(self)
        prompt.title("Onde salvar as IAs")
        prompt.geometry("560x520")
        prompt.attributes("-topmost", True)
        prompt.configure(fg_color="#0f1117")
        prompt.resizable(False, False)
        prompt.transient(self)
        prompt.grab_set()

        current_dir = str(get_models_dir())
        path_var = tk.StringVar(value=current_dir)

        # Título
        ctk.CTkLabel(
            prompt,
            text="Onde salvar as IAs",
            font=("Inter", 20, "bold"),
            text_color="#58a6ff",
        ).pack(pady=(20, 10))

        # Descrição
        missing_text = ", ".join(missing)
        ctk.CTkLabel(
            prompt,
            text="Os modelos ocupam cerca de 450 MB. Escolha o disco ou pasta com espaço livre.\nO download não usará mais o cache do disco C: se você escolher outro local.",
            wraplength=500,
            font=("Inter", 11),
            text_color="#c9d1d9",
            justify="center",
        ).pack(padx=20, pady=(0, 5))

        ctk.CTkLabel(
            prompt,
            text=f"Modelos ausentes: {missing_text}",
            wraplength=500,
            font=("Inter", 10),
            text_color="#8b949e",
        ).pack(padx=20, pady=(0, 15))

        # Frame de seleção de disco
        drives = list_available_drives()
        if drives:
            disk_frame = ctk.CTkFrame(prompt, fg_color="#161b22", corner_radius=8)
            disk_frame.pack(pady=10, padx=30, fill="x")

            ctk.CTkLabel(
                disk_frame,
                text="1️⃣  Escolha o disco:",
                font=("Inter", 13, "bold"),
                text_color="#58a6ff"
            ).pack(anchor="w", padx=15, pady=(12, 5))

            # Preparar lista de discos com info de espaço
            drive_values = []
            for item in drives:
                free_gb = item['free'] / (1024**3)
                total_gb = item['total'] / (1024**3)
                percent_free = (item['free'] / item['total'] * 100) if item['total'] > 0 else 0
                drive_values.append(
                    f"{item['label']}    {free_gb:.1f} GB livres de {total_gb:.1f} GB ({percent_free:.0f}% livre)"
                )

            # Detectar disco atual
            current_drive = Path(current_dir).drive or "C:"
            current_idx = 0
            for idx, item in enumerate(drives):
                if item['label'].startswith(current_drive.rstrip(":")):
                    current_idx = idx
                    break

            drive_var = tk.StringVar(value=drive_values[current_idx])

            def on_drive_change(choice):
                idx = drive_values.index(choice)
                selected_drive = drives[idx]["path"]
                # Sugerir pasta ToonixAI no disco escolhido
                suggested = Path(selected_drive) / "ToonixAI"
                path_var.set(str(suggested))

            ctk.CTkOptionMenu(
                disk_frame,
                values=drive_values,
                variable=drive_var,
                command=on_drive_change,
                fg_color="#21262d",
                button_color="#30363d",
                button_hover_color="#484f58",
                dropdown_fg_color="#21262d",
                font=("Inter", 11),
                width=480,
                height=35,
            ).pack(pady=(5, 12), padx=15)

        # Frame de pasta
        folder_frame = ctk.CTkFrame(prompt, fg_color="#161b22", corner_radius=8)
        folder_frame.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(
            folder_frame,
            text="2️⃣  Escolha ou digite a pasta:",
            font=("Inter", 13, "bold"),
            text_color="#58a6ff"
        ).pack(anchor="w", padx=15, pady=(12, 5))

        path_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=path_var,
            font=("Inter", 11),
            width=480,
            height=35,
            fg_color="#0d1117",
            border_color="#30363d"
        )
        path_entry.pack(pady=(5, 8), padx=15)

        def browse():
            chosen = filedialog.askdirectory(
                title="Escolher pasta para os modelos de IA",
                initialdir=str(Path(path_var.get()).parent) if path_var.get() else current_dir,
            )
            if chosen:
                path_var.set(chosen)

        ctk.CTkButton(
            folder_frame,
            text="📁 Navegar e escolher pasta...",
            fg_color="#21262d",
            hover_color="#30363d",
            font=("Inter", 11),
            height=32,
            command=browse,
        ).pack(pady=(0, 12), padx=15)

        # Label de espaço livre (atualiza em tempo real)
        space_label = ctk.CTkLabel(
            prompt,
            text="",
            font=("Inter", 12, "bold"),
            text_color="#3fb950"
        )
        space_label.pack(pady=8)

        def refresh_space(*_args):
            target = path_var.get().strip() or current_dir
            try:
                free = get_free_space(target)
                free_gb = free / (1024**3)
                if free_gb > 10:
                    color = "#3fb950"  # Verde
                    icon = "✅"
                elif free_gb > 1:
                    color = "#d29922"  # Amarelo
                    icon = "⚠️"
                else:
                    color = "#f85149"  # Vermelho
                    icon = "❌"

                space_label.configure(
                    text=f"{icon}  {format_bytes(free)} disponíveis em {target}",
                    text_color=color
                )
            except Exception as e:
                space_label.configure(
                    text=f"⚠️  Caminho inválido ou inacessível",
                    text_color="#f85149"
                )

        path_var.trace_add("write", refresh_space)
        refresh_space()

        # Botões de ação
        btn_frame = ctk.CTkFrame(prompt, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20, fill="x")

        def start_download():
            target = path_var.get().strip() or current_dir
            try:
                # Verificar espaço antes
                free = get_free_space(target)
                if free < 500 * 1024 * 1024:  # 500 MB mínimo
                    space_label.configure(
                        text="❌ Espaço insuficiente! Escolha outro disco.",
                        text_color="#f85149"
                    )
                    return

                set_models_dir(target)
                logger.info(f"Pasta de modelos configurada: {target}")
            except OSError as exc:
                logger.error(f"Pasta de modelos inválida: {exc}")
                space_label.configure(
                    text=f"❌ Erro: {exc}",
                    text_color="#f85149"
                )
                return

            prompt.destroy()
            self._set_status(_("status_downloading_models"), "#58a6ff")
            threading.Thread(target=self._download_models_worker, daemon=True).start()

        def skip_download():
            prompt.destroy()
            self._finish_boot(_("status_models_skipped"), "orange")

        ctk.CTkButton(
            btn_frame,
            text="✓ Baixar modelos neste local",
            fg_color="#238636",
            hover_color="#2ea043",
            font=("Inter", 12, "bold"),
            height=38,
            width=200,
            command=start_download,
        ).pack(side="right", padx=30)

        ctk.CTkButton(
            btn_frame,
            text="Baixar depois",
            fg_color="#21262d",
            hover_color="#30363d",
            font=("Inter", 11),
            height=38,
            width=150,
            command=skip_download,
        ).pack(side="left", padx=30)

        prompt.protocol("WM_DELETE_WINDOW", skip_download)

    def _download_models_worker(self):
        try:
            from core.model_manager import ModelManager
            model_mgr = ModelManager()

            def progress_hook(percentage, model_name):
                global_pct = 0.6 + (percentage * 0.4)
                status_text = f"{_('status_downloading_models')} {model_name}: {int(percentage*100)}%"
                self.after(0, lambda: [self.progress_bar.set(global_pct), self._set_status(status_text, "#58a6ff")])

            if not model_mgr.check_and_download_all(progress_hook=progress_hook):
                logger.warning("Falha ao baixar modelos; o app ainda pode iniciar.")
                self.after(0, lambda: self._finish_boot(_("status_models_failed"), "orange"))
                return
            self.after(0, self._finish_boot)
        except Exception as e:
            logger.error(f"Erro no download de modelos: {e}")
            self.after(0, lambda: self._finish_boot(_("status_models_failed"), "orange"))

    def _finish_boot(self, status_text=None, color="#238636"):
        self.progress_bar.set(1.0)
        self._set_status(status_text or _("status_idle"), color)
        self.btn_start.configure(state="normal")
        logger.info("Botão Iniciar liberado.")

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
        
        kind = "Patch (só código)" if remote_data.get("update_type") == "patch" else "Pacote completo"
        info_text = f"Versão Atual: {self.version}\nNova Versão: {remote_data.get('version')}\nTipo: {kind}"
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
            def skip_update():
                update_win.destroy()
                threading.Thread(target=self._continue_boot, daemon=True).start()

            btn_later = ctk.CTkButton(btn_frame, text="Depois", fg_color="#21262d", hover_color="#30363d", command=skip_update)
            btn_later.pack(side="left", padx=20)
        else:
            update_win.protocol("WM_DELETE_WINDOW", lambda: self.quit()) # Força fechar o app se fechar o popup

    def _update_worker(self, remote_data):
        """Thread que gerencia o download e a aplicação do patch."""
        phase_labels = {
            "download": "Baixando",
            "verify": "Verificando arquivo",
            "apply": "Aplicando atualização",
        }
        try:
            def progress_hook(percentage, phase="download"):
                label = phase_labels.get(phase, "Atualizando")
                self.after(0, lambda p=percentage, t=f"{label}... {int(percentage*100)}%": [
                    self.progress_bar.set(p),
                    self._set_status(t, "#58a6ff"),
                ])

            success = self.updater.perform_update(remote_data, progress_callback=progress_hook)
            if not success:
                self.after(0, lambda: self._set_status("Falha na atualização. Você pode iniciar mesmo assim.", "orange"))
                self.after(0, lambda: self.btn_start.configure(state="normal"))
                self._continue_boot()
        except Exception as e:
            logger.error(f"Erro fatal no update_worker: {e}")
            self.after(0, lambda: self._set_status("Erro na atualização. Inicie o app normalmente.", "orange"))
            self.after(0, lambda: self.btn_start.configure(state="normal"))
            self._continue_boot()

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
        settings_win.geometry("480x430")
        settings_win.attributes("-topmost", True)
        settings_win.configure(fg_color="#0f1117")
        
        config = load_user_config()

        # UI de Config
        ctk.CTkLabel(settings_win, text=_("settings_lang"), font=("Inter", 12)).pack(pady=(20, 5))
        
        langs = i18n.get_available_languages()
        lang_var = tk.StringVar(value=config.get("language", "pt-br"))
        lang_menu = ctk.CTkOptionMenu(settings_win, values=langs, variable=lang_var, fg_color="#21262d", button_color="#30363d")
        lang_menu.pack(pady=5)

        analytics_var = tk.BooleanVar(value=config.get("analytics", True))
        analytics_check = ctk.CTkCheckBox(settings_win, text=_("settings_analytics"), variable=analytics_var, fg_color="#21262d")
        analytics_check.pack(pady=12)

        ctk.CTkLabel(settings_win, text=_("settings_models_dir"), font=("Inter", 12)).pack(pady=(8, 5))
        models_var = tk.StringVar(value=str(get_models_dir()))
        models_entry = ctk.CTkEntry(settings_win, textvariable=models_var, width=360)
        models_entry.pack(pady=4)

        def browse_models():
            chosen = filedialog.askdirectory(
                title=_("models_dir_browse"),
                initialdir=models_var.get() or str(get_models_dir()),
            )
            if chosen:
                models_var.set(chosen)

        ctk.CTkButton(
            settings_win,
            text=_("models_dir_browse"),
            fg_color="#21262d",
            hover_color="#30363d",
            command=browse_models,
        ).pack(pady=6)

        def save_and_close():
            try:
                set_models_dir(models_var.get().strip() or get_models_dir())
            except OSError as exc:
                logger.error(f"Pasta de modelos inválida: {exc}")
                return
            save_user_config({
                "language": lang_var.get(),
                "analytics": analytics_var.get(),
                "last_check": config.get("last_check", ""),
            })
            
            logger.info("Configurações salvas. Reinicie para aplicar o idioma.")
            settings_win.destroy()

        ctk.CTkButton(settings_win, text=_("settings_save"), command=save_and_close, fg_color="#238636").pack(pady=16)

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

def start_ui(version, skip_update=False, binary_version=None, current_commit=None):
    ctk.set_appearance_mode("dark")
    app = ToonixUI(version, skip_update=skip_update, binary_version=binary_version, current_commit=current_commit)
    app.mainloop()
