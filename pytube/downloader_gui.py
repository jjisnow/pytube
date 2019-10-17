#!/usr/bin/env python
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from pytube import downloader


class QIComboBox(QComboBox):
    def __init__(self, parent=None):
        super(QIComboBox, self).__init__(parent)


class MagicWizard(QWizard):
    def __init__(self, parent=None):
        super(MagicWizard, self).__init__(parent)
        self.addPage(Page1(self))
        self.addPage(Page2(self))
        self.addPage(Page3(self))
        self.setWindowTitle("Pytube GUI Downloader")
        # self.resize(640,480)


class Page1(QWizardPage):
    def __init__(self, parent=None):
        super(Page1, self).__init__(parent)
        self.setTitle("Choose video link")
        self.setSubTitle("Please input a URL to download")

        layout = QVBoxLayout()
        #
        # self.comboBox = QIComboBox(self)
        # self.comboBox.addItem("Python", "/path/to/filename1")
        # self.comboBox.addItem("PyQt5", "/path/to/filename2")
        # layout.addWidget(self.comboBox)
        #
        # file_box = QHBoxLayout()
        # layout.addLayout(file_box)

        # self.myTextBox = QTextEdit(self)
        self.myTextBox = QLineEdit(self)
        self.myTextBox.setAlignment(Qt.AlignLeft)
        self.registerField("TextBox", self.myTextBox)
        # self.myTextBox.setGeometry(QtCore.QRect(100, 0, 350, 50))
        # file_box.addWidget(self.myTextBox)
        layout.addWidget(self.myTextBox)

        # self.uploader = QPushButton("upload", self)
        # # self.uploader.clicked.connect(self.get_file_name)
        # file_box.addWidget(self.uploader)

        # self.spacer = QSpacerItem(0, 0)
        # layout.addSpacerItem(self.spacer)

        self.setLayout(layout)


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.setTitle("Choose itag")
        self.setSubTitle("Choose an itag corresponding to a video or audio stream")
        layout = QVBoxLayout()

        self.label1 = QLabel()
        layout.addWidget(self.label1)

        self.itag_box = QLineEdit()
        self.registerField("iTag*", self.itag_box)
        layout.addWidget(self.itag_box)

        self.setLayout(layout)

    def initializePage(self):
        tb = self.field("TextBox")
        itag_descr = downloader.downloader(tb, "--list")
        self.label1.setText(itag_descr)


class Page3(QWizardPage):
    def __init__(self, parent=None):
        super(Page3, self).__init__(parent)
        layout = QVBoxLayout()

        self.label1 = QLabel()
        layout.addWidget(self.label1)

        self.setLayout(layout)

    def initializePage(self):
        tb = self.field("TextBox")
        itag = self.field("iTag")
        self.label1.setText("Downloading video...")
        downloader.downloader(tb, "--itag", itag, "-v")

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    wizard = MagicWizard()
    wizard.show()
    sys.exit(app.exec_())
