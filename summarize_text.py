import os
import anthropic
import re

def clean_and_split_title(title):
    """
    Remove prefix in brackets and split title into topics
    
    Args:
        title (str): Title string possibly containing prefix in brackets
    
    Returns:
        list: List of cleaned topic strings
    """
    # Remove prefix in brackets (e.g., [슈카월드])
    cleaned_title = re.sub(r'^\s*\[[^\]]+\]\s*', '', title)
    
    # Split by '/' and clean each topic
    topics = [topic.strip() for topic in cleaned_title.split('/')]
    
    return topics

def summarize_text(text, lang='en', title=None):
    # Claude API 키 환경 변수에서 가져오기
    client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Title parsing instruction
    title_instruction = ""
    if title:
        topics = clean_and_split_title(title)
        title_instruction = f"""
    Analyze the following topics from the title:
    {' '.join(f'[{topic}]' for topic in topics)}
    
    For each topic mentioned in the title, provide analysis in the format below.
    """
    
    prompt = f"""
    The following text is in its original language. Provide the output in this language: {lang}.
    
    {title_instruction}
    First, provide a concise overview summary of the entire text for each topic.
    Then, analyze each topic using the following format:

    For each topic:
    1. Background Context:
       - Explain why this topic is being discussed
       - What triggered this discussion
       - Current relevance of this topic
    
    2. Key Phrases and Concepts:
       - List important phrases, terms, or concepts that are central to understanding this topic
       - Include relevant quotes or specific language used in the text
       - Highlight any recurring themes or patterns

    Format the output exactly as follows:
    Overall Summary:
    [summary of the entire text for each topic]

    Topic Analysis:
    [Topic 1]:

    Background Context:
    * [Why this topic emerged]
    * [Current significance]
    
    Key Phrases and Concepts:
    * [Important phrase or concept 1]
    * [Important phrase or concept 2]
    
    [Continue for each topic in the title...]
    
    Note: Focus on extracting meaningful connections and context for each topic while maintaining the relationship between topics where relevant.
    
    input text: {text}
    """
    
    # Claude API 호출
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # 응답에서 텍스트 추출
    summary_text = response.content[0].text
    print(summary_text)
    return summary_text

if __name__ == "__main__":
    text_to_summarize = input("Enter the text to summarize: ")
    lang = input("Enter the language for the summary: ")
    title = input("Enter the title for the summary: ")
    summary = summarize_text(text_to_summarize, lang, title)
    print("Summary:")
    print(summary)