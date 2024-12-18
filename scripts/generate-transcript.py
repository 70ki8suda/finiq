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
    with open(output_file, "w") as f:
        f.write(result['text'])

# コマンドライン引数の取得
if __name__ == "__main__":
    if len(sys.argv) != 3:  # 2つの引数を期待
        print("Usage: python generate-transcript.py <mp3_file> <output_dir>")
        sys.exit(1)

    # MP3ファイルのパスを構築
    mp3_path =  sys.argv[1]
    # 出力ディレクトリを構築
    sub_dir = sys.argv[2]  # 引数からサブディレクトリ名を取得
    output_directory = os.path.join("finiq/content", sub_dir)

    generate_transcript(mp3_path, output_directory)  # 引数からoutput_file_nameを削除