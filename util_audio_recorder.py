
from kivy.utils import platform

class AndroidAudioRecorder:
    def __init__(self, audio_path="sos_audio.m4a"):
        self.audio_path = audio_path
        self.started = False
        self.rec = None

    def start(self):
        if platform != "android":
            return False
        try:
            from jnius import autoclass
            MediaRecorder = autoclass('android.media.MediaRecorder')
            AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

            self.rec = MediaRecorder()
            self.rec.setAudioSource(AudioSource.MIC)
            self.rec.setOutputFormat(OutputFormat.MPEG_4)
            self.rec.setAudioEncoder(AudioEncoder.AAC)
            self.rec.setAudioChannels(1)
            self.rec.setAudioEncodingBitRate(128000)
            self.rec.setAudioSamplingRate(44100)
            self.rec.setOutputFile(self.audio_path)
            self.rec.prepare()
            self.rec.start()
            self.started = True
            return True
        except Exception as e:
            print("MediaRecorder start error:", e)
            return False

    def stop(self):
        if self.started and self.rec:
            try:
                self.rec.stop()
                self.rec.release()
            except Exception as e:
                print("MediaRecorder stop error:", e)
        self.started = False
        self.rec = None
