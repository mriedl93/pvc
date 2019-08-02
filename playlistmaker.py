from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import pickle
import os
import subprocess, shlex

class PlaylistMaker(QDialog):

    def __init__(self):
        super(PlaylistMaker, self).__init__()

        test = QLabel('Work in Progress ;)')

        layout = QHBoxLayout()
        layout.addWidget(test)

        self.setLayout(layout)
        self.setWindowTitle('Playlist Maker')

