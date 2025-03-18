# Sparrow video player

Video player with the ability to translate subtitles on the fly

It support generate subtitles for video or audio file and torrent download.

![Screenshot](https://github.com/J-CITY/videoPlayer/blob/master/screens/scr.png)


### Install dependencies
Use VLC lib. Already in repository.
```
pip install pyqt5 pytubefix pysrt googletrans bencodepy qt-material
```

#### For subtitles generation need insatll cuda and cudnn-windows-x86_64-8.9.7 dlls put to ctranslate2 folder
Also need install:
```
pip install ctranslate2>=4.0 huggingface_hub>=0.13 tokenizers>=0.13 onnxruntime>=1.14  av>=11 tqdm
```

#### For torrent download need install `peerflix`
```
npm install -g peerflix
```

### Build exe

#### Install `pyinstaller`

```
pip install pyinstaller
```

#### Build .exe

```
pyinstaller main.spec
```

