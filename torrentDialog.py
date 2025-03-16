from PyQt5.QtWidgets import (QFileDialog, QInputDialog, QDialog, QGridLayout, QListWidget, QPushButton)
from widget import GroupBox
import subprocess
import re
import bencodepy
import hashlib
import base64

class TorrentDialog(QDialog):
	def __init__(self, p):
		super().__init__()
		self.setPresenter(p)
		self.torrentPath = ''
		self.magnetLink = ''
		self.initUI()
		
	def setPresenter(self, p):
		self.presenter = p
	
	def initUI(self):
		self.genGroupPlaylist()

		self.grid = QGridLayout(self)
		self.grid.addWidget(self.groupBoxPlaylisy, 0, 0)
		self.setLayout(self.grid)

		self.setWindowTitle("Torrent Stream")
		self.exec_()
	
	def genGroupPlaylist(self):
		self.listWidget = QListWidget()
		self.groupBoxPlaylisy = GroupBox("Torrent", self.listWidget)

		self.layout = QGridLayout()
		self.layout.addWidget(self.listWidget, 1, 0, 5, 4)
		
		btn = QPushButton("Open torrent", self)
		btn.clicked.connect(self.openTorrentFile)
		btn.setToolTip('Open .torrent file')
		self.layout.addWidget(btn, 0, 0)

		btn = QPushButton("Open magnet", self)
		btn.clicked.connect(self.openMagnetLink)
		btn.setToolTip('Open magnet lint or .torrent link')
		self.layout.addWidget(btn, 0, 1)
		
		btn = QPushButton("OK", self)
		btn.setToolTip('Play secected file')
		btn.clicked.connect(self.playFile)
		self.layout.addWidget(btn, 6, 0)
		self.listWidget.itemDoubleClicked.connect(self.playFile)
		
		self.groupBoxPlaylisy.setLayout(self.layout)
	
	def playFile(self):
		id = self.listWidget.selectedItems()[0].text()
		res = re.match('[0-9]+', id)
		if not res:
			return
		id = id[res.start():res.end()]
		if not id is None:
			self.presenter.torrentGo(id, self.magnetLink, self.torrentPath)
		self.close()
	
	def openTorrentFile(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filter = "torrent(*.torrent)"
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",filter, options=options)
		if fileName:
			self.torrentPath = fileName
			self.magnetLink  = ''
			print(fileName)
			listOfTorrentFiles = self.getListOfTorrentFile(self.torrentPath)
			self.listWidget.addItems(listOfTorrentFiles)

	def openMagnetLink(self):
		link, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
		if ok:
			self.magnetLink = link
			self.torrentPath = ''
			print(link)
			listOfTorrentFiles = self.getListOfTorrentFile(self.magnetLink)
			self.listWidget.addItems(listOfTorrentFiles)
	
	def getListOfTorrentFile(self, path):
		out = subprocess.Popen(['peerflix', path, '--list'], 
				stdout=subprocess.PIPE, 
				stderr=subprocess.STDOUT, shell=True)
		stdout, stderr = out.communicate()
		listOfTorrentFiles = stdout.decode("utf-8") .split('\n')
		listOfTorrentFiles = self.filterFiles(listOfTorrentFiles)
		for f in listOfTorrentFiles:
			print(f)
		print('Err: ', stderr)
		return listOfTorrentFiles

	def filterFiles(self, files):
		def isMedia(file_):
			e = [".webm", ".mkv", ".flv", ".vob", ".ogv,", ".ogg",
				".drc", ".gif", ".gifv", ".mng", ".avi", ".mov,", ".qt",
				".wmv", ".yuv", ".rm", ".rmvb", ".asf", ".amv", ".mp4,",
				".m4p", "(with", "DRM),", ".m4v", ".mpg,", ".mp2,",
				".mpeg,", ".mpe,", ".mpv", ".mpg,", ".mpeg,", ".m2v", ".m4v",
				".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv",
				".f4v", ".f4p", ".f4a", ".f4b"]
			return any([ext in file_ for ext in e])
		filesres = []
		for file_ in files:
			if isMedia(file_):
				filesres.append(file_)
		return filesres

	def makeMagnetFromFile(self, file) :
		metadata = bencodepy.decode_from_file(file)
		subj = metadata[b'info']
		hashcontents = bencodepy.encode(subj)
		digest = hashlib.sha1(hashcontents).digest()
		b32hash = base64.b32encode(digest).decode()
		return 'magnet:?'\
			+ 'xt=urn:btih:' + b32hash\
			+ '&dn=' + metadata[b'info'][b'name'].decode()\
			+ '&tr=' + metadata[b'announce'].decode()\
			+ '&xl=' + str(metadata[b'info'][b'length'])



	