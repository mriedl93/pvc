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

        # Audio API & Decks
        self.audioAPISelection = QComboBox()
        self.audioAPISelection.addItems(['Jack', 'ALSA', 'Dummy'])
        self.audioAPISelection.currentIndexChanged.connect(self.audioHWField)
        self.audioAPISelectionLabel = QLabel('Audio API')
        self.audioAPISelectionLabel.setBuddy(self.audioAPISelection)
        self.audioDecksLabel = QLabel('Nr. of Decks')
        self.audioDecksSelection = QComboBox()
        self.audioDecksSelection.addItems(['1', '2', '3'])
        self.audioDecksSelection.currentIndexChanged.connect(self.audioHWField)

        # HW Devices
        self.audiocardLabel = QLabel('HW Device:')
        self.audioCard1TextField = QLineEdit()
        self.audioCard2TextField = QLineEdit()
        self.audioCard3TextField = QLineEdit()

        # Medium
        self.mediumSelection = QComboBox()
        self.mediumSelectionLabel = QLabel('Medium')
        self.mediumSelection.addItems(['serato_2a', 'serato_2b', 'serato_cd', 'traktor_a', 'traktor_b', 'mixvibes_v2', 'mixvibes_7inch'])

        # THRU
        self.thruLabel = QLabel('THRU Switch\nfor Traktro Audio 6')
        self.channelAThru = QPushButton('THRU A')
        self.channelAThru.clicked.connect(partial(self.thruSwitch, 'a'))
        self.channelBThru = QPushButton('THRU B')
        self.channelBThru.clicked.connect(partial(self.thruSwitch, 'b'))

        if self.checkThruState('a'):
            self.channelAState = QLabel("CHANNEL A THRU")
        else:
            self.channelAState = QLabel("")
        if self.checkThruState('b'):
            self.channelBState = QLabel("CHANNEL B THRU")
        else:
            self.channelBState = QLabel("")

        # 33 45
        self.speed = QCheckBox('45 rpm')
        self.speed.setChecked(True)

        # Locking
        self.locking = QCheckBox('Deck Locking')
        self.locking.setChecked(True)

        # Buttons
        self.start = QPushButton('Start xwax')
        self.save = QPushButton('Save Settings')
        self.verbose = QPushButton('Show Command')


        # Playlists
        self.playlistsList = QListWidget()
        self.playlistsList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.playlistsLabel = QLabel('Select playlists')
        self.playlistAppenButton = QPushButton('Add Playlist')
        self.playlistAppenButton.clicked.connect(self.fileSelection)
        self.playlistCreateBuutton = QPushButton('Create Playlist')
        self.playlistCreateBuutton.clicked.connect(self.playlistCreator)
        self.playlistDeleteButton = QPushButton('Delete Playlist')
        self.playlistDeleteButton.clicked.connect(self.playlistDelete)


        # startup
        self.startupcmd = QLineEdit()
        self.startupcmd.setReadOnly(True)
        self.startupcmdLabel = QLabel('Generated Startup Command')

        self.audioHWField()
        self.start.clicked.connect(self.run)
        self.save.clicked.connect(self.configWrite)
        self.verbose.clicked.connect(partial(self.run, True))
        self.configLoad()
        self.setLayout(self.layoutUI())
        self.setWindowTitle('pvc - Simple xwax starterscript - GUI Version')

    def layoutUI(self):
        self.audioCardLayout = QHBoxLayout()
        self.audioCardLayout.addWidget(self.audiocardLabel)
        self.audioCardLayout.addWidget(self.audioCard1TextField)
        self.audioCardLayout.addWidget(self.audioCard2TextField)
        self.audioCardLayout.addWidget(self.audioCard3TextField)

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

        self.secondBox = QHBoxLayout()
        self.secondBox.addWidget(self.speed)
        self.secondBox.addWidget(self.locking)

        self.thirdBox = QVBoxLayout()
        self.thirdBox.addWidget(self.start)
        self.thirdBox.addWidget(self.save)
        self.thirdBox.addWidget(self.verbose)

        self.thruBox2 = QHBoxLayout()
        self.thruBox2.addWidget(self.channelAThru)
        self.thruBox2.addWidget(self.channelBThru)
        self.thruBox3 = QHBoxLayout()
        self.thruBox3.addWidget(self.channelAState)
        self.thruBox3.addWidget(self.channelBState)
        self.thruBox4 = QVBoxLayout()
        self.thruBox4.addStretch()
        self.thruBox4.addLayout(self.thruBox3)
        self.thruBox4.addLayout(self.thruBox2)
        # thruBox.setLayout(self.thruBox4)
        #thruBox.setAlignment(Qt.AlignTop)

        self.playlistsBox = QVBoxLayout()
        self.playlistsBox.addWidget(self.playlistsLabel)
        self.playlistsBox.addWidget(self.playlistsList)
        self.playlistsBox.addWidget(self.playlistAppenButton)
        self.playlistsBox.addWidget(self.playlistCreateBuutton)
        self.playlistsBox.addWidget(self.playlistDeleteButton)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addLayout(self.audioLayout)
        self.settingsLayout.addLayout(self.secondBox)

        self.startupcmdBox = QVBoxLayout()
        self.startupcmdBox.addWidget(self.startupcmdLabel)
        self.startupcmdBox.addWidget(self.startupcmd)

        self.layout = QGridLayout()
        self.layout.addLayout(self.settingsLayout, 0, 0)
        self.layout.addLayout(self.thirdBox, 0, 1)
        self.layout.addLayout(self.playlistsBox, 1, 0)
        self.layout.addLayout(self.thruBox4, 1, 1)
        self.layout.addLayout(self.startupcmdBox, 2, 0, 1, 2)

        return self.layout

    def fileSelection(self):
        fileDialoge = QFileDialog()
        self.file = fileDialoge.getOpenFileName(self, 'Open File', '/home/markus/Musik')
        self.playlistsList.addItem(self.file[0])
        self.playlists.append(self.file[0])
        self.configWrite() 

    def configWrite(self):
        config = {'medium': self.mediumSelection.currentIndex(),
                'api': self.audioAPISelection.currentIndex(),
                'hw-devices': [self.audioCard1TextField.text(), self.audioCard2TextField.text(), self.audioCard3TextField.text()],
                'decks': self.audioDecksSelection.currentIndex(),
                'lock': self.locking.isChecked(),
                'speed': self.speed.isChecked(),
                'playlists': self.playlists}
        with open('config.pkl', 'wb') as file:
            pickle.dump(config, file)

    def configLoad(self):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as file:
                config = pickle.load(file)
        else:
            config = {'medium': 0,
                    'api': 0,
                    'hw-devices': ["", "", ""],
                    'decks': 1,
                    'lock': True,
                    'speed': True,
                    'playlists': self.playlists}
        
        # Set Audio Decks
        self.audioDecksSelection.setCurrentIndex(config['decks'])
        
        # Set Devices Text Fields
        for i, j in enumerate([self.audioCard1TextField, self.audioCard2TextField, self.audioCard3TextField]):
            j.setText(config['hw-devices'][i])

        # Set Medium
        self.mediumSelection.setCurrentIndex(config['medium'])

        # Set API
        self.audioAPISelection.setCurrentIndex(config['api'])

        # Locking and Speed
        self.locking.setChecked(config['lock'])
        self.speed.setChecked(config['speed'])

        # Set Playlists
        self.playlists = config['playlists']
        self.updatePlaylistsList()

        # Select all Playlists
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
        self.configWrite()
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
            print("Startup-command:  " + startcmd)
            self.startupcmd.setText(startcmd)
        else:
            try:
                print("Starting xwax")
                self.startupcmd.setText(startcmd)
                subprocess.Popen(shlex.split(startcmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except:
                print("Couldn't start xwax")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pvc = PvcGui()
    pvc.show()
    sys.exit(app.exec_())
