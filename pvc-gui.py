#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys, re
import pickle
import os
import subprocess, shlex
import playlistmaker
from functools import partial


class PvcGui(QDialog):

    def __init__(self):
        super(PvcGui, self).__init__()

        self.file = None
        self.playlists = []

        # Audio API
        self.audioComboBox = QComboBox()
        self.audioComboBox.addItems(['Jack', 'ALSA', 'Dummy'])
        audioLabel = QLabel('Audio API')
        audioLabel.setBuddy(self.audioComboBox)
        audioDecksLabel = QLabel('Nr. of Decks')
        self.audioDecks = QComboBox()
        self.audioDecks.addItems(['1', '2', '3'])
        self.audioDecks.setCurrentIndex(1)

        # Medium
        self.medium = QComboBox()
        mediumLabel = QLabel('Medium')
        self.medium.addItems(['serato_2a', 'serato_2b', 'mixvibes'])

        audioBox = QVBoxLayout()
        audioAPI = QHBoxLayout()
        audioAPI.addWidget(audioLabel)
        audioAPI.addWidget(self.audioComboBox)
        mediumBox = QHBoxLayout()
        mediumBox.addWidget(mediumLabel)
        mediumBox.addWidget(self.medium)
        audioDecksBox = QHBoxLayout()
        audioDecksBox.addWidget(audioDecksLabel)
        audioDecksBox.addWidget(self.audioDecks)
        audioBox.addLayout(audioAPI)
        audioBox.addLayout(mediumBox)
        audioBox.addLayout(audioDecksBox)

        # THRU
        self.thruLabel = QLabel('THRU Switch\nfor Traktro Audio 6')
        self.channelAThru = QPushButton('THRU A')
        self.channelAThru.clicked.connect(partial(self.thruSwitch, 'a'))
        self.channelBThru = QPushButton('THRU B')
        self.channelBThru.clicked.connect(partial(self.thruSwitch, 'b'))

        # 33 45
        self.speed = QCheckBox('45 rpm')
        self.speed.setChecked(True)

        self.locking = QCheckBox('Deck Locking')
        self.locking.setChecked(True)

        secondBox = QHBoxLayout()
        secondBox.addWidget(self.speed)
        secondBox.addWidget(self.locking)

        # Buttons
        start = QPushButton('Start xwax')

        thirdBox = QVBoxLayout()
        thirdBox.addWidget(start)

        #thruBox = QGroupBox("THRU on Traktor Audio 6")
        thruBox2 = QHBoxLayout()
        thruBox2.addWidget(self.channelAThru)
        thruBox2.addWidget(self.channelBThru)
        if self.checkThruState('a'):
            channelAState = QLabel("CHANNEL A THRU")
        else:
            channelAState = QLabel("")
        if self.checkThruState('b'):
            channelBState = QLabel("CHANNEL B THRU")
        else:
            channelBState = QLabel("")
        thruBox3 = QHBoxLayout()
        thruBox3.addWidget(channelAState)
        thruBox3.addWidget(channelBState)
        thruBox4 = QVBoxLayout()
        thruBox4.addStretch()
        thruBox4.addLayout(thruBox3)
        thruBox4.addLayout(thruBox2)
        # thruBox.setLayout(thruBox4)
        #thruBox.setAlignment(Qt.AlignTop)

        # Playlists
        self.playlistsList = QListWidget()
        self.playlistsList.setSelectionMode(QAbstractItemView.MultiSelection)
        playlistsLabel = QLabel('Select playlists')
        playlistAppenButton = QPushButton('Add Playlist')
        playlistAppenButton.clicked.connect(self.fileSelection)
        playlistCreateBuutton = QPushButton('Create Playlist')
        playlistCreateBuutton.clicked.connect(self.playlistCreator)
        playlistDeleteButton = QPushButton('Delete Playlist')
        playlistDeleteButton.clicked.connect(self.playlistDelete)

        playlistsBox = QVBoxLayout()
        playlistsBox.addWidget(playlistsLabel)
        playlistsBox.addWidget(self.playlistsList)
        playlistsBox.addWidget(playlistAppenButton)
        playlistsBox.addWidget(playlistCreateBuutton)
        playlistsBox.addWidget(playlistDeleteButton)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(audioBox)
        settingsLayout.addLayout(secondBox)

        # Main Layout
        layout = QGridLayout()
        layout.addLayout(settingsLayout, 0, 0)
        layout.addLayout(thirdBox, 0, 1)
        layout.addLayout(playlistsBox, 1, 0)
        layout.addLayout(thruBox4, 1, 1)

        start.clicked.connect(self.run)
        self.playlistLoad()
        self.setLayout(layout)
        self.setWindowTitle('pvc - Simple xwax starterscript - GUI Version')

    def fileSelection(self):
        fileDialoge = QFileDialog()
        self.file = fileDialoge.getOpenFileName(self, 'Open File', '/home/markus/Musik')
        self.playlistsList.addItem(self.file[0])
        self.playlists.append(self.file[0])
        self.writeConfig() 

    def writeConfig(self):
        with open('config.pkl', 'wb') as file:
            pickle.dump(self.playlists, file)

    def playlistLoad(self):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as file:
                self.playlists = pickle.load(file)
        self.updatePlaylistsList()
        for i in range(0, self.playlistsList.count()):
            self.playlistsList.item(i).setSelected(True)


    def playlistCreator(self):
        self.playlistMaker = playlistmaker.PlaylistMaker()
        self.playlistMaker.show()

    def updatePlaylistsList(self):
        self.playlistsList.clear()
        for i in self.playlists:
            self.playlistsList.addItem(i)

    def playlistDelete(self):
        indices = [x.row() for x in self.playlistsList.selectedIndexes()]
        for i in indices[::-1]:
            self.playlists.pop(i)
        self.writeConfig()
        self.updatePlaylistsList()

    def thruSwitch(self, channel):
        """ Switches THRU to channel for Traktor Audio 6 """
        try:
            print("{} clicked".format(channel))

            thru_active, output = self.checkThruState(channel)
            if thru_active:
                switch = 'off'
            else:
                switch = 'on'

            subprocess.call(["amixer", "-c", "T6", "cset", "numid={}".format(output), switch])
            print("Switching THRU on Channel {0} {1}".format(channel.upper(), switch))
        except:
            print("Couldn't switch THRU")

    def checkThruState(self, channel):
        try:
            """ Checks the state of THRU for channel on Traktor Audio 6 """
            amixer = subprocess.Popen(['amixer', '-c', 'T6', 'controls'], stdout=subprocess.PIPE)
            grep = subprocess.Popen(["grep", "'Direct Thru Channel {}'".format(channel.upper())], stdin=amixer.stdout, stdout=subprocess.PIPE)
            cut = subprocess.Popen(["cut", "-d", ",", "-f", "1"], stdin=grep.stdout, stdout=subprocess.PIPE)
            output = subprocess.check_output(["cut", "-d", "=", "-f", "2"], stdin=cut.stdout)
            output = str(output)[2]

            am_status = subprocess.Popen(["amixer", "-c", "T6", "scontents"], stdout=subprocess.PIPE)
            grep2 = subprocess.check_output(["grep", "-A", "3", "'Direct Thru Channel {}".format(channel.upper())], stdin=am_status.stdout)

            thru_active = re.search("\[on\]", str(grep2))  # returns boolean
            
            return [thru_active, output]
        except:
            print("No Soundcard found!")


    def run(self):
        
        if self.speed.isChecked():
            rpm = '-45'
        else:
            rpm = '-33'
        
        if self.locking.isChecked():
            lock = '-c'
        else:
            lock = 'u'

        if self.audioComboBox.currentText() == 'Jack':
            if self.audioDecks.currentIndex() == 0:
                api = '-j deckA'
            elif self.audioDecks.currentIndex() == 1:
                api = '-j deckA -j deckB'
            else:
                api = '-j deckA -j deckB -j deckC'
        elif self.audioComboBox.currentText() == 'Dummy':
            api = '--dummy'
        else:
            print('ALSA')
        
        runPlaylists = []
        for i in self.playlistsList.selectedItems():
            runPlaylists.append('-l')
            runPlaylists.append(i.text())
        
        startcmd = "xwax {} {} -s /bin/cat {} -t {} {}".format(lock, rpm, ' '.join(runPlaylists), self.medium.currentText(), api)
        print(startcmd)
        subprocess.Popen(shlex.split(startcmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pvc = PvcGui()
    pvc.show()
    sys.exit(app.exec_())
