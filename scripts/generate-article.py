# 実行例
# python generate-article.py /path/to/audio.mp3 category_name 

import subprocess
import sys
import os

def run_generate_transcript(mp3_file, category):
    try:
        # Run generate-transcript.py
        subprocess.run(
            [sys.executable, "generate-transcript.py", mp3_file, category],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running generate-transcript.py: {e}")
        sys.exit(1)

def run_generate_article(category, file_name):
    try:
        # Run generate-article-from-transcript.py
        subprocess.run(
            [sys.executable, "generate-article-from-transcript.py", category, file_name],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running generate-article-from-transcript.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_all.py <mp3_file> <category>")
        sys.exit(1)

    mp3_file = sys.argv[1]
    category = sys.argv[2]

    # Run the transcript generation
    run_generate_transcript(mp3_file, category)

    # Determine the transcript file name
    transcript_file_name = os.path.splitext(os.path.basename(mp3_file))[0] + '.txt'

    # Run the article generation
    run_generate_article(category, transcript_file_name)