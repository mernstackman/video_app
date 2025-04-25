import yt_dlp
import os
import logging
from .utils import clean_title
from .file_manager import load_list, save_list, is_title_similar

logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

SEARCH_RESULTS_FILE = "search_results.json"
DOWNLOADED_FILE = "downloaded_videos.json"

class Downloader:
    def __init__(self):
        self.search_results_file = SEARCH_RESULTS_FILE
        self.downloaded_file = DOWNLOADED_FILE

    def search_youtube(self, query, results_length=10, progress_callback=None):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'playlistend': results_length,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch{results_length}:{query}", download=False)
                entries = result.get('entries', [])
                return [{"title": entry['title'], "url": entry['url']} for entry in entries[:results_length]]
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error searching for '{query}': {str(e)}")
            logging.error(f"Search failed for '{query}': {str(e)}")
            return []

    def download_video(self, url, title, progress_callback=None):
        ydl_opts = {
            'outtmpl': f'videos/{title}.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            video_path = f"videos/{title}.mp4"
            if os.path.exists(video_path):
                return True, f"Downloaded: {title}", video_path
            else:
                return False, f"Error: Video file not found for {title}", None
        except Exception as e:
            return False, f"Error downloading {title}: {str(e)}", None

    def download_from_url(self, url, resolution, extension, output_dir="videos", progress_callback=None):
        resolution_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "360p": "bestvideo[height<=360]+bestaudio/best"
        }
        format_str = resolution_map.get(resolution, "bestvideo+bestaudio/best")
        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': format_str,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'merge_output_format': extension.lstrip('.'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: progress_callback(f"Downloading: {d['status']} {d.get('downloaded_bytes', 0)} bytes") if progress_callback else None]
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                output_path = f"{base}{extension}"
                if os.path.exists(filename) and filename != output_path:
                    os.rename(filename, output_path)
            if os.path.exists(output_path):
                if progress_callback:
                    progress_callback(f"Downloaded video to {output_path}")
                logging.info(f"Downloaded video from {url} to {output_path} (resolution: {resolution}, extension: {extension})")
                return True, output_path
            else:
                error_msg = "Download completed but output file not found."
                if progress_callback:
                    progress_callback(error_msg)
                logging.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Error downloading video: {str(e)}"
            if progress_callback:
                progress_callback(error_msg)
            logging.error(f"Download from URL failed: {error_msg}")
            return False, error_msg

    def populate_search_results(self, search_queries, results_length=10, progress_callback=None, progress_updater=None):
        downloaded_list = load_list(self.downloaded_file)
        search_results = load_list(self.search_results_file)
        downloaded_urls = [video['url'] for video in downloaded_list]
        downloaded_titles = [video['title'] for video in downloaded_list]
        search_result_urls = [video['url'] for video in search_results]
        search_result_titles = [video['title'] for video in search_results]

        total_new_results = 0
        for idx, query in enumerate(search_queries, 1):
            if progress_callback:
                progress_callback(f"Searching for '{query}' ({idx}/{len(search_queries)})...")
            all_search_results = self.search_youtube(query, results_length, progress_callback)
            if not all_search_results:
                if progress_callback:
                    progress_callback(f"No search results found for '{query}'.")
                continue

            new_results = []
            for video in all_search_results:
                title = video['title']
                url = video['url']
                if (url in downloaded_urls or
                    url in search_result_urls or
                    is_title_similar(title, downloaded_titles) or
                    is_title_similar(title, search_result_titles)):
                    if progress_callback:
                        progress_callback(f"Excluding (already exists or similar): {title}")
                    continue
                new_results.append(video)

            if new_results:
                search_results.extend(new_results)
                search_result_urls.extend([video['url'] for video in new_results])
                search_result_titles.extend([video['title'] for video in new_results])
                total_new_results += len(new_results)
                if progress_callback:
                    progress_callback(f"Added {len(new_results)} unique videos for '{query}'.")

            if progress_updater:
                progress_updater(idx / len(search_queries) * 100)

        if total_new_results > 0:
            save_list(self.search_results_file, search_results)
            if progress_callback:
                progress_callback(f"Total: Added {total_new_results} unique videos to search results.")
            return True
        else:
            if progress_callback:
                progress_callback("No new unique videos found in search results.")
            return False

    def download_next_video(self, progress_callback=None, max_downloads=1, progress_updater=None):
        search_results = load_list(self.search_results_file)
        downloaded_list = load_list(self.downloaded_file)
        downloaded_urls = [video['url'] for video in downloaded_list]
        downloaded_titles = [video['title'] for video in downloaded_list]

        if not search_results:
            if progress_callback:
                progress_callback("Search results list is empty. Please populate it first.")
            return False, []

        os.makedirs("videos", exist_ok=True)
        downloaded_count = 0
        i = 0
        video_paths = []
        while i < len(search_results) and downloaded_count < max_downloads:
            video = search_results[i]
            original_title = video['title']
            url = video['url']

            if url in downloaded_urls:
                if progress_callback:
                    progress_callback(f"Skipping (already downloaded): {original_title}")
                i += 1
                continue

            if is_title_similar(original_title, downloaded_titles):
                if progress_callback:
                    progress_callback(f"Skipping (similar title): {original_title}")
                i += 1
                continue

            cleaned_title = clean_title(original_title)
            success, message, video_path = self.download_video(url, cleaned_title, progress_callback)
            if progress_callback:
                progress_callback(message)
            if success:
                downloaded_list.append({"title": cleaned_title, "url": url, "path": video_path})
                video_paths.append((video_path, cleaned_title))
                search_results.pop(i)
                downloaded_count += 1
                if progress_callback:
                    progress_callback("Download complete. One video processed.")
                if progress_updater:
                    progress_updater((downloaded_count / max_downloads) * 100)
            else:
                i += 1

        save_list(self.search_results_file, search_results)
        save_list(self.downloaded_file, downloaded_list)

        return downloaded_count > 0, video_paths