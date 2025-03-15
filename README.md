# videoPlayer

deps:
pyqt5
pytube
pysrt
goslate
bencodepy
qt-material

Build exe

pyinstaller -w -i "./icons/icon.ico" -F main.py

Video player (use VLC lib). Can translate sub.

Dependences:

pip install pyqt5 goslate pysrt python-libtorrent

for torrents need install peerflix and replace index.js and app.js

![Screenshot](https://github.com/J-CITY/videoPlayer/blob/master/scr.png)
