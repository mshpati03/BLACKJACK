import cv2
import threading
import time


class CameraService:
    def __init__(self, camera_index=0, frame_width=640):
        self._camera_index = camera_index
        self._frame_width = frame_width
        self._cap = None
        self._latest_frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {self._camera_index}")
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        # Give the camera a moment to warm up
        time.sleep(0.5)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._cap:
            self._cap.release()
            self._cap = None

    def _update_loop(self):
        while self._running:
            if self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret:
                    # Resize to target width, keeping aspect ratio
                    h, w = frame.shape[:2]
                    scale = self._frame_width / w
                    new_h = int(h * scale)
                    resized = cv2.resize(frame, (self._frame_width, new_h))
                    with self._lock:
                        self._latest_frame = resized
            time.sleep(0.033)  # ~30 fps

    def get_latest_frame(self):
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def is_running(self):
        return self._running


# Singleton instance shared across the app
camera_service = CameraService()
