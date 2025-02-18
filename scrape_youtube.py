# scrape_youtube.py
import sys
import re
import requests
from bs4 import BeautifulSoup
import json
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    # Regular expression to extract video ID from URL
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def extract_metadata(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")

    link_title = soup.find_all(name="title")[0]
    title = str(link_title)
    title = title.replace("<title>","")
    title = title.replace("</title>","")

    link_channel = soup.find("link", itemprop="name")
    channel = str(link_channel)

    # Parse the HTML
    soup = BeautifulSoup(channel, 'html.parser')

    # Find the link tag with itemprop="name"
    link_tag = soup.find('link', itemprop='name')

    # Extract the content attribute
    channel = link_tag['content'] if link_tag else None
    
    return title, channel

def extract_chapters_from_html(url):
    """
    1. watch 페이지 HTML을 받아옴
    2. ytInitialPlayerResponse = {...}; 형태의 JSON 스니펫을 찾음
    3. JSON 파싱 후, 공식 챕터 데이터(chapters) 추출
    4. 챕터 제목과 시작 시간을 튜플 (startTime, title) 형태로 리스트 반환
    """

    r = requests.get(url)
    html = r.text

    # 1) ytInitialPlayerResponse 블록 추출 (정규식 혹은 string find 등)
    #    "ytInitialPlayerResponse = { ... };" 형태로 되어있는 스크립트 부분을 찾음
    pattern = r"ytInitialPlayerResponse\s*=\s*(\{.*?\});"
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return []

    json_str = match.group(1)

    # 2) JSON 파싱
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return []

    # 3) chapters 위치 찾아가기
    #    data["playerOverlays"]["playerOverlayRenderer"]["decoratedPlayerBarRenderer"]["decoratedPlayerBarRenderer"]["playerBar"]["chapteredPlayerBarRenderer"]["chapters"]
    #    예외가 발생할 수 있으므로 dict.get()으로 안전하게 접근
    chapters_data = (
        data
        .get("playerOverlays", {})
        .get("playerOverlayRenderer", {})
        .get("decoratedPlayerBarRenderer", {})
        .get("decoratedPlayerBarRenderer", {})
        .get("playerBar", {})
        .get("chapteredPlayerBarRenderer", {})
        .get("chapters", [])
    )

    chapters = []
    for ch in chapters_data:
        # 각 챕터는 {"title":{"simpleText":"..."}, "timeRangeStartMillis":"...", ...} 형태
        title = ch.get("title", {}).get("simpleText", None)
        start_ms = ch.get("timeRangeStartMillis")
        if title and start_ms is not None:
            # ms -> seconds 변환
            start_sec = int(start_ms) / 1000
            chapters.append((start_sec, title))
    
    return chapters

def extract_chapters_from_description(url):
    """
    1. 영상 설명 텍스트 추출
    2. 'MM:SS Title' 형태의 타임스탬프를 탐색
    3. (start_time, title) 리스트 반환
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # <meta itemprop="description" content="...영상 설명..."> 태그 찾기
    desc_meta = soup.find("meta", itemprop="description")
    if not desc_meta:
        return []
    
    description = desc_meta.get("content", "")
    if not description:
        return []

    # 라인 별로 나누어, 0:00, 1:24, 10:11 등 시간 형태를 찾고 뒤의 텍스트를 챕터명으로 인식
    lines = description.split('\n')
    chapter_regex = re.compile(r"^(\d+:\d+)\s+(.*)$")

    chapters = []
    for line in lines:
        match = chapter_regex.match(line)
        if match:
            timestamp_str = match.group(1)  # "0:00"
            chapter_title = match.group(2)  # "Intro"
            chapters.append((timestamp_str, chapter_title))

    return chapters
        
def download_thumbnail(video_id):
    image_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    img_data = requests.get(image_url).content
    with open('thumbnail.jpg', 'wb') as handler:
        handler.write(img_data)     
        
def get_transcript(video_id, url):
    transcript_raw = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'es', 'ko'])
    transcript_str_lst = [i['text'] for i in transcript_raw]
    transcript_full = ' '.join(transcript_str_lst)
    # 1) 공시 챕터 시도
    chapters = extract_chapters_from_html(url)
    # 2) 없으면 설명에서 시도
    if not chapters:
        chapters = extract_chapters_from_description(url)
    print(f"Chapters: {chapters}")
    return transcript_full, chapters

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <youtube_url>") # QUOTATION MARKS AROUND URL NEEDED WHEN RUNNING ON TERMINAL
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    video_id = extract_video_id(youtube_url)
    title, channel = extract_metadata(youtube_url)
    transcript = get_transcript(video_id)
    download_thumbnail(video_id)
    print(f"Title: {title}")
    print(f"Channel: {channel}")
    print('=============')
    print(transcript)
