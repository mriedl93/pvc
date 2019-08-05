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

        test = QLabel('Select audiofiles that you want to convert into a xwax-readable playlist!')
        tunaButton = QPushButton('Select Tunas')
        tunaButton.clicked.connect(self.tunaSelector)
        tunaRemover = QPushButton('Remove Tunas')
        tunaRemover.clicked.connect(self.tunaDeleter)
        commitButton = QPushButton('Save Playlist')
        commitButton.clicked.connect(self.writePlaylist)
        loadButton = QPushButton('Load Playlist')
        loadButton.clicked.connect(self.loadPlaylist)

        label = "  Structure\n\
                %C = Comment Tag\n\
                %A = Artist Tag\n\
                %T = Title Tag"

        self.structureLabel = QLabel(label)
        self.structureBox1Label = QLabel('Left Column')
        self.structureBox2Label = QLabel('Right Column')
        self.structureBox1 = QLineEdit("%A")
        self.structureBox2 = QLineEdit("%T")
        self.structureBoxLabelBox = QHBoxLayout()
        self.structureBoxLabelBox.addWidget(self.structureBox1Label)
        self.structureBoxLabelBox.addWidget(self.structureBox2Label)
        self.structureBox3 = QHBoxLayout()
        self.structureBox3.addWidget(self.structureBox1)
        self.structureBox3.addWidget(self.structureBox2)
        self.structureBox4 = QVBoxLayout()
        self.structureBox4.addLayout(self.structureBoxLabelBox)
        self.structureBox4.addLayout(self.structureBox3)
        self.structureBox5 = QVBoxLayout()
        self.structureBox5.addWidget(self.structureLabel)
        self.structureBox5.addLayout(self.structureBox4)

        self.tunaList = QListWidget()
        self.tunaList.setSelectionMode(QAbstractItemView.MultiSelection)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(test)
        layout.addWidget(tunaButton)
        layout.addWidget(tunaRemover)
        layout.addWidget(commitButton)
        layout.addWidget(loadButton)
        layout.addLayout(self.structureBox5)
        layout.addWidget(self.tunaList)

        self.setLayout(layout)
        self.setWindowTitle('Playlist Maker')

    def tunaSelector(self):
        self.tunaSelect = QFileDialog()
        self.tunas = self.tunaSelect.getOpenFileNames()
        self.tunaList.addItems(self.tunas[0])        

    def tunaDeleter(self):
        tunas = [x.row() for x in self.tunaList.selectedIndexes()]
        for i in tunas:
            print(i)
            self.tunaList.takeItem(i)

    def tunaPreparator(self, filepath):
        if filepath.endswith(".mp3"):
            self.audiofile = eyed3.load(filepath)
            artistTag = self.audiofile.tag.artist
            titleTag = self.audiofile.tag.title
            commentTag = self.audiofile.tag.comments[0].text # <<- that's weird, isn't it?!
        elif filepath.endswith(".wav"):
            filename = filepath.split("/")[-1].split(".w")[0]
            artistTag = filename.split(" - ")[0]
            titleTag = filename.split(" - ")[1]
            commentTag = self.audiofile.tag.comments[0].text # <<- that's weird, isn't it?!
        
        firstColumn = []
        firstBoxSplitted = self.structureBox1.displayText().split('%')

        for i in firstBoxSplitted:
            if i == '':
                continue
            elif i[0] == 'C':
                firstColumn.append(i.replace('C', '{}'.format(commentTag)))
            elif i[0] == 'A':
                firstColumn.append(i.replace('A', '{}'.format(artistTag)))
            elif i[0] == 'T':
                firstColumn.append(i.replace('T', '{}'.format(titleTag)))

        secondColumn = []
        secondBoxSplitted = self.structureBox2.displayText().split('%')
        
        for i in secondBoxSplitted:
            if i == '':
                continue
            elif i[0] == 'C':
                secondColumn.append(i.replace('C', '{}'.format(commentTag)))
            elif i[0] == 'A':
                secondColumn.append(i.replace('A', '{}'.format(artistTag)))
            elif i[0] == 'T':
                secondColumn.append(i.replace('T', '{}'.format(titleTag)))
            
        string = filepath + "\t" + ''.join(firstColumn) + "\t" + ''.join(secondColumn)
        return string

    def writePlaylist(self):

        filename, other_crap = QFileDialog().getSaveFileName()

        for i in range(0, self.tunaList.count()):
            self.tunaList.item(i).setSelected(True)

        writeStuff = [x.text() for x in self.tunaList.selectedItems()]
        for i, j in enumerate(writeStuff):
            writeStuff[i] = self.tunaPreparator(j)
        writeStuff.append('')
        
        with open(filename, 'w') as file:
            file.write('\n'.join(writeStuff))
    
    def loadPlaylist(self):

        filename, other_crap = QFileDialog().getOpenFileName()

        self.tunaList.clear()

        with open(filename, 'r') as file:
            playlist = file.readlines()

        for i in playlist:
            self.tunaList.addItem(i.split('\t')[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pm = PlaylistMaker()
    pm.show()
    sys.exit(app.exec_())
