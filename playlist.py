import os
from PyQt5.QtWidgets import (QDialog, QGridLayout, QListWidget, QPushButton, QFileDialog)
from widget import GroupBox

class PlaylistDialog(QDialog):
	def __init__(self, p, pl):
		super().__init__()
		self.playlist = pl
		self.setPresenter(p)
		self.initUI()
		
	def setPresenter(self, p):
		self.presenter = p
	
	def initUI(self):
		self.genGroupPlaylist()

		self.grid = QGridLayout(self)
		self.grid.addWidget(self.groupBoxPlaylisy, 0, 0)
		self.setLayout(self.grid)

		self.setWindowTitle("Playlist")
		self.exec_()
	
	def genGroupPlaylist(self):
		self.listWidget = QListWidget()
		self.groupBoxPlaylisy = GroupBox("Playlist", self.listWidget)

		self.listWidget.addItems(self.playlist)
		self.layout = QGridLayout()
		self.layout.addWidget(self.listWidget, 0, 0, 4, 4)
		
		btn = QPushButton("Add", self)
		btn.clicked.connect(self.addItems)
		self.layout.addWidget(btn, 0, 5)
		btn = QPushButton("Delete", self)
		btn.clicked.connect(self.delItems)
		self.layout.addWidget(btn, 1, 5)
		btn = QPushButton("Up", self)
		btn.clicked.connect(lambda: self.swapItems(True))
		self.layout.addWidget(btn, 2, 5)
		btn = QPushButton("Down", self)
		btn.clicked.connect(lambda: self.swapItems(False))
		self.layout.addWidget(btn, 3, 5)
		
		btn = QPushButton("OK", self)
		btn.clicked.connect(lambda: (self.updateList(), self.close()))
		self.layout.addWidget(btn, 5, 0)
		
		self.listWidget.itemDoubleClicked.connect(self.playSelectedItem)
		
		self.groupBoxPlaylisy.setLayout(self.layout)
		
	def updateList(self):
		pl = []
		for i in range(self.listWidget.count()):
			pl.append(self.listWidget.item(i).text())
		#pl = [i.text() for i in _pl]
		self.presenter.setPlaylist(pl)
	
	def playSelectedItem(self):
		itms = self.listWidget.selectedItems()
		item = -1
		if len(itms) > 0:
			item = self.listWidget.row(itms[0])
		else:
			return
		if item < 0:
			return
			
		self.updateList()
		self.presenter.playById(item)
		
	def delItems(self):
		for item in self.listWidget.selectedItems():
			self.listWidget.takeItem(self.listWidget.row(item))
			
	
	def addItems(self):
		path = os.path.dirname(os.path.abspath(__file__))
		filter = "Video (*.avi *.wmv *.mov *.mkv *3gp)"
		fnames = QFileDialog.getOpenFileNames(self, 'Open files', path, filter)
		self.listWidget.addItems(fnames[0])
		
	
	def swapItems(self, isUp):
		itms = self.listWidget.selectedItems()
		item = 0
		if len(itms) > 0:
			item = self.listWidget.row(itms[0])
		else:
			return
			
		if (item == 0 and isUp) or (item == len(self.listWidget)-1 and not isUp):
			return
		
		itemTo = item-1 if isUp else item+1
		self.listWidget.insertItem(itemTo, self.listWidget.takeItem(item))
		self.listWidget.setCurrentRow(itemTo)
		#self.listWidget.swap(item, itemTo)
		
	
	
	
	
	
	
	
	