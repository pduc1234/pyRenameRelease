"""Main window for File Renamer."""
from pathlib import Path
import webbrowser
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, 
    QSizePolicy, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSettings, QTimer

from .widgets.top_bar import TopBar
from .widgets.sidebar import Sidebar
from .widgets.preview_table import PreviewTable
from .widgets.status_footer import StatusFooter
from .tabs.sequential_tab import SequentialTab
from .tabs.add_suffix_tab import AddSuffixTab
from .tabs.video_format_tab import VideoFormatTab
from .tabs.guide_tab import GuideTab

from ..core.file_scanner import FileScanner
from ..core.preview_engine import PreviewEngine
from ..core.rename_engine import RenameEngine
from ..core.undo_manager import UndoManager
from ..core.update_checker import UpdateChecker
from ..core.update_downloader import UpdateDownloader
from ..core.update_security import verify_sha256
from .i18n import I18nManager
from ..app_info import APP_VERSION
import os
import sys
import subprocess


class MainWindow(QMainWindow):
    """Main window coordinating UI and core logic."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"File Renamer v{APP_VERSION}")
        self.setMinimumSize(900, 650)

        # Initialize Core
        self.settings = QSettings("FileRenamer", "FileRenamer")
        lang = self.settings.value("language", "en")
        self.i18n = I18nManager(lang)
        
        self.scanner = None
        self.preview_engine = PreviewEngine()
        self.undo_manager = UndoManager()
        self.rename_engine = RenameEngine(self.undo_manager)
        self.update_checker = UpdateChecker()
        self.update_downloader = UpdateDownloader()
        self.latest_release = None
        
        self.all_files = []
        self.display_files = []
        
        # Initialize UI
        self._create_layout()
        self._connect_signals()
        
        # Initial status
        self.status_footer.set_status(self.i18n.tr("ready"))
        self._apply_translations()

        # Set initial language in selector
        self.top_bar.set_language(lang)
        
        # Enable drag and drop
        self.setAcceptDrops(True)

        # Check for updates after a short delay
        QTimer.singleShot(2000, self._check_updates)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if Path(path).is_dir():
                self.top_bar.set_folder(path)
                self._on_folder_changed(path)

    def _create_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Bar
        self.top_bar = TopBar(self.i18n)
        main_layout.addWidget(self.top_bar)

        # Main Body (Splitter)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left Sidebar
        self.sidebar = Sidebar(self.i18n)
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setMaximumWidth(360)
        self.splitter.addWidget(self.sidebar)

        # Right Content
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Mode Tabs (Rename vs Guide)
        self.mode_tabs = QTabWidget()
        
        # Rename Mode Content
        rename_content = QWidget()
        rename_layout = QVBoxLayout(rename_content)
        rename_layout.setContentsMargins(5, 5, 5, 5)
        rename_layout.setSpacing(5)

        self.rename_splitter = QSplitter(Qt.Vertical)

        # Function Tabs
        self.rename_tabs = QTabWidget()
        self.seq_tab = SequentialTab(self.i18n)
        self.suffix_tab = AddSuffixTab(self.i18n)
        self.video_tab = VideoFormatTab(self.i18n)

        self.rename_tabs.addTab(self.seq_tab, "Sequential")
        self.rename_tabs.addTab(self.suffix_tab, "Add Suffix")
        self.rename_tabs.addTab(self.video_tab, "Video Format")
        
        self.rename_splitter.addWidget(self.rename_tabs)

        # Preview Table
        self.preview_table = PreviewTable(self.i18n)
        self.rename_splitter.addWidget(self.preview_table)
        
        # Initial sizes for vertical splitter [tabs, preview]
        self.rename_splitter.setSizes([280, 420])
        
        rename_layout.addWidget(self.rename_splitter)
        
        # Guide Tab
        self.guide_tab = GuideTab(self.i18n)

        self.mode_tabs.addTab(rename_content, "Rename")
        self.mode_tabs.addTab(self.guide_tab, "Guide")
        
        right_layout.addWidget(self.mode_tabs)

        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([280, 700])
        
        main_layout.addWidget(self.splitter, 1)

        # Footer
        self.status_footer = StatusFooter(self.i18n)
        main_layout.addWidget(self.status_footer)

    def _connect_signals(self):
        # Top Bar
        self.top_bar.folder_changed.connect(self._on_folder_changed)
        self.top_bar.refresh_requested.connect(self._on_refresh)
        self.top_bar.language_changed.connect(self._on_language_changed)
        self.top_bar.update_requested.connect(self._on_update_requested)

        # Sidebar
        self.sidebar.filter_changed.connect(self._on_filter_changed)
        self.sidebar.sort_changed.connect(self._on_sort_changed)
        self.sidebar.selection_changed.connect(self._on_selection_changed)

        # Tabs
        self.seq_tab.options_changed.connect(self._update_preview)
        self.suffix_tab.options_changed.connect(self._update_preview)
        self.video_tab.options_changed.connect(self._update_preview)
        self.rename_tabs.currentChanged.connect(self._update_preview)
        self.mode_tabs.currentChanged.connect(self._update_preview)

        # Footer
        self.status_footer.rename_requested.connect(self._on_rename)
        self.status_footer.undo_requested.connect(self._on_undo)

    def _on_folder_changed(self, folder):
        self.scanner = FileScanner(folder)
        self._on_refresh(preserve_selection=False)
        self._refresh_undo_button()

    def _on_refresh(self, preserve_selection: bool = True):
        if not self.scanner:
            return
        
        self.all_files = self.scanner.scan()
        self.sidebar.update_extensions(self.scanner.extensions)
        self._on_filter_changed(preserve_selection)

    def _on_filter_changed(self, preserve_selection: bool = True):
        if not self.scanner:
            return
        
        active_exts = self.sidebar.get_active_extensions()
        self.display_files = self.scanner.filter(active_exts)
        self.sidebar.update_items(self.display_files, preserve_selection)
        # update_items triggers selection_changed which triggers preview

    def _on_sort_changed(self, by):
        if not self.scanner:
            return
        self.display_files = self.scanner.sort(self.display_files, by)
        self.sidebar.update_items(self.display_files, preserve_selection=True)

    def _on_selection_changed(self):
        count = len(self.display_files)
        selected = len(self.sidebar.selected_file_paths)
        status = self.i18n.tr("selected_status", n=selected, total=count) if selected > 0 else self.i18n.tr("no_selection")
        # Add 'ready' or similar if needed
        self.status_footer.set_status(status)
        self.status_footer.set_rename_enabled(selected > 0)
        self._update_preview()

    def _get_target_files(self):
        return [f for f in self.display_files if f.path in self.sidebar.selected_file_paths]

    def _update_preview(self):
        # If in Guide mode, clear preview and return
        if self.mode_tabs.currentIndex() == 1:
            self.preview_table.update_pairs([])
            return

        targets = self._get_target_files()
        if not targets:
            self.preview_table.update_pairs([])
            return

        current_tab_idx = self.rename_tabs.currentIndex()
        pairs = []
        
        try:
            if current_tab_idx == 0: # Sequential
                opt = self.seq_tab.get_options()
                pairs = self.preview_engine.preview_sequential(
                    targets, start=opt["start"], pad=opt["pad"], prefix=opt["prefix"], pattern=opt["pattern"]
                )
            elif current_tab_idx == 1: # Suffix
                opt = self.suffix_tab.get_options()
                pairs = self.preview_engine.preview_suffix(
                    targets, suffix=opt["suffix"], separator=opt["separator"]
                )
            elif current_tab_idx == 2: # Video
                opt = self.video_tab.get_options()
                pairs = self.preview_engine.preview_video(
                    targets, pattern=opt["pattern"], start=opt["start"], 
                    auto_detect=opt["auto_detect"], manual_res=opt["manual_res"],
                    prefix=opt["prefix"]
                )
        except Exception as e:
            # Fallback error
            self.status_footer.set_status(self.i18n.tr("preview_error", message=str(e)))
            return

        self.preview_table.update_pairs(pairs)
        
        # Check if rename should be enabled (only if NO errors)
        has_errors = any(p.status == "error" for p in pairs)
        self.status_footer.set_rename_enabled(not has_errors and len(pairs) > 0)

    def _on_rename(self):
        if self.mode_tabs.currentIndex() == 1: # Guide mode
            return

        targets = self._get_target_files()
        if not targets:
            return

        current_tab_idx = self.rename_tabs.currentIndex()
        pairs = []
        
        if current_tab_idx == 0:
            opt = self.seq_tab.get_options()
            pairs = self.preview_engine.preview_sequential(targets, **opt)
        elif current_tab_idx == 1:
            opt = self.suffix_tab.get_options()
            pairs = self.preview_engine.preview_suffix(targets, **opt)
        elif current_tab_idx == 2:
            opt = self.video_tab.get_options()
            pairs = self.preview_engine.preview_video(targets, **opt)
        
        if not pairs:
            return

        # Filter active pairs (exclude errors and no-ops)
        active_pairs = [p for p in pairs if p.status != "error" and p.old_name.lower() != p.new_name.lower()]
        
        if not active_pairs:
            QMessageBox.information(self, self.i18n.tr("rename"), self.i18n.tr("no_changes"))
            return

        # Confirm for large batches
        if len(active_pairs) > 20:
            confirm = QMessageBox.question(
                self, self.i18n.tr("confirm_title"), 
                self.i18n.tr("confirm_msg", n=len(active_pairs))
            )
            if confirm != QMessageBox.Yes:
                return

        success, msg = self.rename_engine.execute(self.top_bar.folder_input.text(), pairs)
        
        if success:
            # Show success popup
            QMessageBox.information(
                self, self.i18n.tr("rename_success_title"), 
                self.i18n.tr("renamed", n=len(active_pairs))
            )
            if msg: # Warning (history failure)
                QMessageBox.warning(self, self.i18n.tr("warning"), msg)
            
            # Update pairs to show "renamed" status
            for p in pairs:
                if any(ap.old_name == p.old_name and ap.new_name == p.new_name for ap in active_pairs):
                    p.status = "renamed"
                    p.message = None
            
            # Refresh file list (this will clear selection)
            # We disconnect to prevent _update_preview from wiping our "renamed" status rows
            self.sidebar.selection_changed.disconnect(self._on_selection_changed)
            self._on_refresh(preserve_selection=False)
            self.sidebar.selection_changed.connect(self._on_selection_changed)
            
            # Update preview table with our "renamed" results
            self.preview_table.update_pairs(pairs)
            self.status_footer.set_rename_enabled(False)
            self._refresh_undo_button()
        else:
            QMessageBox.critical(self, self.i18n.tr("error"), msg)

    def _on_undo(self):
        folder = self.top_bar.folder_input.text()
        if not folder:
            return
            
        success, msg = self.undo_manager.undo(folder)
        if success:
            self.status_footer.set_status(self.i18n.tr("undo_ok"))
            self._on_refresh(preserve_selection=False)
            self._refresh_undo_button()
        else:
            QMessageBox.critical(self, self.i18n.tr("error"), msg)

    def _check_updates(self):
        """Background update check."""
        self.latest_release = self.update_checker.check_for_update()
        if self.latest_release:
            self.top_bar.show_update_button(True)

    def _on_update_requested(self):
        """Show update dialog and handle download/install."""
        if not self.latest_release:
            return
            
        version = self.latest_release.version
        msg = self.i18n.tr("update_dialog_msg", version=version)
        
        reply = QMessageBox.question(
            self, self.i18n.tr("update_dialog_title"), msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            if not self.latest_release.package_url:
                webbrowser.open(self.latest_release.notes_url or self.latest_release.package_url)
                return

            # 1. Start download
            self.status_footer.set_status(f"Downloading update v{version}...")
            self.top_bar.show_update_button(False)
            
            try:
                # We do it synchronously for simplicity in this turn, 
                # but real app should use a QThread.
                # Since it's a small app, we'll keep it simple.
                package_path = self.update_downloader.download_package(
                    self.latest_release.package_url,
                    progress_callback=lambda p: self.status_footer.set_status(f"Downloading: {p}%")
                )
                
                # 2. Verify hash when the release provides one. GitHub API
                # fallback releases may not expose a digest, but they can still
                # be installed through the updater instead of opening a browser.
                if self.latest_release.sha256:
                    self.status_footer.set_status("Verifying update...")
                    if not verify_sha256(package_path, self.latest_release.sha256):
                        QMessageBox.critical(self, "Update Error", "Update package verification failed (hash mismatch).")
                        self.update_downloader.cleanup()
                        return
                else:
                    self.status_footer.set_status("Installing update without release hash...")
                
                # 3. Launch updater
                self.status_footer.set_status("Launching updater...")
                
                # Path to bundled FileRenamerUpdater.exe
                # When running from source, it's a python script, but we assume bundled
                if getattr(sys, 'frozen', False):
                    # Bundled
                    base_dir = os.path.dirname(sys.executable)
                    updater_exe = os.path.join(base_dir, "FileRenamerUpdater.exe")
                    install_dir = base_dir
                else:
                    # Source - for testing we'd need a different flow or just mock
                    QMessageBox.information(self, "Update", "Auto-update is only available in bundled version.")
                    return

                if not os.path.exists(updater_exe):
                    # Fallback to manual update if updater is missing
                    webbrowser.open(self.latest_release.notes_url or self.latest_release.package_url)
                    return

                # Launch updater and exit
                cmd = [
                    updater_exe,
                    "--package", package_path,
                    "--parent-pid", str(os.getpid()),
                    "--install-dir", install_dir,
                    "--restart"
                ]
                subprocess.Popen(cmd, start_new_session=True)
                QApplication.quit()
                
            except Exception as e:
                QMessageBox.critical(self, "Update Error", f"Failed to download or install update: {e}")
                self.status_footer.set_status("Update failed")
                self.top_bar.show_update_button(True)

    def _refresh_undo_button(self):
        folder = self.top_bar.folder_input.text()
        has_history = False
        if folder:
            has_history = self.undo_manager.load_last(folder) is not None
        self.status_footer.set_undo_enabled(has_history)

    def _on_language_changed(self, lang):
        self.i18n.load_language(lang)
        self.settings.setValue("language", lang)
        self._apply_translations()

    def _apply_translations(self):
        self.top_bar.update_translations()
        self.sidebar.update_translations()
        self.preview_table.update_translations()
        self.status_footer.update_translations()
        
        self.seq_tab.update_translations()
        self.suffix_tab.update_translations()
        self.video_tab.update_translations()
        self.guide_tab.update_translations()
        
        # Update tab texts
        self.rename_tabs.setTabText(0, self.i18n.tr("sequential"))
        self.rename_tabs.setTabText(1, self.i18n.tr("suffix"))
        self.rename_tabs.setTabText(2, self.i18n.tr("video"))
        
        self.mode_tabs.setTabText(0, self.i18n.tr("rename"))
        self.mode_tabs.setTabText(1, self.i18n.tr("guide"))
        
        # Re-trigger status update
        self._on_selection_changed()
        
    def closeEvent(self, event):
        # Save splitter state or other settings if desired
        super().closeEvent(event)
