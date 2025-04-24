import requests
import logging

logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Uploader:
    def upload_to_facebook(self, video_path, page_id, access_token, title, progress_callback=None):
        try:
            url = f"https://graph-video.facebook.com/v20.0/{page_id}/videos"
            files = {'file': open(video_path, 'rb')}
            data = {
                'access_token': access_token,
                'title': title,
                'description': f"Check out this awesome video: {title}"
            }
            response = requests.post(url, files=files, data=data)
            files['file'].close()
            if response.status_code == 200:
                if progress_callback:
                    progress_callback(f"Uploaded {title} to Facebook page")
                logging.info(f"Uploaded {title} to Facebook page")
                return True
            else:
                if progress_callback:
                    progress_callback(f"Error uploading to Facebook: {response.text}")
                logging.error(f"Error uploading to Facebook: {response.text}")
                return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error uploading to Facebook: {str(e)}")
            logging.error(f"Error uploading to Facebook: {str(e)}")
            return False