from urllib.parse import unquote

from chimerax.core.commands import run
from chimerax.core.settings import Settings
from chimerax.core.tools import ToolInstance, get_singleton
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

from Qt.QtCore import Qt, QUrl
from Qt.QtGui import QColor
from Qt.QtWidgets import (
    QWidget,
    QGridLayout,
    QTextBrowser ,
    QTabWidget,
    QPushButton,
)

class _NoteSettings(Settings):

    AUTO_SAVE = {
        "text": "",
    }
    

class NotesTool(ToolInstance):
    SESSION_SAVE = True

    def __init__(self, session, name="My Notes"):       
        super().__init__(session, name)
        
        self.display_name = name
        
        self.tool_window = MainToolWindow(self, close_destroys=False)        
        self.settings = _NoteSettings(session, name)
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        self.notes_tab = QTabWidget()
        layout.addWidget(self.notes_tab, 0, 0)

        self.session_notes = QTextBrowser()
        self.session_notes.setAutoFormatting(QTextBrowser.AutoAll)
        self.session_notes.setTextInteractionFlags(
            Qt.TextSelectableByMouse |
            Qt.TextSelectableByKeyboard |
            Qt.TextEditable |
            Qt.LinksAccessibleByMouse |
            Qt.LinksAccessibleByKeyboard
        )
        self.session_notes.anchorClicked.connect(self.run_cmd)
        self.session_notes.setOpenLinks(False)
        self.notes_tab.addTab(self.session_notes, "session notes")
 
        self.all_notes = QTextBrowser()
        self.all_notes.setAutoFormatting(QTextBrowser.AutoAll)
        self.all_notes.setHtml(self.settings.text)
        self.all_notes.focusOutEvent = self.save_notes
        self.all_notes.focusInEvent = self.save_notes
        self.all_notes.setTextInteractionFlags(
            Qt.TextSelectableByMouse |
            Qt.TextSelectableByKeyboard |
            Qt.TextEditable |
            Qt.LinksAccessibleByMouse |
            Qt.LinksAccessibleByKeyboard
        )
        self.all_notes.anchorClicked.connect(self.run_cmd)
        self.all_notes.setOpenLinks(False)
        self.notes_tab.addTab(self.all_notes, "all notes")

        format_buttons = QWidget()
        format_layout = QGridLayout(format_buttons)
        layout.addWidget(format_buttons, 1, 0)
        
        cxcmd = QPushButton("turn selected text into command link")
        cxcmd.clicked.connect(self.insert_command)
        format_layout.addWidget(cxcmd, 0, 0)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def run_cmd(self, url):
        scheme = url.scheme()
        if scheme == "cxcmd":
            cmd = unquote(url.toString(QUrl.None_).lstrip("cxcmd:"))
            run(self.session, cmd)
        else:
            link = url.toString(QUrl.None_)
            run(self.session, "open \"" + link + "\"")

    def take_snapshot(self, session, flags):
        return self.session_notes.toHtml()
    
    def insert_command(self, toggled):
        if self.notes_tab.currentIndex() == 0:
            edit = self.session_notes
        else:
            edit = self.all_notes

        cursor = edit.textCursor()
        cmd = cursor.selectedText()
        cursor.removeSelectedText()
        edit.insertHtml("<a href=\"cxcmd:%s\">" % cmd + cmd + "</a>")
        text = edit.toHtml()
    
    @classmethod
    def restore_snapshot(cls, session, data):
        obj = get_singleton(session, cls, "My Notes", display=True)
        obj.session_notes.setHtml(data)

    def save_notes(self, event):
        self.settings.text = self.all_notes.toHtml()

    def delete(self):
        """overload delete"""
        
        super().delete()
