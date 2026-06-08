"""Guide tab with usage instructions."""
from html import escape
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser


class GuideTab(QWidget):
    """Tab providing usage instructions."""

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()

    def _create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        self.update_translations()

    @staticmethod
    def format_step_text(text: str) -> str:
        """Render newline-separated guide text as readable HTML blocks."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""

        html_parts = []
        in_list = False
        for line in lines:
            marker = line[:1]
            is_list_item = marker in ("\u2022", "-")
            item = line[1:].strip() if is_list_item else line
            if is_list_item:
                if not in_list:
                    html_parts.append("<ul>")
                    in_list = True
                html_parts.append(f"<li>{escape(item)}</li>")
            else:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<p>{escape(item)}</p>")

        if in_list:
            html_parts.append("</ul>")
        return "".join(html_parts)

    def update_translations(self):
        html = f"""
        <style>
            h1 {{ margin: 0 0 18px 0; }}
            h3 {{ margin: 22px 0 8px 0; }}
            ul {{ margin: 0 0 8px 22px; padding: 0; }}
            li {{ margin: 0 0 7px 0; line-height: 1.45; }}
            p {{ margin: 0 0 7px 0; line-height: 1.45; }}
        </style>
        <h1>{escape(self.i18n.tr("quick_guide"))}</h1>

        <h3>{escape(self.i18n.tr("step_1_title"))}</h3>
        {self.format_step_text(self.i18n.tr("step_1_text"))}

        <h3>{escape(self.i18n.tr("step_2_title"))}</h3>
        {self.format_step_text(self.i18n.tr("step_2_text"))}

        <h3>{escape(self.i18n.tr("step_3_title"))}</h3>
        {self.format_step_text(self.i18n.tr("step_3_text"))}

        <h3>{escape(self.i18n.tr("step_4_title"))}</h3>
        {self.format_step_text(self.i18n.tr("step_4_text"))}
        """
        self.browser.setHtml(html)
