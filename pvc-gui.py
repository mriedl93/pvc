from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import pickle


class PvcGui(QDialog):

    def __init__(self):
        super(PvcGui, self).__init__()

        self.file = None
        self.playlists = []

        # Audio API
        self.audioComboBox = QComboBox()
        self.audioComboBox.addItems(['Jack', 'ALSA'])
        audioLabel = QLabel('Audio API')
        audioLabel.setBuddy(self.audioComboBox)
        audioDecksLabel = QLabel('Nr. of Decks')
        self.audioDecks = QComboBox()
        self.audioDecks.addItems(['1', '2', '3'])
        self.audioDecks.setCurrentIndex(1)

        audioBox = QVBoxLayout()
        audioAPI = QHBoxLayout()
        audioAPI.addWidget(audioLabel)
        audioAPI.addWidget(self.audioComboBox)
        audioDecksBox = QHBoxLayout()
        audioDecksBox.addWidget(audioDecksLabel)
        audioDecksBox.addWidget(self.audioDecks)
        audioBox.addLayout(audioAPI)
        audioBox.addLayout(audioDecksBox)

        # 33 45
        self.speed = QCheckBox('45 rpm')
        self.speed.setChecked(True)

        secondBox = QHBoxLayout()
        secondBox.addWidget(self.speed)

        # Buttons
        start = QPushButton('Start xwax')

        thirdBox = QVBoxLayout()
        thirdBox.addWidget(start)

        # Playlists
        self.playlistsList = QListWidget()
        self.playlistsList.setSelectionMode(QAbstractItemView.MultiSelection)
        playlistsLabel = QLabel('Playlists')
        playlistAppenButton = QPushButton('Add Playlist')
        playlistAppenButton.clicked.connect(self.fileSelection)
        playlistDeleteButton = QPushButton('Delete Playlist')
        playlistDeleteButton.clicked.connect(self.playlistDelete)

        playlistsBox = QVBoxLayout()
        playlistsBox.addWidget(playlistsLabel)
        playlistsBox.addWidget(self.playlistsList)
        playlistsBox.addWidget(playlistAppenButton)
        playlistsBox.addWidget(playlistDeleteButton)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(audioBox)
        settingsLayout.addLayout(secondBox)

        # Main Layout
        layout = QGridLayout()
        layout.addLayout(settingsLayout, 0, 0)
        layout.addLayout(thirdBox, 0, 1)
        layout.addLayout(playlistsBox, 1, 0)

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
        with open('config.pkl', 'rb') as file:
            self.playlists = pickle.load(file)
        self.updatePlaylistsList()

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

    def run(self):
        
        if self.speed.isChecked():
            rpm = '-45'
        else:
            rpm = '-33'

        print(self.audioComboBox.currentText())
        if self.audioComboBox.currentText() == 'Jack':
            if self.audioDecks.currentIndex() == 0:
                api = '-j deckA'
            elif self.audioDecks.currentIndex() == 1:
                api = '-j deckA -j deckB'
            else:
                api = '-j deckA -j deckB -j deckC'
        else:
            print('ALSA')
        
        print('xwax', rpm, api)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pvc = PvcGui()
    pvc.show()
    sys.exit(app.exec_())
