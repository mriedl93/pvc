#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import pickle
import os
import subprocess, shlex
import eyed3

"""

https://stackoverflow.com/questions/8948/accessing-mp3-meta-data-with-python

"""


class PlaylistMaker(QDialog):

    def __init__(self):
        super(PlaylistMaker, self).__init__()

        test = QLabel('Work in Progress ;)')
        tunaButton = QPushButton('Select Tunas')
        tunaButton.clicked.connect(self.tunaSelector)

        self.tunaList = QListWidget()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(test)
        layout.addWidget(tunaButton)
        layout.addWidget(self.tunaList)

        self.setLayout(layout)
        self.setWindowTitle('Playlist Maker')

    def tunaSelector(self):
        self.tunaSelect = QFileDialog()
        self.tunas = self.tunaSelect.getOpenFileNames()
        self.tunaList.addItems(self.tunas[0])        
        self.tunaPreparator(self.tunas[0][0])

    def tunaPreparator(self, filepath):
        self.audiofile = eyed3.load(filepath)
        print(self.audiofile.tag.artist)
        print(self.audiofile.tag.title)
        print(self.audiofile.tag.comments[0].text) # <<- that's weird, isn't it?!
        

        # print('\n'.join(self.tunas[0]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pm = PlaylistMaker()
    pm.show()
    sys.exit(app.exec_())
