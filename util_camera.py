
from kivy.uix.camera import Camera
from kivy.core.image import Image as CoreImage
from kivy.base import EventLoop
from kivy.clock import Clock

def capture_photo(output_path: str) -> bool:
    try:
        cam = Camera(play=True, resolution=(640, 480), index=0)
        def _grab(dt):
            if not cam.texture:
                return False
            CoreImage(cam.texture).save(output_path)
            cam.play = False
            return False
        EventLoop.ensure_window()
        Clock.schedule_once(_grab, 1.0)
        return True
    except Exception as e:
        print("capture_photo error:", e)
        return False
