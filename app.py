import os
import re
import time
import urllib.parse
from pathlib import Path

import requests
import streamlit as st
from playwright.sync_api import sync_playwright


DOWNLOAD_FOLDER = Path("video_downloads")

VIDEO_EXTENSIONS = (
    ".mp4", ".webm", ".mov", ".m4v", ".mkv", ".avi"
)

STREAM_EXTENSIONS = (
    ".m3u8", ".mpd"
)


def sanitize_filename(name: str) -> str:
    name = urllib.parse.unquote(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.strip() or "video.mp4"


def filename_from_url(url: str, index: int) -> str:
    parsed = urllib.parse.urlparse(url)
    name = os.path.basename(parsed.path)

    if not name or "." not in name:
        name = f"video_{index}.mp4"

    return sanitize_filename(name)


def unique_path(folder: Path, filename: str) -> Path:
    path = folder / filename

    if not path.exists():
        return path

    base, ext = os.path.splitext(filename)
    counter = 2

    while True:
        new_path = folder / f"{base}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def cookies_to_requests_cookiejar(playwright_cookies):
    jar = requests.cookies.RequestsCookieJar()

    for cookie in playwright_cookies:
        jar.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/")
        )

    return jar


def capture_video_links(page_url: str, capture_seconds: int, headless: bool, progress_callback=None):
    found_video_urls = set()
    found_stream_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        context = browser.new_context(
            accept_downloads=True
        )

        page = context.new_page()

        def handle_response(response):
            try:
                url = response.url
                clean_url = url.split("?")[0].lower()
                headers = response.headers
                content_type = headers.get("content-type", "").lower()

                is_direct_video = (
                    content_type.startswith("video/")
                    or clean_url.endswith(VIDEO_EXTENSIONS)
                )

                is_stream = (
                    clean_url.endswith(STREAM_EXTENSIONS)
                    or "mpegurl" in content_type
                    or "dash+xml" in content_type
                )

                if is_direct_video:
                    found_video_urls.add(url)

                if is_stream:
                    found_stream_urls.add(url)

            except Exception:
                pass

        page.on("response", handle_response)

        page.goto(page_url, wait_until="domcontentloaded", timeout=0)

        for second in range(capture_seconds):
            time.sleep(1)

            if progress_callback:
                progress_callback((second + 1) / capture_seconds)

        cookies = context.cookies()
        user_agent = page.evaluate("navigator.userAgent")
        referer = page.url

        browser.close()

    return {
        "videos": sorted(found_video_urls),
        "streams": sorted(found_stream_urls),
        "cookies": cookies,
        "user_agent": user_agent,
        "referer": referer
    }


def download_file(url: str, index: int, headers: dict, cookies) -> Path:
    DOWNLOAD_FOLDER.mkdir(exist_ok=True)

    with requests.get(
        url,
        headers=headers,
        cookies=cookies,
        stream=True,
        timeout=90
    ) as response:
        response.raise_for_status()

        filename = filename_from_url(url, index)

        content_type = response.headers.get("content-type", "").lower()

        if "." not in filename:
            if "webm" in content_type:
                filename += ".webm"
            elif "quicktime" in content_type:
                filename += ".mov"
            else:
                filename += ".mp4"

        file_path = unique_path(DOWNLOAD_FOLDER, filename)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

        return file_path


st.set_page_config(
    page_title="Video Downloader",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Video Downloader din Network / Media")

st.warning(
    "Folosește aplicația doar pentru fișiere video pentru care ai drept de acces și descărcare. "
    "Aplicația nu este pentru ocolirea DRM, parolelor, restricțiilor sau protecțiilor site-urilor."
)

page_url = st.text_input("Link pagina web")

capture_seconds = st.slider(
    "Câte secunde să urmărească traficul Network/Media?",
    min_value=10,
    max_value=300,
    value=60,
    step=10
)

headless = st.checkbox(
    "Rulează fără să se vadă browserul",
    value=False,
    help="Pentru cazul tău lasă debifat. Așa poți apăsa Play, login, scroll etc."
)

if "capture_result" not in st.session_state:
    st.session_state.capture_result = None

if st.button("1. Deschide pagina și caută video-uri"):
    if not page_url.strip():
        st.error("Introdu link-ul paginii.")
    else:
        st.info(
            "Se va deschide Chromium. În fereastra deschisă: fă login dacă este nevoie, "
            "apasă Play pe video-uri și dă scroll ca să se încarce toate."
        )

        progress = st.progress(0)

        try:
            result = capture_video_links(
                page_url=page_url.strip(),
                capture_seconds=capture_seconds,
                headless=headless,
                progress_callback=lambda value: progress.progress(value)
            )

            st.session_state.capture_result = result

            st.success("Capturarea s-a terminat.")

        except Exception as e:
            st.error(f"Eroare la capturare: {e}")


result = st.session_state.capture_result

if result:
    video_urls = result["videos"]
    stream_urls = result["streams"]

    st.subheader("Fișiere video directe găsite")

    if video_urls:
        st.success(f"Am găsit {len(video_urls)} fișiere video directe.")

        st.text_area(
            "Link-uri video găsite",
            value="\n".join(video_urls),
            height=200
        )

        if st.button("2. Descarcă fișierele video"):
            headers = {
                "User-Agent": result["user_agent"],
                "Referer": result["referer"]
            }

            cookies = cookies_to_requests_cookiejar(result["cookies"])

            downloaded_files = []

            download_progress = st.progress(0)

            for index, video_url in enumerate(video_urls, start=1):
                try:
                    file_path = download_file(
                        url=video_url,
                        index=index,
                        headers=headers,
                        cookies=cookies
                    )

                    downloaded_files.append(file_path)

                except Exception as e:
                    st.error(f"Eroare la descărcarea link-ului {video_url}: {e}")

                download_progress.progress(index / len(video_urls))

            if downloaded_files:
                st.success(f"Am descărcat {len(downloaded_files)} fișiere în folderul: {DOWNLOAD_FOLDER.resolve()}")

                for file_path in downloaded_files:
                    st.write(str(file_path))

    else:
        st.info("Nu am găsit fișiere video directe de tip MP4/WebM/MOV.")

    st.subheader("Stream-uri HLS/DASH găsite")

    if stream_urls:
        st.warning(
            "Am găsit link-uri de tip streaming, de exemplu .m3u8 sau .mpd. "
            "Acestea nu sunt fișiere video simple, ci stream-uri împărțite în segmente."
        )

        st.text_area(
            "Link-uri streaming găsite",
            value="\n".join(stream_urls),
            height=160
        )
    else:
        st.info("Nu am găsit stream-uri HLS/DASH.")
