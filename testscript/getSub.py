
#import ffmpeg
#from faster_whisper import WhisperModel
import math
from pathlib import Path

#need insatll cuda and cudnn-windows-x86_64-8.9.7 dlls put to ctranslate2 folder
#pip install ctranslate2>=4.0 huggingface_hub>=0.13 tokenizers>=0.13 onnxruntime>=1.14  av>=11 tqdm

input_video = "D:/films/Индиана Джонс/Индиана Джонс и Королевство xрустального черепа/Индиана Джонс и Королевство xрустального черепа (2008) BDRip.avi"
input_video_name = Path(input_video).stem
print(input_video_name)

def getAudioStreamsList():
	res = []
	probe = ffmpeg.probe(input_video)
	for stream in probe['streams']:
		if stream['codec_type'] == 'audio':
			res.append((stream['index'], stream['tags']['title']))
			#print(stream['index'], stream['tags']['title'])
	return res

def extractAudio():
	extracted_audio = f"audio_{input_video_name}.wav"
	stream = ffmpeg.input(input_video)
	stream = ffmpeg.output(stream, extracted_audio, map = '0:1')
	ffmpeg.run(stream, overwrite_output=True)
	return extracted_audio

def transcribe(audio):
	model = WhisperModel("small")
	segments, info = model.transcribe(audio)
	language = info.language
	print("Transcription language", language)
	subtitle_file = f"sub_{input_video_name}.{language}.srt"
	text = ""
	index = 0
	for segment in segments:
		print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
		segment_start = formatTime(segment.start)
		segment_end = formatTime(segment.end)
		text += f"{str(index+1)} \n"
		text += f"{segment_start} --> {segment_end} \n"
		text += f"{segment.text} \n"
		text += "\n"
		index += 1
	f = open(subtitle_file, "w")
	f.write(text)
	f.close()
	return language, []

def formatTime(seconds):
	hours = math.floor(seconds / 3600)
	seconds %= 3600
	minutes = math.floor(seconds / 60)
	seconds %= 60
	milliseconds = round((seconds - math.floor(seconds)) * 1000)
	seconds = math.floor(seconds)
	formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
	return formatted_time

def generateSubtitleFile(language, segments):
	print("Save subtitles")
	subtitle_file = f"sub_{input_video_name}.{language}.srt"
	text = ""
	for index, segment in enumerate(segments):
		segment_start = formatTime(segment[0])
		segment_end = formatTime(segment[1])
		text += f"{str(index+1)} \n"
		text += f"{segment_start} --> {segment_end} \n"
		text += f"{segment[2]} \n"
		text += "\n"
	f = open(subtitle_file, "w")
	f.write(text)
	f.close()
	return subtitle_file

def run():
	audioPath = extractAudio()
	#language, segments = transcribe(audio='D:/films/Индиана Джонс/Индиана Джонс и Королевство xрустального черепа/Индиана Джонс и Королевство xрустального черепа (2008) BDRip.Eng.ac3')
	#print("Segments ready")
	#subtitle_file = generateSubtitleFile(language=language, segments=segments)

#run()

from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://www.youtube.com/watch?v=0Osso8mLL-A"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution().url
print(ys)