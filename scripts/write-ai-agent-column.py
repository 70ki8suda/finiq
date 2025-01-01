import argparse
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI  # OpenAI's ChatGPT APIを使用
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from pathlib import Path

# .envファイルのパスを指定して読み込み
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Define state schema
class State(TypedDict):
    file_path: str
    text_content: str
    investment_advisor_column: str | None

# Define a node for data collection
class DataCollectionNode:
    def run(self, state: State) -> State:
        file_path = state["file_path"]
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        state["text_content"] = content
        return state

# Define a node for data analysis and column generation
class ColumnGenerationNode:
    def __init__(self):
        # Initialize ChatGPT
        # self.llm = ChatOpenAI(
        #     model="gpt-4o", 
        #     temperature=0.7
        # )
        self.llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.7)

    def run(self, state: State) -> State:
        text_content = state["text_content"]
        
        # Generate prompt for the AI
        prompt = f"""
        あなたは、テスタさんやジョージ・ソロスのような一流投資家です。
        以下の記事内容を分析し、プロの一流投資家ならではの視点から記事の特に気になったトピックについて意見や考察を述べてください
        『資産形成には長期的な視点が欠かせません』のような一般論は価値がないので必要ありません。記事で述べられている具体的なトピックに関連する形で知見や意見を述べてください。
        出力はマークダウン形式で日本語でお願いします。
        タイトルは『AIエージェント コラム』でお願いします。

        記事内容:
        {text_content}
        """

        # Generate investment advice using ChatGPT
        response = self.llm.invoke(prompt)
        
        # Update state with generated column
        state["investment_advisor_column"] = response.content
        return state

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate an investment advisor column based on a text file.')
    parser.add_argument('file_path', type=str, help='Path to the text file containing the article content')

    # Parse the arguments
    args = parser.parse_args()

    # Create nodes
    data_collection = DataCollectionNode()
    column_generation = ColumnGenerationNode()

    # Create a workflow with state schema
    workflow = StateGraph(State)

    # Add nodes to the workflow
    workflow.add_node("collect_data", data_collection.run)
    workflow.add_node("generate_column", column_generation.run)

    # Add edges to connect the nodes
    workflow.add_edge(START, "collect_data")
    workflow.add_edge("collect_data", "generate_column")
    workflow.add_edge("generate_column", END)

    # Compile the workflow
    app = workflow.compile()

    # Create initial state
    initial_state = {"file_path": args.file_path, "text_content": "", "investment_advisor_column": None}

    # Execute the workflow
    final_state = app.invoke(initial_state)

    # Print the generated column
    print(final_state["investment_advisor_column"])

if __name__ == "__main__":
    main()