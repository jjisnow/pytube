#!/usr/bin/env python
import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from pytube import downloader


class MagicWizard(QWizard):
    def __init__(self, parent=None):
        super(MagicWizard, self).__init__(parent)
        self.addPage(url_page(self))
        self.addPage(itag_page(self))
        self.addPage(final_path_page(self))
        self.setWindowTitle("Pytube GUI Downloader")
        self.setWindowIcon(
            QtGui.QIcon(
                os.path.join("..", "images", "rooster.png")
            ))
        # self.resize(640,480)


class url_page(QWizardPage):
    def __init__(self, parent=None):
        super(url_page, self).__init__(parent)
        self.setTitle("Choose video link")
        self.setSubTitle("Please input a URL to download")

        layout = QVBoxLayout()

        self.myTextBox = QLineEdit(self)
        self.myTextBox.setAlignment(Qt.AlignLeft)
        self.registerField("TextBox", self.myTextBox)
        layout.addWidget(self.myTextBox)

        self.setLayout(layout)


class itag_page(QWizardPage):
    def __init__(self, parent=None):
        super(itag_page, self).__init__(parent)
        self.setTitle("Choose itag")
        self.setSubTitle("Choose an itag corresponding to a video or audio stream")

        layout = QVBoxLayout()

        self.label1 = QLabel()
        layout.addWidget(self.label1)

        hbox = QHBoxLayout()
        layout.addLayout(hbox)

        self.label2 = QLabel()
        hbox.addWidget(self.label2, alignment=Qt.AlignLeft)

        self.itag_box = QLineEdit()
        self.registerField("iTag*", self.itag_box)
        hbox.addWidget(self.itag_box)

        self.setLayout(layout)

    def initializePage(self):
        tb = self.field("TextBox")
        self.label2.setText("itag: ")
        itag_descr = downloader.downloader(tb, "--list")
        font = self.label1.font()
        self.label1.setFont(QtGui.QFont("Courier", 6, QtGui.QFont.Medium))
        self.label1.setText(itag_descr)


class final_path_page(QWizardPage):
    def __init__(self, parent=None):
        super(final_path_page, self).__init__(parent)
        layout = QVBoxLayout()

        self.label1 = QLabel()
        layout.addWidget(self.label1)

        self.setLayout(layout)

    def initializePage(self):
        tb = self.field("TextBox")
        itag = self.field("iTag")
        final_path = downloader.downloader(tb, "--itag", itag, "-v")
        self.label1.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label1.setText(f"Final output file: \'{final_path}\'")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    wizard = MagicWizard()
    wizard.show()
    sys.exit(app.exec_())
