try:
	import PyQt5
	import pytube
	import pysrt
	import goslate
	import bencodepy
except:
	print("Some important lids are not installed (pyqt5/pytube/pysrt/goslate/bencodepy)")
	exit(1)

from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
		QPushButton, QVBoxLayout, QWidget, QMainWindow,QWidget, QPushButton, 
		QAction, QMenu, QInputDialog, QTextEdit)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QCursor, QIcon
import sys, os
import vlc
import time
import datetime
import ctypes
from pytube import YouTube
from widget import QJumpSlider, CustomSystemTrayIcon, Frame
from equalizer import EqualizerDialog
from playlist import PlaylistDialog
from torrentDialog import TorrentDialog
from delay import DelayDialog
import strings
import threading
from messageBox import MessageBox
import re
from sub import Subtitles
import subprocess
import asyncio
import os.path

class Track:
	codec = ""
	id = ""
	type = ""
	level = ""
	language = ""
	description = ""
	is_external = False
	path = ""

class VideoPlayerWindow(QMainWindow):
	EQ_BANDS = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]

	def __init__(self, inList, parent=None):
		super(VideoPlayerWindow, self).__init__(parent)
		self.setWindowTitle(strings.VIDEOPLAYER_NAME) 
		
		self.torrentProc = None

		self.___onChange = True
		
		# creating a basic vlc instance
		self.instance = vlc.Instance()
		# creating an empty vlc media player
		self.mediaplayer = self.instance.media_player_new()
		vlc.libvlc_video_set_mouse_input(self.mediaplayer, 0)
		vlc.libvlc_video_set_key_input(self.mediaplayer, 0);
		
		self.externalTrack = self.instance.media_player_new()
		self.externalMedia = None
		
		self.media = None #film
		self.videoTracksId = 0
		self.videoTracks = []
		self.audioTracksId = 0
		self.audioTracks = []
		self.subTracksId = 0
		self.subTracks = []
		self.presenter = None
		#equalizer
		self.eq = vlc.libvlc_audio_equalizer_new()
		
		#ratio
		self.ratios = [
		"-1",
		"16:9",
		"4:3",
		"1:1",
		"16:10",
		"5:4",
		"2.21:1",
		"2.35:1",
		"2.39:1"]
		self.ratioId = 0
		
		#playlist
		self.playlistList = []
		self.playlistListId = 0
		
		self.createUI()
		self.menu = None
		self.contextMenu()
		self.setTray()
		#self.messageTray(strings.VIDEOPLAYER_NAME, "Videoplayer is run")
		
		self.isPaused = False
		self.offset = None
		self.isFullScreen = False
		self.isTop = False
		self._popframe = None
		self._popflag = False
		self.controlVisable = True
		
		self.curTime = 0
		self.currentMilliTime = lambda: int(round(time.time() * 1000))
		
		#second subtitles
		self.isSecondSub = False
		self.isTranslateSub = False
		self.isInteractiveTranslateSub = False
		self.secondSub = Subtitles()
		#translate
		######
		
		
		if inList != []:
			self.openFile(inList)
		self.updateFlags()
		self.run()

	def createUI(self):
		self.widget = QWidget(self)
		self.setCentralWidget(self.widget)
		# In this widget, the video will be drawn
		if sys.platform == "darwin": # for MacOS
			from PyQt5.QtWidgets import QMacCocoaViewContainer	
			self.videoframe = QMacCocoaViewContainer(0)
		else:
			self.videoframe = Frame(self)
		#self.videoframe.dropEvent = self.__dropEvent
		
		self.palette = self.videoframe.palette()
		self.palette.setColor (QPalette.Window, QColor(0,0,0))
		self.videoframe.setPalette(self.palette)
		self.videoframe.setAutoFillBackground(True)
		
		####
		
		self.positionslider = QJumpSlider(Qt.Horizontal, self)
		self.positionslider.setToolTip("Position")
		self.positionslider.setMaximum(1000)
		self.positionslider.valueChanged.connect(self.setPosition)
		
		
		font = QFont()
		font.setPointSize(20)
		self.subbox = QHBoxLayout()
		self.subLabel = QLabel()
		self.subLabel.setText("")
		self.subLabel.setFont(font)
		self.subbox.addWidget(self.subLabel)
		self.subLabel.setStyleSheet('QLabel {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+';}')
		self.subLabel.setWordWrap(True)
		self.subLabel.setAlignment(Qt.AlignCenter)
		self.subLabel.setFixedHeight(50)
		items = (self.subbox.itemAt(i) for i in range(self.subbox.count()))
		for w in items:
			if w.widget() != None:
				w.widget().setHidden(True)
				
		
		self.dsubbox = QHBoxLayout()
		self.dsubText = QTextEdit()
		self.dsubText.setReadOnly(True)
		self.dsubText.setText("")
		self.dsubText.setFont(font)
		self.dsubbox.addWidget(self.dsubText)
		self.dsubText.setStyleSheet('QTextEdit {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+';}')
		self.dsubText.setFixedHeight(50)
		items = (self.dsubbox.itemAt(i) for i in range(self.dsubbox.count()))
		for w in items:
			if w.widget() != None:
				w.widget().setHidden(True)
		
		
		self.hbuttonbox = QHBoxLayout()
		self.playbutton = QPushButton(strings.PLAY_BTN)
		#self.playbutton.setIcon(QIcon('icons/play.png'))
		self.hbuttonbox.addWidget(self.playbutton)
		self.playbutton.clicked.connect(self.playPause)
		self.playbutton.setFixedSize(40, 40)
		self.playbutton.setStyleSheet('QPushButton {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+'; border: 1px;} \
			QPushButton:pressed { background-color: '+strings.BG_COLOR_PRESSED+' }')
		
		self.stopbutton = QPushButton(strings.STOP_BTN)
		self.hbuttonbox.addWidget(self.stopbutton)
		self.stopbutton.clicked.connect(self.stop)
		self.stopbutton.setFixedSize(40, 40)
		self.stopbutton.setStyleSheet('QPushButton {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+'; border: 1px;}' \
			'QPushButton:pressed { background-color: '+strings.BG_COLOR_PRESSED+' }')
		
		self.prevbutton = QPushButton(strings.PREV_BTN)
		self.hbuttonbox.addWidget(self.prevbutton)
		self.prevbutton.clicked.connect(self.prev)
		self.prevbutton.setFixedSize(40, 40)
		self.prevbutton.setStyleSheet('QPushButton {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+'; border: 1px;}' \
			'QPushButton:pressed { background-color: '+strings.BG_COLOR_PRESSED+' }')
		
		self.nextbutton = QPushButton(strings.NEXT_BTN)
		self.hbuttonbox.addWidget(self.nextbutton)
		self.nextbutton.clicked.connect(self.next)
		self.nextbutton.setFixedSize(40, 40)
		self.nextbutton.setStyleSheet('QPushButton {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+'; border: 1px;}' \
			'QPushButton:pressed { background-color: '+strings.BG_COLOR_PRESSED+' }')
		
		self.timeLabel = QLabel()
		self.timeLabel.setText("00:00:00")
		self.hbuttonbox.addWidget(self.timeLabel)
		self.timeLabel.setStyleSheet('QLabel {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+';}')
		
		self.lengthLabel = QLabel()
		self.lengthLabel.setText("/ 00:00:00")
		self.hbuttonbox.addWidget(self.lengthLabel)
		self.lengthLabel.setStyleSheet('QLabel {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+';}')
		
		self.hbuttonbox.addStretch(1)
		self.volumeslider = QJumpSlider(Qt.Horizontal, self)
		self.volumeslider.setMaximum(100)
		self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
		self.volumeslider.setToolTip("Volume")
		self.volumeslider.valueChanged.connect(self.setVolume)
		
		self.volumesliderlabel = QLabel()
		self.volumesliderlabel.setText("Vol: "+str(self.mediaplayer.audio_get_volume())+" ")
		self.volumesliderlabel.setStyleSheet('QLabel {background-color: '+strings.BG_COLOR+'; color: '+strings.TEXT_COLOR+';}')
		self.hbuttonbox.addWidget(self.volumesliderlabel)
		self.hbuttonbox.addWidget(self.volumeslider)
		
		self.vboxlayout = QVBoxLayout()
		self.vboxlayout.setSpacing(0)
		self.vboxlayout.addLayout(self.subbox)
		self.vboxlayout.addWidget(self.videoframe)
		self.vboxlayout.addLayout(self.dsubbox)
		self.vboxlayout.addWidget(self.positionslider)
		self.vboxlayout.addLayout(self.hbuttonbox)
		
		self.vboxlayout.setSpacing(2)
		self.vboxlayout.setContentsMargins(0,0,0,0);
		
		self.widget.setLayout(self.vboxlayout)
		
		
		self.timer = QTimer(self)
		self.timer.setInterval(200)
		self.timer.timeout.connect(self.updateUI)
		self.timer.start()
		
		
		self.timerControlHide = QTimer(self)

		
		if strings.CONFIG_USE_NOTIFICATION:
			self.message = MessageBox()
		else:
			self.message = None
		
	def getState(self):
		while True:
			_id = self.playlistListId
			if self.mediaplayer != None:
				_t = self.mediaplayer.get_time()
				_l = self.mediaplayer.get_length()
				#print(_t, _l)
				#print(self.mediaplayer.get_state(), _id, len(self.playlistList), self.playlistList)
				if _t>0 and _l>0 and _t >= _l-100:#self.mediaplayer.get_state() == vlc.State.Ended:
					self.playlistListId += 1
					if self.playlistListId >= len(self.playlistList):
						self.playlistListId = len(self.playlistList)-1#0
				#print(len(self.playlistList), self.playlistListId)
				if _id != self.playlistListId:
					if self.playlistListId < 0:
						self.playlistListId = 0
					self.secondSub.id = 0
					self.openPlayer(self.playlistList[self.playlistListId])
				#for i in self.listPlayer:
				#	print(i)
				
				#D&D
				#if self.videoframe.newPl != []:
				#	self.openFile(self.videoframe.newPl)
				#	self.videoframe.newPl = []
			time.sleep(.200)
	
	def run(self):
		thread = threading.Thread(target=self.getState)
		thread.daemon = True
		thread.start()
	
	def updateUI(self):
		self.___onChange = False
		self.positionslider.setValue(self.mediaplayer.get_position() * 1000)
		
		_t = self.mediaplayer.get_time()
		self.timeLabel.setText(self.msToHMS(_t))
		_t = self.mediaplayer.get_length()
		self.lengthLabel.setText("/ "+self.msToHMS(_t))
		
		v = self.mediaplayer.audio_get_volume()
		self.volumesliderlabel.setText("Vol: "+str(v)+" ")
		
		self.___onChange = True
		if not self.mediaplayer.is_playing():
			if not self.isPaused:
				self.stop()
				
		if self.isSecondSub:
			self.subLabel.setText(self.secondSub.getCurSub(self.mediaplayer.get_time()))
		#print(self.isTranslateSub)
		if self.isTranslateSub:
			sub = self.secondSub.getTranslateCurSub(self.mediaplayer.get_time())
			if sub != None:
				self.subLabel.setText(sub)
		if self.isInteractiveTranslateSub:
			selected = self.dsubText.textCursor().selectedText()
			if selected != "" and self.message.text != selected:
				tr = self.secondSub.translate(selected)
				if tr != None:
					self.message.setTextAlways(tr)
				if not self.isPaused:
					self.playPause()
			if selected == "":
				self.message.hide()
		
			sub = self.secondSub.getCurSub(self.mediaplayer.get_time())
			if sub != None:
				_text = self.dsubText.toPlainText()
				sub = sub.replace("\n", ' ')
				_sub = re.sub(r'<[/a-zA-Z]*>', '', sub)
				if _text != _sub:
					#print(_text, " | ", sub)
					self.dsubText.setHtml("<p style=\"text-align: center\">"+sub+"</p>")
				
				
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Q and e.modifiers() == Qt.ControlModifier:
			self.systemtray.hide()
			self.close()
		
		if e.key() == Qt.Key_F:
			self.fullscreen()
		elif e.key() == Qt.Key_S and e.modifiers() == Qt.ControlModifier:
			self.takeScreenshot()
		elif e.key() == Qt.Key_T and e.modifiers() == Qt.ControlModifier:
			self.onTop()
		#subtitles
		elif e.key() == Qt.Key_V:# next sub
			self.runSub(-1 if self.subTracksId+1 >= len(self.subTracks) else self.subTracksId+1)
		elif e.key() == Qt.Key_C:# off sub
			self.runSub(-1)
		#audio
		elif e.key() == Qt.Key_B:# next audio
			self.runAudio(0 if self.audioTracksId+1 >= len(self.audioTracks) else self.audioTracksId+1)
		elif e.key() == Qt.Key_N:# off audio
			self.offAudio()
		#ratio
		elif e.key() == Qt.Key_H:
			self.setNextRatio()
		#play control
		elif e.key() == Qt.Key_P or e.key() == Qt.Key_Space:
			self.playPause()
		elif e.key() == Qt.Key_S:
			self.stop()
		elif e.key() == Qt.Key_Comma and e.modifiers() == Qt.ControlModifier:
			self.moveLessMs()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Period and e.modifiers() == Qt.ControlModifier:
			self.moveGreaterMs()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Comma:
			self.moveLess()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Period:
			self.moveGreater()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Less:
			self.prev()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Greater:
			self.next()
			self.secondSub.id = 0
		elif e.key() == Qt.Key_Equal:
			self.volumeUp()
		elif e.key() == Qt.Key_Minus:
			self.volumeDown()
		elif e.key() == Qt.Key_M:
			self.mute()
	
	def mouseDoubleClickEvent(self, event):
		self.fullscreen()
	
	def mousePressEvent(self, event):
		if event.button() == Qt.RightButton:
			self.popUpMenu()
			self.offset = None
		elif event.button() == Qt.MidButton:
			self.playPause()
			self.offset = None
		else:
			self.offset = event.pos()
	def mouseMoveEvent(self, event):
		if event.button() != Qt.RightButton and event.button() != Qt.MidButton  and self.offset != None and not self.isFullScreen:
			
			if event.localPos().y() * 100 / self.height() > 80:
				return
			x=event.globalX()
			y=event.globalY()
			x_w = self.offset.x()
			y_w = self.offset.y()
			self.move(x-x_w, y-y_w)
	
	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		pass
	
	def wheelEvent(self, event):
		p = event.angleDelta()
		if p.y() < 0:
			self.volumeDown()
		elif p.y() > 0:
			self.volumeUp()
			
	def hideEvent(self, event):
		self.hide()
		#self.messageTray(strings.VIDEOPLAYER_NAME, "Hide application")
	
	def showTrayEvent(self, ev):
		if ev == CustomSystemTrayIcon.Trigger:
			self.show()
	
	def eventFilter(self, source, event):
		if event.type() == QEvent.MouseMove:
			if event.buttons() == Qt.NoButton:
				if self.isFullScreen:
					if not self.controlVisable:
						self.hideControl(True)
					self.curTime = self.currentMilliTime()
					self.videoframe.unsetCursor()
					self.timerControlHide.singleShot(2000, lambda: self.hideControl(False, auto=True))
					self.timerControlHide.start()
			else:
				pass # do other stuff
		return QMainWindow.eventFilter(self, source, event)
	
	def hideControl(self, hide=None, auto=False):
		if auto:
			if not self.isFullScreen:
				return
			if self.currentMilliTime() - self.curTime < 1980:
				#print(self.currentMilliTime(), self.curTime, self.currentMilliTime() - self.curTime)
				return
			self.videoframe.setCursor(Qt.BlankCursor)
		self.controlVisable = not self.controlVisable if hide == None else hide
		self.positionslider.setHidden(not self.controlVisable)
		items = (self.hbuttonbox.itemAt(i) for i in range(self.hbuttonbox.count()))
		for w in items:
			if w.widget() != None:
				w.widget().setHidden(not self.controlVisable)
	
	def setTray(self):
		if self.menu == None:
			return
		self.systemtray = CustomSystemTrayIcon(QIcon('iconst/bell.png'), self.contextMenu(True), self)
		self.systemtray.activated.connect(self.showTrayEvent)
		self.systemtray.show()
		
	def messageTray(self, title, message):
		self.systemtray.showMessage(title, message, msecs=1500)
	
	def updateTray(self):
		if self.menu == None:
			return
		self.systemtray.updateMenu(self.menu)
	
	def playById(self, id):
		self.playlistListId = id
		self.openPlayer(self.playlistList[id])
	
	def setTracks(self):
		self.videoTracks = []
		self.audioTracks = []
		self.subTracks = []
		if self.media == None:
			return None
		mediaTrack_pp = ctypes.POINTER(vlc.MediaTrack)()
		n = vlc.libvlc_media_tracks_get(self.media, ctypes.byref(mediaTrack_pp))
		info = ctypes.cast(mediaTrack_pp, ctypes.POINTER(ctypes.POINTER(vlc.MediaTrack) * n))
		try:
			contents = info.contents
		except ValueError:
			return None
		tracks = ( contents[i].contents for i in range(len(contents)) )
		for t in tracks:
			track = Track()
			track.id = t.id
			track.codec = t.codec
			track.type = t.type
			track.level = t.level
			track.language = t.language
			track.description = t.description
			if track.type == vlc.TrackType.video:
				self.videoTracks.append(track)
			if track.type == vlc.TrackType.audio:
				self.audioTracks.append(track)
			if track.type == vlc.TrackType.text:
				self.subTracks.append(track)
			
	def updateSupTracks(self):
		maxId = 0
		for t in self.subTracks:
			maxId = maxId if maxId > t.id else t.id
		#self.subTracks = []
		if self.media == None:
			return None
		mediaTrack_pp = ctypes.POINTER(vlc.MediaTrack)()
		n = vlc.libvlc_media_tracks_get(self.media, ctypes.byref(mediaTrack_pp))
		info = ctypes.cast(mediaTrack_pp, ctypes.POINTER(ctypes.POINTER(vlc.MediaTrack) * n))
		try:
			contents = info.contents
		except ValueError:
			return None
		tracks = ( contents[i].contents for i in range(len(contents)) )
		
		for t in tracks:
			flag = False
			for tt in self.subTracks:
				if tt.id == t.id:
					flag = True
					break
			if flag:
				continue
			track = Track()
			track.id = t.id
			track.codec = t.codec
			track.type = t.type
			track.level = t.level
			track.language = t.language
			track.description = t.description
			if t.type == vlc.TrackType.text:
				self.subTracks.append(track)
			

	def playPause(self):
		if self.mediaplayer.is_playing():
			self.mediaplayer.pause()
			#self.listPlayer.pause()
			self.playbutton.setText(strings.PLAY_BTN)
			self.isPaused = True
			if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
				self.externalTrack.pause()
		else:
			self.mediaplayer.play()
			if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
				self.externalTrack.play()
				self.externalTrack.set_position(self.mediaplayer.get_position())
			#self.listPlayer.play()
			self.playbutton.setText(strings.PAUSE_BTN)
			#self.timer.start()
			self.isPaused = False
		
	def stop(self):
		"""Stop player
		"""
		self.mediaplayer.stop()
		if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.stop()
		#self.listPlayer.stop()
		self.playbutton.setText(strings.PLAY_BTN)
	
	def next(self):
		_id = self.playlistListId
		self.playlistListId += 1
		if self.playlistListId >= len(self.playlistList):
			self.playlistListId = len(self.playlistList)-1
		if len(self.playlistList) > 0 and _id != self.playlistListId:
			self.openPlayer(self.playlistList[self.playlistListId])
		if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.stop()
	def prev(self):
		_id = self.playlistListId
		self.playlistListId -= 1
		if self.playlistListId < 0:
			self.playlistListId = 0
		if len(self.playlistList) > 0 and _id != self.playlistListId:
			self.openPlayer(self.playlistList[self.playlistListId])
		if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.stop()
	
	def setVolume(self, Volume):
		self.mediaplayer.audio_set_volume(Volume)
		if len(self.audioTracks) > 0 and self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.audio_set_volume(Volume)
		
		if self.message != None:
			self.message.setText("Vol: "+str(Volume))
		
	def setPosition(self, position):
		if self.___onChange:
			self.mediaplayer.set_position(position / 1000.0)
			if self.audioTracks[self.audioTracksId].is_external:
				self.externalTrack.set_position(position / 1000.0)
			self.secondSub.id = 0
				
	def setPosition(self):
		if self.___onChange:
			position = self.positionslider.value()
			self.mediaplayer.set_position(position / 1000.0)
			if self.audioTracks[self.audioTracksId].is_external:
				self.externalTrack.set_position(position / 1000.0)
			self.secondSub.id = 0
	
	def moveLessMs(self):
		_p = self.mediaplayer.get_time()
		_p -= 1000
		if _p < 0:
			_p = 0
		self.mediaplayer.set_time(_p)
		if self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.set_time(_p)
		
	def moveGreaterMs(self):
		_p = self.mediaplayer.get_time()
		_p += 1000
		if _p >= self.mediaplayer.get_length():
			_p = self.mediaplayer.get_length()-10
		self.mediaplayer.set_time(_p)
		if self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.set_time(_p)
	
	def moveLess(self):
		_p = self.mediaplayer.get_position() * 1000.0
		_p -= 10
		if _p < 0:
			_p = 0
		self.mediaplayer.set_position(_p / 1000.0)
		if self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.set_position(_p / 1000.0)
		
	def moveGreater(self):
		_p = self.mediaplayer.get_position() * 1000.0
		_p += 10
		if _p >= 1000:
			_p = 1000
		self.mediaplayer.set_position(_p / 1000.0)
		if self.audioTracks[self.audioTracksId].is_external:
			self.externalTrack.set_position(_p / 1000.0)
	
	def mute(self):
		v = self.mediaplayer.audio_get_mute()
		if int(v) == -1:
			return
		if v:
			self.mediaplayer.audio_set_mute(False)
			self.volumesliderlabel.setText("Vol: "+str(self.mediaplayer.audio_get_volume())+" ")
		else:
			self.mediaplayer.audio_set_mute(True)
			self.volumesliderlabel.setText("Mute")
	def volumeUp(self):
		v = self.mediaplayer.audio_get_volume()
		v = v+5 if v+5 < 100 else 100
		self.setVolume(v)
		self.volumeslider.setValue(v)
		self.volumesliderlabel.setText("Vol: "+str(v)+" ")
	def volumeDown(self):
		v = self.mediaplayer.audio_get_volume()
		v = v-5 if v-5 >= 0 else 0
		self.setVolume(v)
		self.volumeslider.setValue(v)
		self.volumesliderlabel.setText("Vol: "+str(v)+" ")
	
	def onTop(self):
		self.isTop = not self.isTop
		self.updateFlags()
	
	def fullscreen(self):
		self.isFullScreen = not self.isFullScreen
		if self.isFullScreen:
			self.isTop = False
			self.updateFlags()
			self.showFullScreen()
			self.hideControl(False)
			self.videoframe.setCursor(Qt.BlankCursor)
		else:
			self.showNormal()#showMaximized()
			self.hideControl(True)
			self.videoframe.unsetCursor()
	
	def takeScreenshot(self):
		import pathlib
		path = os.path.dirname(os.path.abspath(__file__))
		now = datetime.datetime.now()
		filename = now.strftime("%Y-%m-%d-%H-%M-%S-")+str(now.microsecond)+".png"
		wh = self.mediaplayer.video_get_size()
		pathlib.Path(path+"/screenshots").mkdir(parents=False, exist_ok=True) 
		self.mediaplayer.video_take_snapshot(0, path+"/screenshots/"+filename, wh[0], wh[1])
	
	def setNextRatio(self):
		self.ratioId = 0 if self.ratioId+1 >= len(self.ratios) else self.ratioId+1
		self.mediaplayer.video_set_aspect_ratio(self.ratios[self.ratioId])
	def setRatio(self, i):
		self.ratioId = i
		#print(self.ratios[self.ratioId])
		self.mediaplayer.video_set_aspect_ratio(self.ratios[self.ratioId])
	
	def get_audio_track(self):
		return self.mediaplayer.audio_get_track_description()[self.mediaplayer.audio_get_track()]
		
	def increment_audio_track(self, value):
		current_audio_track = self.mediaplayer.audio_get_track()
		if self.mediaplayer.audio_get_track_count()-1 == 0:
			return (0, "No audio tracks found")
		elif current_audio_track == self.mediaplayer.audio_get_track_count()-1 and value > 0:
			self.mediaplayer.audio_set_track(1)
		elif current_audio_track == 0 and value < 0:
			self.mediaplayer.audio_set_track(self.mediaplayer.audio_get_track_count()-1)
		else:
			self.mediaplayer.audio_set_track(current_audio_track+value)
		return self.get_audio_track()
	
	def openFile(self, filenames=None):
		if filenames is None or filenames == []:
			return
		# create the media
		self.playlistList = filenames
		self.playlistListId = 0
		self.openPlayer(filenames[0])

	async def playTorrentSubprocess(self, id, magnetLink, torrentPath):
		if not self.torrentProc is None:
			self.torrentProc.stdout.close()
			self.torrentProc.kill()
			self.torrentProc = None
		
		_torrentPath = magnetLink if torrentPath == '' else torrentPath
		if _torrentPath == '':
			return
		print('cmd: ', 'peerflix "'+_torrentPath+'" -i ' + str(id))
		self.torrentProc = await asyncio.create_subprocess_shell(
			'peerflix "'+_torrentPath+'" -i ' + str(id),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE, shell=True)
	
		fileName = ''
		rootPath = ''
		#b=False
		while self.torrentProc.returncode is None:
			data = await self.torrentProc.stdout.readline()
			#if not data:
			line = data.decode('utf-8').strip()
			print(data)
			ostrs = line.split('\n')

			for ostr in ostrs:
				#print(ostr, ostr.find('info streaming '))
				if ostr.find('info streaming ') != -1:
					fileName = ostr[15:]
					print(fileName)
				if ostr.find('info path ') != -1:
					rootPath = ostr[10:]
					print(rootPath)
			if fileName != '' and rootPath != '':#and not b:
				time.sleep(5)
				#b=True
				self.getListOfFiles(rootPath, fileName)
				break
			asyncio.sleep(.99)
		
		subprocess.Popen('peerflix "'+_torrentPath+'" -i ' + str(id), close_fds=True, shell=True)
		
		#os.spawnl(os.P_DETACH, 'peerflix "'+_torrentPath+'" -i ' + str(id),"DUMMY")
		#time.sleep(5) 
		#self.getListOfFiles(rootPath, fileName)
		#self.close()
	
	def getListOfFiles(self, dirName, fileName):
		listOfFile = os.listdir(dirName)
		for entry in listOfFile:
			fullPath = os.path.join(dirName, entry)
			if os.path.isdir(fullPath):
				self.getListOfFiles(fullPath, fileName)
			else:
				if entry == fileName:
					print("OPEN FILE: ", fullPath)
					self.playlistList = []
					self.openFile([fullPath])
					return
	
	def openPlayer(self, fname):
		self.media = self.instance.media_new(fname)
		
		self.mediaplayer.set_media(self.media)
		# parse the metadata of the file
		self.media.parse()
		# set the title of the track as window title
		self.setWindowTitle(self.media.get_meta(0))
		if sys.platform.startswith('linux'):
			self.mediaplayer.set_xwindow(self.videoframe.winId())
		elif sys.platform == "win32": # for Windows
			self.mediaplayer.set_hwnd(self.videoframe.winId())
		elif sys.platform == "darwin": # for MacOS
			self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
		self.playPause()
		self.setTracks()
		
		if self.message != None:
			pathList = fname.split("/")
			if len(pathList) == 1:
				pathList = fname.split("\\")
			_fn = pathList[len(pathList)-1]
			self.message.setText("Play: "+_fn)
		
		self.systemtray.updateMenu(self.contextMenu())
		
	def msToHMS(self, millis):
		millis = int(millis)
		seconds=(millis/1000)%60
		seconds = int(seconds)
		minutes=(millis/(1000*60))%60
		minutes = int(minutes)
		hours=(millis/(1000*60*60))%24
		hours=int(hours)
		return (str(hours) if hours > 9 else "0"+str(hours)) +":"+\
			(str(minutes) if minutes > 9 else "0"+str(minutes))+":"+\
			(str(seconds) if seconds > 9 else "0"+str(seconds))
	
	def updateFlags(self):
		#print(bool(self.windowFlags() & Qt.MSWindowsFixedSizeDialogHint))
		#print(bool(self.windowFlags() & Qt.X11BypassWindowManagerHint))
		#print(bool(self.windowFlags() & Qt.FramelessWindowHint))
		#print(bool(self.windowFlags() & Qt.WindowTitleHint))
		#print(bool(self.windowFlags() & Qt.WindowSystemMenuHint))
		#print(bool(self.windowFlags() & Qt.WindowMinimizeButtonHint))
		#print(bool(self.windowFlags() & Qt.WindowMaximizeButtonHint))
		#print(bool(self.windowFlags() & Qt.WindowCloseButtonHint))
		#print(bool(self.windowFlags() & Qt.WindowContextHelpButtonHint))
		#print(bool(self.windowFlags() & Qt.WindowShadeButtonHint))
		#print(bool(self.windowFlags() & Qt.WindowStaysOnTopHint))
		#print(bool(self.windowFlags() & Qt.WindowStaysOnBottomHint))
		#print(bool(self.windowFlags() & Qt.CustomizeWindowHint))
		#print("--------------------------")
		
		#self.setWindowFlags(Qt.WindowStaysOnTopHint)
		flags = Qt.WindowFlags()
		#flags = flags | Qt.FramelessWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint\
		#	| Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
		#flags | Qt.FramelessWindowHint
		if self.isTop:
			flags = flags | Qt.WindowStaysOnTopHint
		#flags = flags | Qt.Window
		self.setWindowFlags(flags)
		pos = self.pos()
		if pos.x() < 0:
			pos.setX(0)
		if pos.y() < 0:
			pos.setY(0)
		self.move(pos)
		self.show()
	
	def runSub(self, i):
		self.subTracksId = i
		if self.subTracksId < 0:
			print("SUB OFF")
			self.mediaplayer.video_set_spu(self.subTracksId)
		elif self.subTracks[self.subTracksId].is_external:
			self.mediaplayer.video_set_subtitle_file(str(self.subTracks[self.subTracksId].path))
		else:
			self.mediaplayer.video_set_spu(self.subTracks[self.subTracksId].id)
			print(self.mediaplayer.video_get_spu())
			
	def runSub2(self, i):
		if i < 0 or i >= len(self.subTracks):
			return
		if self.subTracks[i].is_external:
			self.isSecondSub = True
			self.isTranslateSub = False
			items = (self.subbox.itemAt(i) for i in range(self.subbox.count()))
			for w in items:
				if w.widget() != None:
					w.widget().setHidden(False)
			self.subTracksId2 = i
			self.secondSub.open(self.subTracks[i].path)
		else:
			self.offSub2()
	
	def translateSub(self):
		if self.subTracksId < 0 or self.subTracksId >= len(self.subTracks):
			return
		if self.subTracks[self.subTracksId].is_external:
			self.isSecondSub = False
			self.isTranslateSub = not self.isTranslateSub
			if self.isTranslateSub:
				items = (self.subbox.itemAt(i) for i in range(self.subbox.count()))
				for w in items:
					if w.widget() != None:
						w.widget().setHidden(False)
				self.secondSub.open(self.subTracks[self.subTracksId].path)
			else:
				items = (self.subbox.itemAt(i) for i in range(self.subbox.count()))
				for w in items:
					if w.widget() != None:
						w.widget().setHidden(True)
			
	def translateDynamicSub(self):
		if self.subTracksId < 0 or self.subTracksId >= len(self.subTracks):
			return
		if self.subTracks[self.subTracksId].is_external:
			self.mediaplayer.video_set_spu(-1)
			self.isInteractiveTranslateSub = not self.isInteractiveTranslateSub
			if self.isInteractiveTranslateSub:
				items = (self.dsubbox.itemAt(i) for i in range(self.dsubbox.count()))
				for w in items:
					if w.widget() != None:
						w.widget().setHidden(False)
				self.secondSub.open(self.subTracks[self.subTracksId].path)
			else:
				items = (self.dsubbox.itemAt(i) for i in range(self.dsubbox.count()))
				for w in items:
					if w.widget() != None:
						w.widget().setHidden(True)
			
	def offSub(self):
		self.subTracksId = -1
		self.mediaplayer.video_set_spu(self.subTracksId)
		
	def offSub2(self):
		self.isSecondSub = False
		self.isTranslateSub = False
		items = (self.subbox.itemAt(i) for i in range(self.subbox.count()))
		for w in items:
			if w.widget() != None:
				w.widget().setHidden(True)
		
	def runAudio(self, i):
		_i = self.audioTracksId
		self.audioTracksId = i
		
		if self.audioTracks[self.audioTracksId].is_external:
			self.mediaplayer.audio_set_mute(True)
			self.externalMedia = self.instance.media_new(self.audioTracks[self.audioTracksId].path)
			self.externalTrack.set_media(self.externalMedia)
			
			#self.externalTrack.play()
			
			#self.playPause()
			#self.externalTrack.set_position(self.mediaplayer.get_position())
			if self.mediaplayer.is_playing() != 0:
				self.externalTrack.play()
				self.externalTrack.set_position(self.mediaplayer.get_position())
		else:
			self.mediaplayer.audio_set_mute(False)
			self.externalTrack.stop()
			self.mediaplayer.audio_set_track(self.audioTracks[self.audioTracksId].id)
			
	def offAudio(self):
		self.audioTracksId = -1
		self.mediaplayer.audio_set_track(self.audioTracksId)
	
	def runVideo(self, track, i):
		self.videoTracksId = i
		#print(track, i)
		if track.is_external:
			pass
		else:
			self.mediaplayer.video_set_track(track.id)
			
	def offVideo(self):
		self.videoTracksId = -1
		self.mediaplayer.video_set_track(self.videoTracksId)
	
	def contextMenu(self, needHideToTray=False):
		self.menu = QMenu(self)
		if needHideToTray:
			controlAct = QAction('Hide to tray', self)
			controlAct.triggered.connect(self.hideEvent)
			self.menu.addAction(controlAct)
			self.menu.addSeparator()
		
		controlAct = QAction('Play/Pause', self)
		controlAct.triggered.connect(self.playPause)
		self.menu.addAction(controlAct)
		
		controlAct = QAction('Stop', self)
		controlAct.triggered.connect(self.stop)
		self.menu.addAction(controlAct)
		
		controlAct = QAction('Next', self)
		controlAct.triggered.connect(self.next)
		self.menu.addAction(controlAct)
		
		controlAct = QAction('Prev', self)
		controlAct.triggered.connect(self.prev)
		self.menu.addAction(controlAct)
		
		controlAct = QAction('Move ->', self)
		controlAct.triggered.connect(self.moveGreater)
		self.menu.addAction(controlAct)
		
		controlAct = QAction('Move <-', self)
		controlAct.triggered.connect(self.moveLess)
		self.menu.addAction(controlAct)
		self.menu.addSeparator()
		
		subAction = QMenu('Subtitles 1', self)
		
		externalSubAct = QAction('External subtitles', self)
		externalSubAct.triggered.connect(self.externalSub)
		subAction.addAction(externalSubAct)
		subAction.addSeparator()
		
		translateSubAct = QAction('Translate', self.menu)
		translateSubAct.triggered.connect(self.translateSub)
		subAction.addAction(translateSubAct)
		subAction.addSeparator()
		
		translateSubAct = QAction('Dynamic Translate', self.menu)
		translateSubAct.triggered.connect(self.translateDynamicSub)
		subAction.addAction(translateSubAct)
		subAction.addSeparator()
		
		for i, s in enumerate(self.subTracks):
			#if not self.subTracks[i].is_external:
			subAct = QAction(str((s.language if s.language != None else str(i)+" - track")), self)
			subAct.triggered.connect(lambda  state, _i = i: self.runSub(_i))
			subAction.addAction(subAct)
		offSubAct = QAction("off", self)
		offSubAct.triggered.connect(self.offSub)
		subAction.addAction(offSubAct)
		
		subAction.addSeparator()
		delaySubAct = QAction("delay", self)
		delay = self.mediaplayer.video_get_spu_delay()
		delaySubAct.triggered.connect(lambda state, d=delay: self.delayDialog(d, "AUDIO"))
		subAction.addAction(delaySubAct)
		##################
		subAction2 = QMenu('Subtitles 2', self)
		for i, s in enumerate(self.subTracks):
			if self.subTracks[i].is_external:
				subAct = QAction(str((s.language if s.language != None else str(i)+" - track")), self)
				subAct.triggered.connect(lambda  state, _i = i: self.runSub2(_i))
				subAction2.addAction(subAct)
		offSubAct2 = QAction("off", self)
		offSubAct2.triggered.connect(self.offSub2)
		subAction2.addAction(offSubAct2)
		
		#subAction.addSeparator()
		#delaySubAct = QAction("delay", self)
		#delay = self.mediaplayer.video_get_spu_delay()
		#delaySubAct.triggered.connect(lambda state, d=delay: self.delayDialog(d, "AUDIO"))
		#subAction.addAction(delaySubAct)
		######################
		audioAction = QMenu('Audio', self)
		externalAudioAct = QAction('External audio', self)
		externalAudioAct.triggered.connect(self.externalAudio)
		audioAction.addAction(externalAudioAct)
		audioAction.addSeparator()
		for i, s in enumerate(self.audioTracks):
			audioAct = QAction(str((s.language if s.language != None else str(i)+" - track")), self)
			audioAct.triggered.connect(lambda state, _i=i: self.runAudio( _i))
			audioAction.addAction(audioAct)
		offAudioAct = QAction("off", self)
		offAudioAct.triggered.connect(self.offAudio)
		audioAction.addAction(offAudioAct)
		audioAction.addSeparator()
		
		audioAction.addSeparator()
		delayAudioAct = QAction("delay", self)
		delay = self.mediaplayer.audio_get_delay()
		delayAudioAct.triggered.connect(lambda state, d=delay: self.delayDialog(d, "AUDIO"))
		audioAction.addAction(delayAudioAct)
		
		eqAudioAct = QAction("Effects", self)
		eqAudioAct.triggered.connect(self.dialogEffectAudio)
		audioAction.addAction(eqAudioAct)
		audioAction.addSeparator()
		
		eqAudioAct = QAction("Vol up", self)
		eqAudioAct.triggered.connect(self.volumeUp)
		audioAction.addAction(eqAudioAct)
		
		eqAudioAct = QAction("Vol down", self)
		eqAudioAct.triggered.connect(self.volumeDown)
		audioAction.addAction(eqAudioAct)
		
		eqAudioAct = QAction("Mute", self)
		eqAudioAct.triggered.connect(self.mute)
		audioAction.addAction(eqAudioAct)

		###############################
		videoAction = QMenu('Video', self)
		
		for i, s in enumerate(self.videoTracks):
			videoAct = QAction(str((s.language if s.language != None else str(i)+" - track")), self)
			videoAct.triggered.connect(lambda state, _s=s, _i=i: self.runVideo(_s, _i))
			videoAction.addAction(videoAct)
		offVideoAct = QAction("off", self)
		offVideoAct.triggered.connect(self.offVideo)
		videoAction.addAction(offVideoAct)
		videoAction.addSeparator()
		
		ratioAction = QMenu('Set ratio', self)
		for i, s in enumerate(self.ratios):
			if s == "-1":
				s = "default"
			videoAct = QAction(str(s), self)
			videoAct.triggered.connect(lambda state, _i=i: self.setRatio(_i))
			ratioAction.addAction(videoAct)
		videoAction.addMenu(ratioAction)
		
		videoAct = QAction("Screenshot", self)
		videoAct.triggered.connect(self.takeScreenshot)
		videoAction.addAction(videoAct)
		
		videoAct = QAction("Fullscreen", self)
		videoAct.triggered.connect(self.fullscreen)
		videoAction.addAction(videoAct)
		
		videoAct = QAction("On top", self)
		videoAct.triggered.connect(self.onTop)
		videoAction.addAction(videoAct)
		
		#########################
		sourceAction = QMenu('Source', self)
		openfileAct = QAction("Open file", self)
		openfileAct.triggered.connect(self.openFileAct)
		sourceAction.addAction(openfileAct)
		
		openfileAct = QAction("Open files", self)
		openfileAct.triggered.connect(self.openFilesAct)
		sourceAction.addAction(openfileAct)
		
		openurlAct = QAction("Open url", self)
		openurlAct.triggered.connect(self.openUrlAct)
		sourceAction.addAction(openurlAct)
		#externalSubAct = QAction('External subtitles', self)
		#renameAction.triggered.connect(lambda: self.renameSlot(event))
		
		playlistAct = QAction('Playlist', self)
		playlistAct.triggered.connect(self.dialogPlaylist)

		torrentAct = QAction('Torrent', self)
		torrentAct.triggered.connect(self.dialogTorrent)
		
		
		closeAct = QAction('Close', self)
		closeAct.triggered.connect(lambda: (self.systemtray.hide(), self.close()))
		
		self.menu.addMenu(subAction)
		self.menu.addMenu(subAction2)
		self.menu.addMenu(audioAction)
		self.menu.addMenu(videoAction)
		self.menu.addMenu(sourceAction)
		self.menu.addAction(playlistAct)
		self.menu.addAction(torrentAct)
		self.menu.addSeparator()
		self.menu.addAction(closeAct)
		return self.menu
	
	
	def delayDialog(self, delay, type):
		dialog = DelayDialog(self.presenter, delay, type)
		
	def setDelay(self, delay, type):
		if type == "SUBTITLES":
			self.mediaplayer.video_set_spu_delay(delay)
		elif type == "AUDIO":
			if self.audioTracks[self.audioTracksId].is_external:
				self.externalTrack.audio_set_delay(delay)
				self.mediaplayer.audio_set_delay(delay)
			else:
				self.mediaplayer.audio_set_delay(delay)
	
	def externalSub(self):
		path = os.path.dirname(os.path.abspath(__file__))
		filter = "Sub (*.aqt *.cvd *.dks *.jss *.sub *.ttxt *.mpl *.txt *.pjs *.psb *.rt *.smi *.ssf *.srt *.ssa *.svcder *.usf *.idx )"
		fname = QFileDialog.getOpenFileName(self, 'Open file', path, filter)[0]
		if fname == "":
			return
		newT = Track()
		newT.codec = ""
		newT.id = 100+len(self.subTracks)
		newT.type = vlc.TrackType.text
		newT.level = None
		newT.language = None
		newT.description = "Externel sub"
		newT.is_external = True
		newT.path = fname
		self.subTracks.append(newT)
		self.updateSupTracks()
		
	def externalAudio(self):
		path = os.path.dirname(os.path.abspath(__file__))
		filter = "Audio (*.ac3 *.mp3 *.wav)"
		fname = QFileDialog.getOpenFileName(self, 'Open file', path, filter)[0]
		if fname == "":
			return
		newT = Track()
		newT.codec = ""
		newT.id = -11
		newT.type = vlc.TrackType.audio
		newT.level = None
		newT.language = None
		newT.description = "Externel audio"
		newT.is_external = True
		newT.path = fname
		self.audioTracks.append(newT)
	
	def popUpMenu(self):
		self.contextMenu()
		self.menu.popup(QCursor.pos())
		
	def setPlaylist(self, pl):
		self.openFile(pl)
		self.playlistListId = 0
		
	def dialogEffectAudio(self):
		self.effectDialog = EqualizerDialog(self.presenter)
		
	def dialogPlaylist(self):
		self.playlistDialog = PlaylistDialog(self.presenter, self.playlistList)
	
	def dialogTorrent(self):
		self.torrentDialog = TorrentDialog(self.presenter)

	def openFileAct(self):
		path = os.path.dirname(os.path.abspath(__file__))
		filter = "Video (*.avi *.wmv *.mov *.mkv *.3gp *.m4v *.mp4)"
		fname = QFileDialog.getOpenFileName(self, 'Open file', path, filter)[0]
		if fname == "":
			return
		
		self.playlistList = []
		self.openFile([fname])
		
	def openFilesAct(self):
		path = os.path.dirname(os.path.abspath(__file__))
		filter = "Video (*.avi *.wmv *.mov *.mkv *3gp)"
		fnames = QFileDialog.getOpenFileNames(self, 'Open files', path, filter)
		if fnames == []:
			return
		self.playlistList = []
		self.openFile(fnames[0])
		#self.listWidget.addItems(fnames[0])

	def openUrlAct(self):
		text, ok = QInputDialog.getText(self, 'Input Dialog',
			'Enter URL:')
		if ok and str(text) != "":
			url = str(text)
			#if "youtu" in url:
			try:
				_url = YouTube(url).streams.first().url
				print(_url)
				self.playlistList = []
				self.openFile([_url])
				return
			except:
				print("Not YT")
			
			try:
				if (url.find('http') != -1):
					self.playlistList = []
					self.openFile([url])
				return
			except:
				print("Not http link")
			return
	def setPresenter(self, p):
		self.presenter = p
	
	def getEqualizer(self):
		result = {'bands': {}, 'preamp': vlc.libvlc_audio_equalizer_get_preamp(self.eq)}
		for i, band in enumerate(self.EQ_BANDS):
			result['bands'][band]=vlc.libvlc_audio_equalizer_get_amp_at_index(self.eq, i)
		return result
	
	def setEqualizer(self, band, value):
		vlc.libvlc_audio_equalizer_set_amp_at_index(self.eq, band, int(value))
		vlc.libvlc_media_player_set_equalizer(self.mediaplayer, self.eq)

	def setEqualizerPreamp(self, value):
		vlc.libvlc_audio_equalizer_set_preamp(self.eq, int(value))
		vlc.libvlc_media_player_set_equalizer(self.mediaplayer, self.eq)
	

from presenter import Presenter

def printHelp():
	print(strings.HELP)

if __name__ == '__main__':
	inList = []
	lenargs = len(sys.argv)
	if lenargs == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
		printHelp()
		sys.exit()
	elif lenargs > 1:
		inList = sys.argv[1:]
	
	import pathlib
	path = os.path.dirname(os.path.abspath(__file__))+"/screenshots"
	pathlib.Path(path).mkdir(parents=True, exist_ok=True) 
	

	app = QApplication(sys.argv)
	app.setStyleSheet('QMainWindow{background-color: '+strings.BG_COLOR+';border: 0px solid black;}')
	
	p = Presenter()
	
	player = VideoPlayerWindow(inList)
	player.setPresenter(p)
	p.setPlayer(player)
	
	player.resize(640, 480)
	player.show()
	
	app.installEventFilter(player)
	sys.exit(app.exec_())
	