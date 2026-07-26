import os

import shutil
import subprocess
import re
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

# Optional pure-Python fallback that provides ffmpeg binary
try:
    import imageio_ffmpeg
except Exception:
    imageio_ffmpeg = None

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
VIDEO_EXTS = {'.mp4', '.mov', '.mkv', '.avi', '.webm'}


def compress_image(input_path, output_path, target_size_mb=4):
    image = Image.open(input_path)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    target_size_bytes = target_size_mb * 1024 * 1024
    quality = 95

    image.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)

    while os.path.getsize(output_path) > target_size_bytes and quality > 10:
        quality -= 5
        image.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)

    print(f"✅ Compressed image saved: {output_path}")


def find_files(paths, exts, recursive=False):
    """Expand a list of paths (files, directories, glob patterns) and return files with matching extensions."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            if recursive:
                for root, _, filenames in os.walk(p):
                    for fn in filenames:
                        if os.path.splitext(fn)[1].lower() in exts:
                            files.append(os.path.join(root, fn))
            else:
                for fn in os.listdir(p):
                    fp = os.path.join(p, fn)
                    if os.path.isfile(fp) and os.path.splitext(fn)[1].lower() in exts:
                        files.append(fp)
        else:
            # Glob patterns or single files
            matches = glob.glob(p, recursive=recursive)
            for m in matches:
                if os.path.isfile(m) and os.path.splitext(m)[1].lower() in exts:
                    files.append(m)
    return sorted(set(files))


def compress_images_batch(paths, target_size_mb=4, out_dir=None, force=False, workers=4, recursive=False):
    files = find_files(paths, IMAGE_EXTS, recursive=recursive)
    if not files:
        print("❌ No image files found for the provided paths.")
        return

    print(f"🔎 Found {len(files)} images to compress. workers={workers}, out_dir={out_dir}, target={target_size_mb}MB")

    def _task(infile):
        base = os.path.basename(infile)
        outp = os.path.join(out_dir, "compressed_" + base) if out_dir else os.path.join(os.path.dirname(infile), "compressed_" + base)
        if os.path.exists(outp) and not force:
            print(f"ℹ️ Skipping {infile}; output exists: {outp}")
            return outp, False
        try:
            compress_image(infile, outp, target_size_mb=target_size_mb)
            return outp, True
        except Exception as e:
            print(f"❌ Failed to compress {infile}: {e}")
            return outp, False

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_task, f) for f in files]
        for fut in as_completed(futures):
            outp, ok = fut.result()
            if ok:
                print(f"✅ {outp}")

    print("✅ Batch image compression complete.")


def _find_ffmpeg():
    """Return (ffmpeg_exec, ffprobe_exec) where either may be None."""
    ffmpeg_exec = shutil.which('ffmpeg')
    ffprobe_exec = shutil.which('ffprobe')

    if ffmpeg_exec:
        return ffmpeg_exec, ffprobe_exec

    # Try bundled imageio-ffmpeg binary
    if imageio_ffmpeg is not None:
        try:
            ffmpeg_exec = imageio_ffmpeg.get_ffmpeg_exe()
            print("ℹ️ Using bundled ffmpeg from imageio-ffmpeg as fallback.")
            return ffmpeg_exec, None
        except Exception:
            pass

    return None, None


def _probe_duration(input_path, ffprobe_exec=None, ffmpeg_exec=None):
    # Prefer ffprobe if available
    if ffprobe_exec:
        try:
            dur_cmd = [
                ffprobe_exec, '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', input_path
            ]
            return float(subprocess.check_output(dur_cmd, universal_newlines=True).strip())
        except Exception:
            return None

    # Fall back to parsing ffmpeg -i stderr
    if ffmpeg_exec:
        try:
            p = subprocess.run([ffmpeg_exec, '-i', input_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            stderr = p.stderr
            m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', stderr)
            if m:
                hours, minutes, seconds = m.groups()
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        except Exception:
            return None

    return None


def _probe_audio_bitrate(input_path, ffprobe_exec=None, ffmpeg_exec=None):
    # Try ffprobe first
    if ffprobe_exec:
        try:
            a_cmd = [
                ffprobe_exec, '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', input_path
            ]
            audio_bitrate_str = subprocess.check_output(a_cmd, universal_newlines=True).strip()
            return int(audio_bitrate_str) if audio_bitrate_str else 128000
        except Exception:
            return 128000

    # Fallback: parse ffmpeg -i stderr for 'Audio: ... 128 kb/s' or similar
    if ffmpeg_exec:
        try:
            p = subprocess.run([ffmpeg_exec, '-i', input_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            stderr = p.stderr
            m = re.search(r'Audio:[^,]*,[^,]*,[^,]*,?\s*(\d+)\s*kb/s', stderr, re.IGNORECASE)
            if m:
                return int(m.group(1)) * 1000
        except Exception:
            return 128000

    return 128000


def compress_video(input_path, output_path, target_size_mb=30, force=False):
    """Compress a video to approximately target_size_mb using ffmpeg bitrate control.

    This function will attempt to use system ffmpeg/ffprobe. If they are not
    available and `imageio-ffmpeg` is installed, it will use the bundled ffmpeg
    binary from that package as a fallback.

    If `force=True`, the video will be re-encoded even if the input file is
    already smaller than the target size.
    """
    ffmpeg_exec, ffprobe_exec = _find_ffmpeg()

    if ffmpeg_exec is None:
        print("❌ No ffmpeg available. Install system ffmpeg or pip install imageio-ffmpeg")
        return

    target_size_bytes = target_size_mb * 1024 * 1024

    input_size = os.path.getsize(input_path)
    print(f"ℹ️ Input size: {input_size/1024/1024:.2f}MB; target: {target_size_mb}MB; force={force}")

    if input_size <= target_size_bytes and not force:
        shutil.copy2(input_path, output_path)
        print(f"✅ Video already under target size. Copied to: {output_path}")
        return

    duration = _probe_duration(input_path, ffprobe_exec=ffprobe_exec, ffmpeg_exec=ffmpeg_exec)
    if not duration:
        print("❌ Could not determine video duration (ffprobe/ffmpeg probing failed).")
        return

    audio_bitrate = _probe_audio_bitrate(input_path, ffprobe_exec=ffprobe_exec, ffmpeg_exec=ffmpeg_exec)

    # Compute target video bitrate (bits per second)
    total_bits = target_size_bytes * 8
    video_bitrate_bps = int(total_bits / duration) - audio_bitrate
    min_video_bitrate_bps = 100_000  # 100 kbps minimum for sanity

    if video_bitrate_bps < min_video_bitrate_bps:
        print("⚠️ Calculated video bitrate is very low; using minimum bitrate. Result may be poor quality or target may not be achievable.")
        video_bitrate_bps = min_video_bitrate_bps

    # ffmpeg expects bitrate like '500k'
    video_k = max(100, int(video_bitrate_bps / 1000))
    audio_k = max(64, int(audio_bitrate / 1000))
    video_bitrate = f"{video_k}k"
    audio_bitrate = f"{audio_k}k"

    print(f"🔧 Encoding with video bitrate={video_bitrate}, audio bitrate={audio_bitrate} (approx target: {target_size_mb}MB)")

    # Two-pass encode for better bitrate targeting
    pass1 = [
        ffmpeg_exec, '-y', '-i', input_path, '-c:v', 'libx264', '-b:v', video_bitrate,
        '-pass', '1', '-an', '-f', 'mp4', os.devnull
    ]
    pass2 = [
        ffmpeg_exec, '-y', '-i', input_path, '-c:v', 'libx264', '-b:v', video_bitrate,
        '-pass', '2', '-c:a', 'aac', '-b:a', audio_bitrate, output_path
    ]

    try:
        subprocess.run(pass1, check=True)
        subprocess.run(pass2, check=True)
    except subprocess.CalledProcessError:
        print("❌ ffmpeg failed to compress the video.")
        return
    finally:
        # Clean ffmpeg pass logs if they exist
        for fname in ('ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree'):
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except Exception:
                    pass

    print(f"✅ Compressed video saved: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compress images and videos to a target size (MB). Supports files, directories, and glob patterns.")
    parser.add_argument('paths', nargs='+', help='Path(s) to input files, directories, or glob patterns (e.g., images/*.jpg)')
    parser.add_argument('-t', '--target', type=float, default=None, help='Target size in MB (e.g., 5)')
    parser.add_argument('-f', '--force', action='store_true', help='Force re-encoding even if input is already under target size')
    parser.add_argument('-o', '--output', help='Output filename (single file) or output directory when batch-compressing')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively scan directories and glob patterns')
    parser.add_argument('-w', '--workers', type=int, default=4, help='Number of worker threads for batch image compression')

    args = parser.parse_args()

    paths = args.paths
    target_size_mb = args.target
    out = args.output

    # discover files
    image_files = find_files(paths, IMAGE_EXTS, recursive=args.recursive)
    video_files = find_files(paths, VIDEO_EXTS, recursive=args.recursive)

    if image_files:
        compress_images_batch(paths, target_size_mb=(target_size_mb if target_size_mb is not None else 4), out_dir=out if out and os.path.isdir(out) else out, force=args.force, workers=args.workers, recursive=args.recursive)

    if video_files:
        for v in video_files:
            outp = out if out and os.path.isdir(out) else (out if out else "compressed_" + os.path.basename(v))
            compress_video(v, outp, target_size_mb=(target_size_mb if target_size_mb is not None else 30), force=args.force)

    if not image_files and not video_files:
        print("❌ No supported files found for the given paths.")
