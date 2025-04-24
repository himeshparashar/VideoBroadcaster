from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from stream_utils import Streaming
import threading

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

streaming = Streaming()

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

@app.get("/devices")
def get_devices():
    """Get a list of available video capture devices."""
    return streaming.list_available_devives()

@app.get("/start")
def start_stream(
        source : str = Query("0"),
        fps : int = Query(15),
        blur_strength: int = Query(21),
        background: str = Query("none"),
):
    streaming.update_streaming_config(
        in_source=source,
        out_source="None",
        fps=fps,
        blur_strength=blur_strength,
        background=background
    )

    if streaming.running:
        return JSONResponse(content={"message": "stream already running"}, status_code=400)
    
    stream_thread = threading.Thread(target=streaming.stream_video, args=())
    stream_thread.start()
    return {"message": f"Streaming started on source {source} with fps {fps}, blur_strength {blur_strength}, background {background}"}  

@app.get("/stop")
def stop_stream():
    """Stop the video stream."""
    streaming.update_running_status()
    return {"message": "Streaming stopped"}    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)