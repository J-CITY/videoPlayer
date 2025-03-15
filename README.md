# Sparrow video player

Video player with the ability to translate subtitles on the fly


### Install dependencies
Use VLC lib. Already in repository.
```
pip install pyqt5 pytube pysrt googletrans bencodepy qt-material
```

### Build exe
```
pyinstaller -w -i "./icons/icon.ico" -F main.py
```
Video player (use VLC lib). Can translate sub.


![Screenshot](https://github.com/J-CITY/videoPlayer/blob/master/screens/scr.png)
