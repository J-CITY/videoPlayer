from PyQt5.QtWidgets import (QDialog, QGridLayout, QPushButton)
from PyQt5.QtWidgets import (QDoubleSpinBox)

class DelayDialog(QDialog):
	def __init__(self, p, delay, type):
		super().__init__()
		self.type = type
		self.delay = float(delay)/1000000.0
		self.setPresenter(p)
		self.initUI()
		
	def setPresenter(self, p):
		self.presenter = p
	
	def initUI(self):
		self.grid = QGridLayout(self)
		
		self.spbox = QDoubleSpinBox()
		self.spbox.setMaximum(1000.0)
		self.spbox.setMinimum(-1000.0)
		self.spbox.setValue(self.delay)
		self.spbox.setSingleStep(0.1)
		self.grid.addWidget(self.spbox, 0, 0, 1, 0)
		
		self.bOk = QPushButton("Ok")
		self.bOk.clicked.connect(self.pressOk)
		self.grid.addWidget(self.bOk, 1, 0)
		
		self.bCancel = QPushButton("Cancel")
		self.bCancel.clicked.connect(self.close)
		self.grid.addWidget(self.bCancel, 1, 1)
		
		self.setLayout(self.grid)

		self.setWindowTitle("Delay")
		self.exec_()
	
	def pressOk(self):
		self.presenter.setDelay(int(self.spbox.value()*1000000), self.type)
		self.close()
	
	
	
	
	
	