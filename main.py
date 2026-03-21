import os
from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
from requests import Session
from http.cookiejar import MozillaCookieJar

app = FastAPI()

COOKIES_FILE = "cookies.txt"

@app.get("/")
def root():
    return {"status": "YT Transcript API is running"}

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    try:
        # Load cookies into a requests Session
        session = Session()
        if os.path.exists(COOKIES_FILE):
            cookie_jar = MozillaCookieJar(COOKIES_FILE)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies.update(cookie_jar)
            ytt = YouTubeTranscriptApi(http_client=session)
        else:
            ytt = YouTubeTranscriptApi()

        try:
            fetched = ytt.fetch(video_id)
            lang = "en"
        except:
            transcript_list = ytt.list(video_id)
            first = next(iter(transcript_list))
            fetched = first.fetch()
            lang = first.language_code

        full_text = " ".join([line.text for line in fetched])
        return {
            "success": True,
            "video_id": video_id,
            "language": lang,
            "total_lines": len(fetched),
            "transcript": full_text
        }
    except Exception as e:
        return {
            "success": False,
            "video_id": video_id,
            "transcript": "Transcript not available.",
            "error": str(e)
        }