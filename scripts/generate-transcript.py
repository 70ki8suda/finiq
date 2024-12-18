import whisper
import os
import sys

# 実行時渡すのはmp3の絶対パスとカテゴリー名
# /fuga/hoge.mp3 cnbc

def generate_transcript(mp3_file, output_dir):
    # Whisperモデルのロード
    model = whisper.load_model("base")
    # 音声ファイルのトランスクリプトを生成
    result = model.transcribe(mp3_file)
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    # output_file_nameをmp3_pathから取り出し、拡張子を.txtに変更
    output_file_name = os.path.splitext(os.path.basename(mp3_file))[0] + '.txt'  # {{ edit_1 }}
    # トランスクリプトをファイルに保存
    output_file = os.path.join(output_dir, output_file_name)  # 引数で受け取ったファイル名を使用
    try:
        # ... existing code ...
        with open(output_file, "w") as f:
            f.write(result['text'])
        print(f"✅ Transcript generated successfully: {output_file}")
    except Exception as e:
        print(f"❌ Error generating transcript: {str(e)}")
        raise

# コマンドライン引数の取得
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Error: Incorrect number of arguments")
        print("Usage: python generate-transcript.py <mp3_file> <output_dir>")
        sys.exit(1)

    try:
        mp3_path = sys.argv[1]
        sub_dir = sys.argv[2]
        output_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "transcript", sub_dir)
        
        generate_transcript(mp3_path, output_directory)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)