from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer
import strings

class MessageBox(QtWidgets.QDialog):
	def __init__(self, text="", parent=None):
		super(MessageBox, self).__init__(parent)
		self.text = text
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.penColor = QtGui.QColor("#333333")
		self.w = 350
		self.h = 100
		self.move(10, 10)
		self.resize(self.w, self.h)
		self.setStyleSheet("background-color: "+strings.BG_COLOR)
		self.timer = QTimer(self)
		self.timer.setInterval(2000)
		self.timer.timeout.connect(self.close)

	def setText(self, text):
		self.hide()
		self.text = text
		self.timer.stop()
		self.timer.start()
		self.show()
		
	def setTextAlways(self, text):
		self.hide()
		self.timer.stop()
		self.text = text
		self.show()
	
	def paintEvent(self, event):
		s = self.size()
		qp = QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
		qp.setPen(self.penColor)

		popup_width = self.w
		popup_height = self.h

		font = QtGui.QFont()
		font.setPixelSize(18)
		#font.setBold(True)
		qp.setFont(font)
		qp.setPen(QtGui.QColor(strings.TEXT_COLOR))
		
		fm = QtGui.QFontMetrics(font)
		pixelsWide = fm.width(self.text)
		while pixelsWide > self.w-10:
			self.text = self.text[:len(self.text)-1]
			pixelsWide = fm.width(self.text)
		
		qp.drawText(int(popup_width/2) - pixelsWide/2, int(popup_height/2)+5, self.text)
		qp.end()
		
