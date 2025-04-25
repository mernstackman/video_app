import json
import os
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_list(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_list(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def is_title_similar(new_title, existing_titles, threshold=0.8):
    if not existing_titles:
        return False
    all_titles = existing_titles + [new_title]
    vectorizer = TfidfVectorizer().fit_transform(all_titles)
    similarity = cosine_similarity(vectorizer[-1], vectorizer[:-1])
    return any(sim >= threshold for sim in similarity[0])

def rename_video(video_path, new_title, output_dir, progress_callback=None):
    try:
        new_title = re.sub(r'[<>:"/\\|?*]', '', new_title).strip()
        if not new_title:
            raise ValueError("New title cannot be empty or invalid.")

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{new_title}.mp4")
        shutil.copy2(video_path, output_path)

        if progress_callback:
            progress_callback(f"Video renamed to {output_path}")
        return True
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error renaming video: {str(e)}")
        logging.error(f"Error renaming video: {str(e)}")
        return False