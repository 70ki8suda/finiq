# 使用例
# python generate-article.py "cnbc" "example.txt"

import os
import subprocess
import sys
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import yaml
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# .envファイルのパスを指定して読み込み
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class ArticleMetadata(BaseModel):
    title: str = Field(description="The article title in Japanese")
    date: str = Field(description="Publication date in YYYY-MM-DD format")
    category: str = Field(description="Article category")
    tags: List[str] = Field(description="List of relevant tags")
    summary: str = Field(description="Brief summary in Japanese")

class ArticleSection(BaseModel):
    content: str = Field(description="Translated content in Japanese")
    quality_score: float = Field(description="Quality score of the translation (0-1)")

def load_transcript(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

def split_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", "!", "?", ",", " "]
    )
    return splitter.split_text(text)

def clean_transcript(text: str, llm) -> str:
    prompt = ChatPromptTemplate.from_template("""
    あなたは、金融・経済ニュースの編集者として10年以上の経験を持つプロフェッショナルです。
    ポッドキャストの書き起こしから、重要な市場情報を抽出し、読みやすい記事に整理することを得意としています。
    
    以下のポッドキャストの書き起こしから、Markdown形式の記事に整形してください。

    重要な要件:
    1. 記事構造:
       - 適切な見出し（h2: ##, h3: ###）を設定してください
       - 重要なポイントは箇条書き（- または1. 2. 3.）を使用してください
       - 引用は > を使用してブロック引用してください
       - 重要な数値や用語は **太字** で強調してください
    
    2. 以下の情報は必ず保持してください：
       - 主要な市場動向や分析
       - 重要な数値データ
       - キーとなる予測や見通し
       - 専門家の重要な指摘
    
    3. 以下は削除または簡潔にしてください：
       - 広告セクション
       - 冗長な説明や繰り返し
    
    4. 全体の長さは原文の約70-90%程度を目安にしてください
    
    テキスト:
    {text}
    
    出力は整形されたテキストのみにしてください。
    """)
    
    # チェーンを構築
    chain = prompt | llm
    
    # 結果を取得し、文字列として返す
    result = chain.invoke({"text": text})
    
    # AIモデルの出力から実際のテキスト内容を取得
    if hasattr(result, 'content'):
        # ChatMessageのような場合
        return str(result.content)
    elif isinstance(result, dict) and 'text' in result:
        # 辞書の場合
        return str(result['text'])
    else:
        # その他の場合
        return str(result)

def generate_metadata(category: str, text: str, file_path: Path, llm) -> ArticleMetadata:
    # 1. パーサーを作成（ArticleMetadataの構造に基づく）
    parser = PydanticOutputParser(pydantic_object=ArticleMetadata)
    
    # 2. format_instructionsを取得
    # parser.get_format_instructions() は以下のような文字列を返します：
    # The output should be formatted as a JSON instance that conforms to the JSON schema below.
    # {
    #     "title": string,  // The article title in Japanese
    #     "date": string,   // Publication date in YYYY-MM-DD format
    #     "category": string,  // Article category
    #     "tags": array,    // List of relevant tags
    #     "summary": string // Brief summary in Japanese
    # }
    
    prompt = ChatPromptTemplate.from_template("""
   あなたは、SEOに精通したコンテンツストラテジストです。
    記事の内容を分析し、最適なメタデータ（タイトル、カテゴリー、タグなど）を抽出することを専門としています。
    
    以下のテキストから、記事のメタデータを抽出してください。
    
    要件：
    1. タイトルは検索エンジンで見つけやすく、かつ内容を適切に表現するものにしてください
    2. カテゴリーはこちらから指定したものをそのまま加工せずでお願いします
    3. タグは検索やナビゲーションに有用なものを5-8個程度選択してください
    4. 要約は記事の主要なポイントを簡潔に表現してください
    5. 西暦の年数をタイトルに含む場合は正しい年数を表記するように注意してください (2024年についての情報であれば2024年、2025年についての情報であれば2025年と表記するように注意してください。誤った表記はメディアの信頼性を損ねます)
    
    カテゴリー:
    {category}
    テキスト:
    {text}
    
    {format_instructions}
    """)
    
    # 3. プロンプトにformat_instructionsを部分的に適用
    formatted_prompt = prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # 4. チェーンを構築して実行
    chain = formatted_prompt | llm | parser
    result = chain.invoke({"text": text, "category": category})
    
    # 5. 日付を設定して返す
    result.date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
    return result


def generate_slug(file_name: str, date: str) -> str:
    """
    ファイル名をURL用のslugに変換する
    例: "Dow's losing streak, Nvidia buying opportunity" -> "2024-03-21-dow-nvidia-market"
    """
    import re
    from typing import Set
    
    # 除外する一般的な単語のリスト
    STOP_WORDS: Set[str] = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after'
    }
    
    base_name = os.path.splitext(file_name)[0]
    
    # 特殊文字を削除
    slug = re.sub(r'[\'’"".,!?&…]', '', base_name)
    
    # 単語に分割して小文字に変換
    words = [w.lower() for w in re.split(r'[\s_-]+', slug)]
    
    # ストップワードを除外
    content_words = [w for w in words if w not in STOP_WORDS]
    
    # 最大3単語を選択
    selected_words = content_words[:3]
    
    # スラッグを生成
    slug = '-'.join(selected_words)
    
    return f"{date}-{slug}"
    

def translate_and_evaluate(text: str, llm) -> ArticleSection:
    parser = PydanticOutputParser(pydantic_object=ArticleSection)
    prompt = ChatPromptTemplate.from_template("""
    あなたは、金融・経済分野の専門的な翻訳者として15年以上の経験を持つエキスパートです。
    特に市場分析や経済レポートの翻訳を得意とし、専門用語の適切な日本語化と、文脈を考慮した自然な翻訳には定評があります。
    
    以下の英語のテキストを、Markdown形式の日本語記事に翻訳してください。

    翻訳と構造化の要件:
    1. Markdownの書式:
       - 適切な見出しレベル（##, ###）を使用してください
       - 重要なポイントは箇条書き（- または数字）を使用
       - 専門家の発言は > を使用してブロック引用
       - 重要な数値や用語は **太字** で強調
       - 必要に応じて水平線 (---) で区切り
    
    2. 翻訳の要点:
       - 重要な市場情報、分析、予測は詳しく翻訳
       - 数値データや具体的な事例は正確に翻訳
       - 専門用語は（）内に英語を併記
       - 文脈を考慮した自然な日本語に
       - 冗長な部分は適度に簡潔に
    
    3. 構成例：
       ## セクションタイトル
       
       主要な内容説明...
       
       ### サブセクション
       - 重要ポイント1
       - 重要ポイント2
       
       > 専門家の発言や重要な引用
       
       ### 今後の展望
       将来予測について...
    
    原文:
    {text}
    
    {format_instructions}
    """)
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt.partial(format_instructions=parser.get_format_instructions())
    )
    
    result = chain.run(text=text)
    return parser.parse(result)

def improve_translation(section: ArticleSection, llm) -> ArticleSection:
    if section.quality_score >= 0.8:
        return section
        
    parser = PydanticOutputParser(pydantic_object=ArticleSection)
    prompt = ChatPromptTemplate.from_template("""
    あなたは、日本の金融メディアで20年以上の経験を持つ編集長です。
    特に以下の点に定評があります：
    - 複雑な金融概念を分かりやすく説明する能力
    - 自然で読みやすい日本語表現への編集力
    - 金融専門用語の適切な使用と解説
    - 論理的で説得力のある文章構成力
    
    以下のMarkdown形式の翻訳文を改善してください。

    改善の要件:
    1. Markdown構造の維持と改善:
       - 見出しレベル（##, ###）の適切性を確認
       - 箇条書きの効果的な使用
       - ブロック引用（>）の適切な使用
       - 重要な数値や用語の強調（**太字**）
    
    2. 文章の改善:
       - 自然な日本語表現に調整
       - 専門用語の適切な使用と解説
       - 文の長さと構造の最適化
       - 情報の論理的な配置
    
    3. 以下の点は維持してください：
       - Markdownの基本構造
       - 重要な市場情報や分析
       - 数値データの正確性
       - 専門家の見解や予測
    4. "この記事は、ブルームバーグニュースのポッドキャストからの情報を基に作成されました。"のように出展をほのめかすような文章は削除してください。
    
    現在の翻訳:
    {text}
    
    {format_instructions}
    """)
    
    chain = prompt | llm | parser
    result = chain.invoke({"text": section.content})
    return result

def save_article(metadata: ArticleMetadata, content: str, output_path: str):
    # ファイル名を生成
    slug = generate_slug(os.path.basename(output_path), metadata.date)
    output_path = os.path.join(os.path.dirname(output_path), f"{slug}.md")
    
    # Prepare frontmatter
    frontmatter = {
        'title': metadata.title,
        'date': metadata.date,
        'category': metadata.category,
        'tags': metadata.tags,
        'summary': metadata.summary
    }
    
    # Create markdown content
    markdown_content = f"""---
{yaml.dump(frontmatter, allow_unicode=True)}---

{content}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def main(category: str, file_name: str):
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        max_tokens=4000
    )
    
    # スクリプトの親ディレクトリを基準にパスを設定
    base_dir = Path(__file__).parent.parent  # finiqディレクトリ
    transcript_dir = base_dir / "transcript"
    content_dir = base_dir / "content"
    
    # 指定されたカテゴリーのパスを構築
    category_path = transcript_dir / category
    if not category_path.is_dir():
        raise ValueError(f"Category directory not found: {category_path}")
    
    # 出力カテゴリーディレクトリを作成
    output_category_path = content_dir / category
    output_category_path.mkdir(parents=True, exist_ok=True)
    
    # 指定されたファイルのパスを構築
    transcript_path = category_path / file_name
    if not transcript_path.exists():
        raise ValueError(f"Transcript file not found: {transcript_path}")
    
    print(f"Processing {file_name}...")
    
    # Load and clean transcript
    raw_text = load_transcript(transcript_path)
    cleaned_text = clean_transcript(raw_text, llm)
    
    # Generate metadata
    metadata = generate_metadata(category, cleaned_text, transcript_path, llm)

    # Split text and translate
    sections = []
    for chunk in split_text(cleaned_text):
        section = translate_and_evaluate(chunk, llm)
        if section.quality_score < 0.8:
            section = improve_translation(section, llm)
        sections.append(section)
    
    # Combine translated sections
    full_content = "\n\n".join(section.content for section in sections)

    # Execute the write-ai-agent-colum.py script and append its output to full_content
    try:
        # Run the write-ai-agent-colum.py script
        result = subprocess.run(
            [sys.executable, "write-ai-agent-column.py", str(transcript_path)],
            capture_output=True,
            text=True,
            check=True
        )
        # Append the column content to full_content
        full_content += "\n\n" + result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running write-ai-agent-colum.py: {e}")
        sys.exit(1)
    
    # Save as markdown
    output_file = os.path.splitext(file_name)[0] + '.md'
    output_path = os.path.join(output_category_path, output_file)
    save_article(metadata, full_content, output_path)
    
    print(f"✅ Article generated: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate article from transcript')
    parser.add_argument('category', help='Category directory name (e.g., "cnbc")')
    parser.add_argument('file_name', help='Transcript file name (e.g., "example.txt")')
    
    args = parser.parse_args()
    main(args.category, args.file_name)