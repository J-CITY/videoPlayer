
import libtorrent as lt
import ffmpeg

path = './Форсаж 10 Fast X (Луи Летерье Louis Leterrier) [2023, США, Боевик, криминал, детектив, WEB-DLRip] MVO (TVShows) + Original + S [rutracker-6374937].torrent'
#path = 'magnet:?xt=urn:btih:AF377C46AB077F4F431958885EB7534B2B175E2B&tr=http%3A%2F%2Fbt2.t-ru.org%2Fann%3Fmagnet&dn=%D0%A4%D0%BE%D1%80%D1%81%D0%B0%D0%B6%2010%20%2F%20Fast%20X%20(%D0%9B%D1%83%D0%B8%20%D0%9B%D0%B5%D1%82%D0%B5%D1%80%D1%8C%D0%B5%20%2F%20Louis%20Leterrier)%20%5B2023%2C%20%D0%A1%D0%A8%D0%90%2C%20%D0%91%D0%BE%D0%B5%D0%B2%D0%B8%D0%BA%2C%20%D0%BA%D1%80%D0%B8%D0%BC%D0%B8%D0%BD%D0%B0%D0%BB%2C%20%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2%2C%20WEB-DLRip%5D%20MVO%20(TVShows)%20%2B%20Original%20%2B%20Sub%20Rus%2C%20Eng'

ses = lt.session()
info = lt.torrent_info(path)
h = ses.add_torrent({
	"ti": info,
	"save_path": './',
	"file_priorities": [0] * len(info.files())  # Disable all files initially
})
fileStorage = info.files()
listOfTorrentFiles = [fileStorage.file_path(i) for i in range(fileStorage.num_files())]
print(listOfTorrentFiles)

#import ffmpeg
#from faster_whisper import WhisperModel
#import math
#from pathlib import Path

#need insatll cuda and cudnn-windows-x86_64-8.9.7 dlls put to ctranslate2 folder
#pip install ctranslate2>=4.0 huggingface_hub>=0.13 tokenizers>=0.13 onnxruntime>=1.14  av>=11 tqdm

#input_video = "D:/films/Индиана Джонс/Индиана Джонс и Королевство xрустального черепа/Индиана Джонс и Королевство xрустального черепа (2008) BDRip.avi"
#input_video_name = Path(input_video).stem
#print(input_video_name)
#
#def getAudioStreamsList():
#	res = []
#	probe = ffmpeg.probe(input_video)
#	for stream in probe['streams']:
#		if stream['codec_type'] == 'audio':
#			res.append((stream['index'], stream['tags']['title']))
#			#print(stream['index'], stream['tags']['title'])
#	return res
#
#def extractAudio():
#	extracted_audio = f"audio_{input_video_name}.wav"
#	stream = ffmpeg.input(input_video)
#	stream = ffmpeg.output(stream, extracted_audio, map = '0:1')
#	ffmpeg.run(stream, overwrite_output=True)
#	return extracted_audio
#
#def transcribe(audio):
#	model = WhisperModel("small")
#	segments, info = model.transcribe(audio)
#	language = info.language
#	print("Transcription language", language)
#	subtitle_file = f"sub_{input_video_name}.{language}.srt"
#	text = ""
#	index = 0
#	for segment in segments:
#		print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
#		segment_start = formatTime(segment.start)
#		segment_end = formatTime(segment.end)
#		text += f"{str(index+1)} \n"
#		text += f"{segment_start} --> {segment_end} \n"
#		text += f"{segment.text} \n"
#		text += "\n"
#		index += 1
#	f = open(subtitle_file, "w")
#	f.write(text)
#	f.close()
#	return language, []
#
#def formatTime(seconds):
#	hours = math.floor(seconds / 3600)
#	seconds %= 3600
#	minutes = math.floor(seconds / 60)
#	seconds %= 60
#	milliseconds = round((seconds - math.floor(seconds)) * 1000)
#	seconds = math.floor(seconds)
#	formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
#	return formatted_time
#
#def generateSubtitleFile(language, segments):
#	print("Save subtitles")
#	subtitle_file = f"sub_{input_video_name}.{language}.srt"
#	text = ""
#	for index, segment in enumerate(segments):
#		segment_start = formatTime(segment[0])
#		segment_end = formatTime(segment[1])
#		text += f"{str(index+1)} \n"
#		text += f"{segment_start} --> {segment_end} \n"
#		text += f"{segment[2]} \n"
#		text += "\n"
#	f = open(subtitle_file, "w")
#	f.write(text)
#	f.close()
#	return subtitle_file
#
#def run():
#	audioPath = extractAudio()
#	#language, segments = transcribe(audio='D:/films/Индиана Джонс/Индиана Джонс и Королевство xрустального черепа/Индиана Джонс и Королевство xрустального черепа (2008) BDRip.Eng.ac3')
#	#print("Segments ready")
#	#subtitle_file = generateSubtitleFile(language=language, segments=segments)
#
##run()
#
#from pytubefix import YouTube
#from pytubefix.cli import on_progress
#
#url = "https://www.youtube.com/watch?v=0Osso8mLL-A"
#
#yt = YouTube(url, on_progress_callback=on_progress)
#print(yt.title)
#
#ys = yt.streams.get_highest_resolution().url
#print(ys)