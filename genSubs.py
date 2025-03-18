import math

def extractAudio(fname, track):
	global _SUB_GEN_SUPPORT
	if _SUB_GEN_SUPPORT:
		try:
			import ffmpeg
			_SUB_GEN_SUPPORT = True
		except:
			_SUB_GEN_SUPPORT = False
	if not _SUB_GEN_SUPPORT:
		return None
	extracted_audio = f"audio_{fname}.wav"
	stream = ffmpeg.input(fname)
	stream = ffmpeg.output(stream, extracted_audio, map = '0:' + str(track[0]))
	ffmpeg.run(stream, overwrite_output=True)
	return extracted_audio

def formatTime(seconds):
	hours = math.floor(seconds / 3600)
	seconds %= 3600
	minutes = math.floor(seconds / 60)
	seconds %= 60
	milliseconds = round((seconds - math.floor(seconds)) * 1000)
	seconds = math.floor(seconds)
	formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
	return formatted_time

def transcribe(audio, fname):
	global _SUB_GEN_SUPPORT
	if _SUB_GEN_SUPPORT:
		try:
			from faster_whisper import WhisperModel
			_SUB_GEN_SUPPORT = True
		except:
			_SUB_GEN_SUPPORT = False
	if not _SUB_GEN_SUPPORT:
		return
	model = WhisperModel("small")
	segments, info = model.transcribe(audio)
	language = info.language
	print("Transcription language", language)
	subtitle_file = f"sub_{fname}.{language}.srt"
	text = ""
	index = 0
	for segment in segments:
		#print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
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
