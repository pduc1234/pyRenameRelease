"""Reusable preview table component."""
import customtkinter as ctk
from .i18n import tr


class PreviewTable(ctk.CTkScrollableFrame):
    """Component to display old name -> new name mapping."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.lang = "en"
        self.current_pairs = []

    def _apply_language(self, lang: str):
        """Update text based on language."""
        self.lang = lang
        self.update_pairs(self.current_pairs)

    def update_pairs(self, pairs: list[tuple[str, str]], empty_text: str = None):
        """Update the table with new old/new name pairs."""
        self.current_pairs = pairs
        
        if empty_text is None:
            empty_text = tr(self.lang, "no_selection")

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        if not pairs:
            label = ctk.CTkLabel(
                self, text=empty_text, text_color="gray", font=("Arial", 11)
            )
            label.pack(pady=20)
            return

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)

        old_head = ctk.CTkLabel(header_frame, text=tr(self.lang, "old_name"), font=("Arial", 10, "bold"))
        old_head.pack(side="left", expand=True)
        
        sep_head = ctk.CTkLabel(header_frame, text="→", font=("Arial", 10, "bold"))
        sep_head.pack(side="left", padx=5)

        new_head = ctk.CTkLabel(header_frame, text=tr(self.lang, "new_name"), font=("Arial", 10, "bold"))
        new_head.pack(side="left", expand=True)

        # Rows
        for i, (old_name, new_name) in enumerate(pairs):
            row_frame = ctk.CTkFrame(
                self,
                fg_color="#3a3a3a" if i % 2 == 0 else "#2a2a2a",
            )
            row_frame.pack(fill="x", padx=5, pady=2)

            old_label = ctk.CTkLabel(
                row_frame, text=old_name, font=("Arial", 10), text_color="gray",
                anchor="w", justify="left"
            )
            old_label.pack(side="left", expand=True, fill="x", padx=10, pady=5)

            arrow_label = ctk.CTkLabel(row_frame, text="→", font=("Arial", 10))
            arrow_label.pack(side="left", padx=5)

            new_label = ctk.CTkLabel(
                row_frame, text=new_name, font=("Arial", 10, "bold"), text_color="#1D9E75",
                anchor="w", justify="left"
            )
            new_label.pack(side="left", expand=True, fill="x", padx=10, pady=5)
