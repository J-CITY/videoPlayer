from PyQt5.QtWidgets import (QDialog, QGroupBox, QGridLayout,  QLabel, QComboBox)
from PyQt5.QtCore import (Qt)
from widget import QJumpSlider
import math

class EqualizerDialog(QDialog):
	def __init__(self, p):
		super().__init__()
		self.setPresenter(p)
		self.initUI()
		
	def setPresenter(self, p):
		self.presenter = p
	
	def initUI(self):
		self.eqSliders = []
		self.eqLables = []
		
		# Initialize tab screen
		#self.tabs = QTabWidget()
		#self.tabs.setTabBar(HorizontalTabWidget())
		#self.tabs.setTabPosition(2)
		self.genGroupEqualizer()
		# Add tabs
		#self.tabs.addTab(self.groupBoxEqualizer, "Equalizer")
		#self.tabs.addTab(self.groupBoxLogin, "Delay")#

		self.grid = QGridLayout(self)
		self.grid.addWidget(self.groupBoxEqualizer, 0, 0)
		self.setLayout(self.grid)

		self.setWindowTitle("Equalizer")
		self.exec_()

	def _listChanged(self,i):
		if i == 0:
			self.grid.addWidget(self.groupBoxEqualizer, 0, 1)
		elif i == 1:
			self.grid.addWidget(self.groupBoxEqualizer, 0, 1)
	
	def getPreset(self, p):
		return {
			"Flat":                   [ 12.0, 0.0, 0.0, 0.0, 0.0, 0.0,  0.0,  0.0,   0.0,  0.0,  0.0],
			"Classicaal":             [ 12.0, 0.0, 0.0, 0.0, 0.0, 0.0,  0.0, -7.2,  -7.2, -7.2, -9.6],
			"Club":                   [  6.0, 0.0, 0.0, 8.0, 5.6, 5.6,  5.6,  3.2,   0.0,  0.0,  0.0],
			"Dance":                  [  5.0, 9.6, 7.2, 2.4, 0.0, 0.0, -5.6, -7.2,  -7.2,  0.0,  0.0],
			"Full bass":              [  5.0,-8.0, 9.6, 9.6, 5.6, 1.6, -4.0, -8.0, -10.3,-11.2,-11.2],
			"Full bass and trable":   [  4.0, 7.2, 5.6, 0.0,-7.2,-4.8,  1.6,  8.0,  11.2, 12.0, 12.0],
			"Full trable":            [  3.0,-9.6,-9.6,-9.6,-4.0, 2.4, 11.2, 16.0,  16.0, 16.0, 16.7],
			"Headfones":              [  4.0, 4.8,11.2, 5.6,-3.2,-2.4,  1.6,  4.8,   9,6, 12.8, 14.4],
			"Large hall":             [  5.0,10.3,10.3, 5.6, 5.6, 0.0, -4.8, -4.8,  -4.8,  0.0,  0.0],
			"Live":                   [  7.0,-4.8, 0.0, 4.0, 5.6, 5.6,  5.6,  4.0,   2.1,  2.1,  2.1],
			"Party":                  [  6.0, 7.2, 7.2, 0.0, 0.0, 0.0,  0.0,  0.0,   0.0,  7.2,  7.2],
			"Pop":                    [  6.0,-1.6, 1.8, 7.2, 8.0, 5.6,  0.0, -2.4,  -2.1, -1.6, -1.6],
			"Raggae":                 [  8.0, 0.0, 0.0, 0.0,-5.6, 0.0,  6.1,  6.1,   0.0,  0.0,  0.0],
			"Rock":                   [  5.0, 8.0, 4.8,-5.6,-8.0,-3.2,  4.0,  8.8,  11.2, 11.2, 11.2],
			"Ska":                    [  6.0,-2.1, 4.8,-4.0, 0.0, 1.0,  5.6,  8.8,   9.6, 11.2,  9.6],
			"Soft":                   [  5.0, 4.8, 1.6, 0.0,-2.4, 0.0,  4.0,  8.0,   9.6, 11.2, 12.0],
			"Soft rock":              [  7.0, 4.0, 4.0, 2.1, 0.0,-4.0, -5.6, -3.2,  0.0,   2.1,  8.0],
			"Tehno":                  [  5.0, 8.0, 5.6, 0.0,-5.6,-1.8,  0.0,  8.0,   9.6,  9.6,  8.8],
		}[p]
	def _setPreset(self):
		p = self.preset.currentText()
		preset = self.getPreset(p)
		for i, s in enumerate(self.eqSliders):
			if i >= len(preset)-1:
				break
			print(i)
			s.setValue(preset[i]*100)
		
	def genGroupEqualizer(self):
		self.groupBoxEqualizer = QGroupBox("Equalizer")
		
		_eq = self.presenter.getEqualizer()
		print(_eq)
		self.layout = QGridLayout()
		
		lPreset = QLabel("Presets")
		self.preset = QComboBox(self)
		self.preset.addItems([
		"Flat",
		"Classicaal",
		"Club",
		"Dance",
		"Full bass",
		"Full bass and trable",
		"Full trable",
		"Headfones",
		"Large hall",
		"Live",
		"Party",
		"Pop",
		"Raggae",
		"Rock",
		"Ska",
		"Soft",
		"Soft rock",
		"Tehno",
		])
		self.preset.currentIndexChanged.connect(self._setPreset)
		self.layout.addWidget(self.preset, 0, 0)
		#preamp
		slider = QJumpSlider(Qt.Vertical, self)
		slider.setToolTip("Preamp")
		slider.setMaximum(2000)
		slider.setMinimum(-2000)
		slider.setSingleStep(1)
		if math.isnan(_eq["preamp"]):
			slider.setValue(0)
		else:
			slider.setValue(_eq["preamp"]*100)
		self.eqSliders.append(slider)
		slider.valueChanged.connect(lambda state, id = 0 : self.setPositionPreamp(id))
		lable = QLabel("Preamp")
		lableVal = QLabel(str(slider.value()/100)+" dB")
		self.eqLables.append(lableVal)
		self.layout.addWidget(slider, 1, 0)
		self.layout.addWidget(lable, 2, 0)
		self.layout.addWidget(lableVal, 3, 0)
		
		#eq bands
		for i, band in enumerate(self.presenter.player.EQ_BANDS):
			slider = QJumpSlider(Qt.Vertical, self)
			slider.setToolTip(str(band) + " Gz")
			slider.setMaximum(2000)
			slider.setMinimum(-2000)
			slider.setSingleStep(1)
			if math.isnan(_eq["bands"][band]):
				slider.setValue(0)
			else:
				slider.setValue(_eq["bands"][band]*100)
			self.eqSliders.append(slider)
			slider.valueChanged.connect(lambda state, id = i+1 : self.setPositionEq(id))
			lable = QLabel(str(band) + " Gz")
			lableVal = QLabel(str(slider.value()/100)+" dB")
			self.eqLables.append(lableVal)
			self.layout.addWidget(slider, 1, i+2)
			self.layout.addWidget(lable, 2, i+2)
			self.layout.addWidget(lableVal, 3, i+2)
		
		
		rate = self.presenter.getRate()
		slider = QJumpSlider(Qt.Horizontal, self)
		slider.setToolTip("Speed")
		slider.setMaximum(400)
		slider.setMinimum(25)
		slider.setSingleStep(1)
		slider.setValue(int(rate*100))
		self.eqSliders.append(slider)
		slider.valueChanged.connect(lambda state, id = len(self.eqSliders)-1 : self.setPositionRate(id))
		lable = QLabel("Speed")
		lableVal = QLabel(str(slider.value()/100))
		self.eqLables.append(lableVal)
		self.layout.addWidget(slider, 5, 0, 5, 10)
		self.layout.addWidget(lable, 4, 0)
		self.layout.addWidget(lableVal, 4, 1)
		
		
		
		self.groupBoxEqualizer.setLayout(self.layout)

	def setPositionEq(self, id):
		#print(id)
		self.eqSliders[id].setValue(self.eqSliders[id].value())
		self.eqLables[id].setText(str(self.eqSliders[id].value() // 100)+" dB")
		self.presenter.setEqualizer(id, self.eqSliders[id].value() // 100)
		
	def setPositionPreamp(self, id):
		#print(id)
		self.eqSliders[id].setValue(self.eqSliders[id].value())
		self.eqLables[id].setText(str(self.eqSliders[id].value() // 100)+" dB")
		self.presenter.setEqualizerPreamp(self.eqSliders[id].value() // 100)
		
	def setPositionRate(self, id):
		#print(id)
		self.eqSliders[id].setValue(self.eqSliders[id].value())
		self.eqLables[id].setText(str(self.eqSliders[id].value() // 100))
		self.presenter.setRate(self.eqSliders[id].value() // 100)
		
		