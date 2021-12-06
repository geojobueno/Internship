# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5 import uic
from PyQt5 import QtWidgets

gui_form = r'form.ui'
FORM_CLASS, _ = uic.loadUiType(gui_form)


class ConnectProject(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ConnectProject, self).__init__(parent)
        self.setupUi(self)

