import ffmpeg
import logging
import os
from moviepy import VideoFileClip, TextClip, ImageClip, AudioFileClip, CompositeVideoClip
from moviepy.video.fx import Crop, MultiplyColor, LumContrast

logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Editor:
    def split_video(self, video_path, title, max_duration=60, progress_callback=None):
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            if duration <= max_duration:
                video.close()
                return [(video_path, title)]

            splits = []
            num_splits = int(duration // max_duration) + (1 if duration % max_duration > 0 else 0)
            from .utils import clean_title
            cleaned_title = clean_title(title)

            for i in range(num_splits):
                start_time = i * max_duration
                end_time = min((i + 1) * max_duration, duration)
                split_clip = video.subclip(start_time, end_time)
                split_title = f"{cleaned_title} PART-{i + 1}"
                split_path = f"videos/{split_title}.mp4"
                split_clip.write_videofile(split_path, codec="libx264", audio_codec="aac")
                splits.append((split_path, split_title))
                if progress_callback:
                    progress_callback(f"Created split {i + 1}/{num_splits}: {split_title}")

            video.close()
            os.remove(video_path)
            return splits
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error splitting video {title}: {str(e)}")
            logging.error(f"Error splitting video {title}: {str(e)}")
            return [(video_path, title)]

    def edit_video_crop(self, video_path, output_path, crop_params, progress_callback=None, preserve_aspect=False):
        try:
            x1, y1, x2, y2 = crop_params
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            video_width = int(video_stream['width'])
            video_height = int(video_stream['height'])

            if preserve_aspect:
                target_width = x2 - x1
                target_height = y2 - y1
                target_aspect = target_width / target_height
                current_aspect = video_width / video_height
                if current_aspect > target_aspect:
                    new_width = int(target_height * current_aspect)
                    x_center = (x1 + x2) / 2
                    x1 = max(0, int(x_center - new_width / 2))
                    x2 = min(video_width, int(x_center + new_width / 2))
                else:
                    new_height = int(target_width / current_aspect)
                    y_center = (y1 + y2) / 2
                    y1 = max(0, int(y_center - new_height / 2))
                    y2 = min(video_height, int(y_center + new_height / 2))

            crop_width = x2 - x1
            crop_height = y2 - y1

            stream = ffmpeg.input(video_path)
            stream = ffmpeg.crop(stream, x1, y1, crop_width, crop_height)
            stream = ffmpeg.output(stream, output_path, c='copy', vcodec='libx264', acodec='aac', strict='experimental')
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            if progress_callback:
                progress_callback(f"Cropped video saved to {output_path}")
            return True
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            if progress_callback:
                progress_callback(f"Error cropping video: {error_msg}")
            logging.error(f"Error cropping video: {error_msg}")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error cropping video: {str(e)}")
            logging.error(f"Error cropping video: {str(e)}")
            return False

    def edit_video_overlays(self, video_path, output_path, overlay_params=None, text_params=None, progress_callback=None):
        try:
            stream = ffmpeg.input(video_path)
            video_stream = stream['v']
            audio_stream = stream['a'] if 'a' in stream else None

            if overlay_params and os.path.exists(overlay_params['image_path']):
                image = ffmpeg.input(overlay_params['image_path'])
                scale = max(0.1, float(overlay_params.get('scale', 1.0)))
                image = ffmpeg.filter(image, 'scale', f"iw*{scale}", f"ih*{scale}")
                x = max(0, int(overlay_params.get('x', 0)))
                y = max(0, int(overlay_params.get('y', 0)))
                video_stream = ffmpeg.overlay(video_stream, image, x=x, y=y)

            if text_params and text_params.get('text'):
                text = text_params['text'].replace(":", "\\:").replace("'", "\\'")
                font_size = max(1, int(text_params.get('font_size', 24)))
                color = text_params.get('color', 'white')
                x = max(0, int(text_params.get('x', 10)))
                y = max(0, int(text_params.get('y', 10)))
                video_stream = ffmpeg.drawtext(
                    video_stream,
                    text=text,
                    fontfile='C:\\Windows\\Fonts\\arial.ttf',
                    fontsize=font_size,
                    fontcolor=color,
                    x=x,
                    y=y
                )

            output_args = {'vcodec': 'libx264', 'acodec': 'aac', 'strict': 'experimental'}
            if audio_stream:
                stream = ffmpeg.output(video_stream, audio_stream, output_path, **output_args)
            else:
                stream = ffmpeg.output(video_stream, output_path, **output_args)

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            if progress_callback:
                progress_callback(f"Overlays applied. Saved to {output_path}")
            logging.info(f"Overlays applied to {video_path}: {output_path}")
            return True
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            if progress_callback:
                progress_callback(f"Error applying overlays: {error_msg}")
            logging.error(f"Error applying overlays: {error_msg}")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error applying overlays: {str(e)}")
            logging.error(f"Error applying overlays: {str(e)}")
            return False

    def edit_video_text_overlay(self, video_path, output_path, text_params, progress_callback=None):
        try:
            text, pos_x, pos_y, font, fontsize, color = text_params
            video = VideoFileClip(video_path)
            text_clip = TextClip(text, font=font, fontsize=fontsize, color=color)
            text_clip = text_clip.set_position((pos_x, pos_y)).set_duration(video.duration)
            final = CompositeVideoClip([video, text_clip])
            final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False)
            final.close()
            video.close()
            if progress_callback:
                progress_callback(f"Text overlay added to {output_path}")
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error adding text overlay: {str(e)}")
            logging.error(f"Error adding text overlay: {str(e)}")
            return False

    def edit_video_image_overlay(self, video_path, output_path, image_params, progress_callback=None):
        try:
            image_path, pos_x, pos_y, width = image_params
            video = VideoFileClip(video_path)
            image_clip = ImageClip(image_path).set_duration(video.duration)
            if width:
                image_clip = image_clip.resize(width=width)
            image_clip = image_clip.set_position((pos_x, pos_y))
            final = CompositeVideoClip([video, image_clip])
            final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False)
            final.close()
            video.close()
            if progress_callback:
                progress_callback(f"Image overlay added to {output_path}")
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error adding image overlay: {str(e)}")
            logging.error(f"Error adding image overlay: {str(e)}")
            return False

    def edit_video_color_grading(video_path, output_path, color_params, progress_callback=None):
        try:
            brightness, contrast_val, saturation = color_params
            video = VideoFileClip(video_path)
            adjusted = MultiplyColor.multiply_color(video, factor=brightness)
            adjusted = LumContrast.lum_contrast(adjusted, contrast=contrast_val)
            adjusted = MultiplyColor.multiply_color(adjusted, factor=saturation)
            adjusted.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False)
            adjusted.close()
            video.close()
            if progress_callback:
                progress_callback(f"Color grading applied to {output_path}")
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error applying color grading: {str(e)}")
            return False

    def edit_video_add_sound(self, video_path, output_path, audio_path, progress_callback=None):
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path).subclip(0, video.duration)
            final = video.set_audio(audio)
            final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False)
            final.close()
            video.close()
            audio.close()
            if progress_callback:
                progress_callback(f"Audio added to {output_path}")
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error adding audio: {str(e)}")
            logging.error(f"Error adding audio: {str(e)}")
            return False

    def edit_video_all(self, video_path, title, crop_params, text_params, image_params, color_params, audio_path, progress_callback=None):
        try:
            os.makedirs(f"Edited/{title}", exist_ok=True)
            current_path = video_path
            temp_path = f"Edited/{title}/temp.mp4"
            final_path = f"Edited/{title}/{title}.mp4"

            if crop_params and self.edit_video_crop(current_path, temp_path, crop_params, progress_callback, preserve_aspect=True):
                if current_path != video_path:
                    os.remove(current_path)
                current_path = temp_path

            if text_params and self.edit_video_text_overlay(current_path, temp_path, text_params, progress_callback):
                if current_path != temp_path:
                    os.remove(current_path)
                current_path = temp_path

            if image_params and self.edit_video_image_overlay(current_path, temp_path, image_params, progress_callback):
                if current_path != temp_path:
                    os.remove(current_path)
                current_path = temp_path

            if color_params and self.edit_video_color_grading(current_path, temp_path, color_params, progress_callback):
                if current_path != temp_path:
                    os.remove(current_path)
                current_path = temp_path

            if audio_path and self.edit_video_add_sound(current_path, final_path, audio_path, progress_callback):
                if current_path != final_path:
                    os.remove(current_path)
            else:
                os.rename(current_path, final_path)

            if progress_callback:
                progress_callback(f"All edits applied, saved to {final_path}")
            return True, final_path
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error applying all edits: {str(e)}")
            logging.error(f"Error applying all edits: {str(e)}")
            return False, None