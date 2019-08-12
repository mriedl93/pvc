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
        self.audioAPISelection = QComboBox()
        self.audioAPISelection.addItems(['Jack', 'ALSA', 'Dummy'])
        self.audioAPISelection.currentIndexChanged.connect(self.audioHWField)
        self.audioAPISelectionLabel = QLabel('Audio API')
        self.audioAPISelectionLabel.setBuddy(self.audioAPISelection)
        self.audioDecksLabel = QLabel('Nr. of Decks')
        self.audioDecksSelection = QComboBox()
        self.audioDecksSelection.addItems(['1', '2', '3'])
        self.audioDecksSelection.setCurrentIndex(1)
        self.audioDecksSelection.currentIndexChanged.connect(self.audioHWField)

        self.audioCardLayout = QHBoxLayout()
        self.audiocardLabel = QLabel('HW Device:')
        self.audioCard1TextField = QLineEdit()
        self.audioCard2TextField = QLineEdit()
        self.audioCard3TextField = QLineEdit()
        self.audioCardLayout.addWidget(self.audiocardLabel)
        self.audioCardLayout.addWidget(self.audioCard1TextField)
        self.audioCardLayout.addWidget(self.audioCard2TextField)
        self.audioCardLayout.addWidget(self.audioCard3TextField)



        # Medium
        self.mediumSelection = QComboBox()
        self.mediumSelectionLabel = QLabel('Medium')
        self.mediumSelection.addItems(['serato_2a', 'serato_2b', 'serato_cd', 'traktor_a', 'traktor_b', 'mixvibes_v2', 'mixvibes_7inch'])

        self.audioLayout = QVBoxLayout()
        self.audioAPILayout = QHBoxLayout()
        self.audioAPILayout.addWidget(self.audioAPISelectionLabel)
        self.audioAPILayout.addWidget(self.audioAPISelection)
        self.mediumLayout = QHBoxLayout()
        self.mediumLayout.addWidget(self.mediumSelectionLabel)
        self.mediumLayout.addWidget(self.mediumSelection)
        self.audioDecksLayout = QHBoxLayout()
        self.audioDecksLayout.addWidget(self.audioDecksLabel)
        self.audioDecksLayout.addWidget(self.audioDecksSelection)
        self.audioLayout.addLayout(self.audioAPILayout)
        self.audioLayout.addLayout(self.audioCardLayout)
        self.audioLayout.addLayout(self.mediumLayout)
        self.audioLayout.addLayout(self.audioDecksLayout)

        # THRU
        self.thruLabel = QLabel('THRU Switch\nfor Traktro Audio 6')
        self.channelAThru = QPushButton('THRU A')
        self.channelAThru.clicked.connect(partial(self.thruSwitch, 'a'))
        self.channelBThru = QPushButton('THRU B')
        self.channelBThru.clicked.connect(partial(self.thruSwitch, 'b'))

        # 33 45
        self.speed = QCheckBox('45 rpm')
        self.speed.setChecked(True)

        # Locking
        self.locking = QCheckBox('Deck Locking')
        self.locking.setChecked(True)

        secondBox = QHBoxLayout()
        secondBox.addWidget(self.speed)
        secondBox.addWidget(self.locking)

        # Buttons
        start = QPushButton('Start xwax')
        verbose = QPushButton('Show Command')

        thirdBox = QVBoxLayout()
        thirdBox.addWidget(start)
        thirdBox.addWidget(verbose)

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
        settingsLayout.addLayout(self.audioLayout)
        settingsLayout.addLayout(secondBox)

        self.startupcmd = QLineEdit()
        self.startupcmd.setReadOnly(True)
        self.startupcmdLabel = QLabel('Generated Startup Command')
        self.startupcmdBox = QVBoxLayout()
        self.startupcmdBox.addWidget(self.startupcmdLabel)
        self.startupcmdBox.addWidget(self.startupcmd)

        # Main Layout
        layout = QGridLayout()
        layout.addLayout(settingsLayout, 0, 0)
        layout.addLayout(thirdBox, 0, 1)
        layout.addLayout(playlistsBox, 1, 0)
        layout.addLayout(thruBox4, 1, 1)
        layout.addLayout(self.startupcmdBox, 2, 0, 1, 2)

        self.audioHWField()
        start.clicked.connect(self.run)
        verbose.clicked.connect(partial(self.run, True))
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

    def audioHWField(self):
        """Handles the HW Device Text fields"""
        deck_nr = int(self.audioDecksSelection.currentText())
        audioCardField = [self.audioCard1TextField, self.audioCard2TextField, self.audioCard3TextField]

        if self.audioAPISelection.currentIndex() == 1:
            self.setAllNegative()
            for i in range(deck_nr):
                audioCardField[i].setEnabled(True)
        else:
            self.setAllNegative()
        
    def setAllNegative(self):
        """Disables all Hardware Device text field when Dummy or JACK are selected"""
        self.audioCard1TextField.setEnabled(False)
        self.audioCard2TextField.setEnabled(False)
        self.audioCard3TextField.setEnabled(False)

    def thruSwitch(self, channel):
        """ Switches THRU to channel for Traktor Audio 6 """
        try:
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


    def run(self, verbose=False):
        
        if self.speed.isChecked():
            rpm = '-45'
        else:
            rpm = '-33'
        
        if self.locking.isChecked():
            lock = '-c'
        else:
            lock = '-u'

        ### JACK API
        if self.audioAPISelection.currentText() == 'Jack':
            if self.audioDecksSelection.currentIndex() == 0:
                api = '-j deckA'
            elif self.audioDecksSelection.currentIndex() == 1:
                api = '-j deckA -j deckB'
            else:
                api = '-j deckA -j deckB -j deckC'

        ### DUMMY
        elif self.audioAPISelection.currentText() == 'Dummy':
            api = '--dummy'

        ### ALSA API
        else:
            deck_nr = int(self.audioDecksSelection.currentText())
            audioDevices = [self.audioCard1TextField, self.audioCard2TextField, self.audioCard3TextField]
            api = []

            for i in range(deck_nr):
                api.append('-a')
                api.append(audioDevices[i].text())
            
            api = ' '.join(api)
        
        runPlaylists = []
        for i in self.playlistsList.selectedItems():
            runPlaylists.append('-l')
            runPlaylists.append(i.text())
        
        startcmd = "xwax {} {} -s /bin/cat {} -t {} {}".format(lock, rpm, ' '.join(runPlaylists), self.mediumSelection.currentText(), api)
        if verbose:
            self.startupcmd.setText(startcmd)
        else:
            self.startupcmd.setText(startcmd)
            subprocess.Popen(shlex.split(startcmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    pvc = PvcGui()
    pvc.show()
    sys.exit(app.exec_())
