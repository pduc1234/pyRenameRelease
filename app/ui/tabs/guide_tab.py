"""Guide tab with usage instructions."""
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

    def update_translations(self):
        html = f"""
        <h1>{self.i18n.tr("quick_guide")}</h1>
        
        <h3>{self.i18n.tr("step_1_title")}</h3>
        <p>{self.i18n.tr("step_1_text").replace("\\n", "<br>")}</p>
        
        <h3>{self.i18n.tr("step_2_title")}</h3>
        <p>{self.i18n.tr("step_2_text").replace("\\n", "<br>")}</p>
        
        <h3>{self.i18n.tr("step_3_title")}</h3>
        <p>{self.i18n.tr("step_3_text").replace("\\n", "<br>")}</p>
        
        <h3>{self.i18n.tr("step_4_title")}</h3>
        <p>{self.i18n.tr("step_4_text").replace("\\n", "<br>")}</p>
        """
        self.browser.setHtml(html)
