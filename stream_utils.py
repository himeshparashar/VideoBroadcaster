import cv2
import pyvirtualcam
import torch

from engine import CustomerSegmentationWithYolo

class Streaming(CustomerSegmentationWithYolo):
    def __init__(self, in_source=None, out_source=None, fps=None, blur_strength=None, cam_fps=15, background=None):
        super().__init__(erode_size=5, erode_intensity=2)
        self.input_source = in_source
        self.output_source = out_source
        self.fps = fps
        self.blur_strength = blur_strength
        self.background = background
        self.running = False
        self.orignal_fps = cam_fps
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        

    def update_streaming_config(self, in_source=None, out_source=None, fps=None, blur_strength=None, background=None):
        self.input_source = in_source
        self.output_source = out_source
        self.fps = max(1, fps) if fps is not None else None  # Ensure fps is at least 1
        self.blur_strength = blur_strength
        self.background = background

    def stream_video(self):
        self.running = True
        cap = cv2.VideoCapture(int(self.input_source))

        frame_idx = 0

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        try:
            self.orignal_fps = int(cap.get(cv2.CAP_PROP_FPS))
        except Exception as e:
            print(f"Webcam({self.input_source}), live fps not available. Set the fps accordingly.")
            self.orignal_fps = 30  # Default fallback FPS

        # Fix the frame interval calculation
        if self.fps is None:
            self.fps = self.orignal_fps
            frame_interval = 1
        else:
            self.fps = min(self.fps, self.orignal_fps)  # Ensure fps doesn't exceed original
            frame_interval = max(1, round(self.orignal_fps / self.fps))

        with pyvirtualcam.Camera(width, height, self.fps) as cam:
            print(f"Virtual camera running at {width}x{height} at {self.fps} FPS")
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                result_frame = frame.copy()  # Default to original frame
                
                if frame_idx % frame_interval == 0:
                    result = self.model.predict(source=frame, save=False, save_txt=False, stream=True, retina_masks=True, verbose=False, device=self.device)
                    mask = self.generate_mask_from_result(result)

                    if mask is not None:
                        if self.background == "blur":
                            result_frame = self.apply_blur_with_mask(frame, mask, blur_strength=self.blur_strength)
                        elif self.background == "none":
                            result_frame = self.apply_black_backgroud(frame, mask)
                        elif self.background == "default":
                            result_frame = self.apply_custom_background(frame, mask)

                # Convert BGR to RGB and send to virtual camera
                cam.send(cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB))
                cam.sleep_until_next_frame()
                
                frame_idx += 1

        cap.release()

    def update_running_status(self, running_status=False):
        self.running = running_status


    def list_available_devives(self):
        """List all available video capture devices."""
        devices = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                devices.append({'id':i, 'name': f"Camera {i}"})
                cap.release()

        print(f"Available devices: {devices}")

        return devices


