from PyQt5.QtCore import QDir, Qt, QUrl, QTimer, pyqtSignal, QObject, QEvent, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, 
		QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import (QMainWindow,QWidget, QPushButton, QAction, QFrame, QMenu, 
	QInputDialog,QTabBar, QStylePainter, QStyleOptionTab, QSystemTrayIcon, QMenu, QGroupBox)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QPainter, QCursor, QMouseEvent
import strings
class QJumpSlider(QSlider):
	def __init__(self, orient, parent = None):
		super(QJumpSlider, self).__init__(orient, parent)

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			if (self.orientation() == Qt.Vertical):
				self.setValue(self.minimum() + ((self.maximum()-self.minimum()) * (self.height()-event.y())) / self.height() ) ;
			else:
				self.setValue(self.minimum() + ((self.maximum()-self.minimum()) * event.x()) / self.width() ) ;
		
		event.accept()
		super(QJumpSlider, self).mousePressEvent(event)

class Frame(QFrame):
	def __init__(self, p):
		super().__init__()
		self.p = p
		self.setAcceptDrops(True)

	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore() 
	newPl = []
	def dropEvent(self, e):
		self.newPl = e.mimeData().text().split("\n")
		self.p.openFile(self.newPl)
		print(e.mimeData().text()) 
		
class HorizontalTabWidget(QTabBar):
	def __init__(self, parent=None, *args, **kwargs):
		self.tabSize = QSize(kwargs.pop('width',100), kwargs.pop('height',30))
		QTabBar.__init__(self, parent, *args, **kwargs)

	def paintEvent(self, event):
		painter = QStylePainter(self)
		option = QStyleOptionTab()
 
		for index in range(self.count()):
			self.initStyleOption(option, index)
			tabRect = self.tabRect(index)
			tabRect.moveLeft(5)
			painter.drawControl(QStyle.CE_TabBarTabShape, option)
			painter.drawText(tabRect, Qt.AlignVCenter |
				Qt.TextDontClip,
				self.tabText(index))
		painter.end()
	def tabSizeHint(self,index):
		return self.tabSize
		
		

class CustomSystemTrayIcon(QSystemTrayIcon):

	def __init__(self, icon, menu, parent=None):
		QSystemTrayIcon.__init__(self, icon, parent)
		self.setContextMenu(menu)
		
	def updateMenu(self, menu):
		self.setContextMenu(menu)
		
class GroupBox(QGroupBox):
	def __init__(self, n, pl):
		super().__init__(n)
		self.pl = pl
		self.setAcceptDrops(True)

	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore() 
			
	def dropEvent(self, e):
		newPl = e.mimeData().text().split("\n")
		print(newPl) 
		self.pl.addItems(newPl)
		
		
		
		
		
		
		
		