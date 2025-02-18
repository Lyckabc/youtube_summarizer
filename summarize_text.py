# summarize_text.py
import os
import anthropic
import re
import openai
import google.generativeai as genai

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

def prompt_syukaworld(text, lang='en', title=None):
    """
    Example prompt that uses 'title' to split into multiple topics (if possible)
    and then provides a structured analysis (1-4).
    """
    title_instruction = ""
    if title:
        topics = clean_and_split_title(title)
        if topics:
            title_instruction = f"""
Analyze the following topics from the title:
{' '.join(f'[{topic}]' for topic in topics)}

For each topic mentioned in the title, provide analysis in the format below:
"""
    prompt = f"""
The following text is in its original language. Provide the output in this language: {lang}.

{title_instruction}
For each topic, analyze the input text and provide the output in the following structure:

1. Detailed Explanation:
   - Provide a detailed and thorough explanation of the topic
   - Include any important context or information that adds depth to the understanding

2. Background Context:
   - Explain why this topic is being discussed
   - What triggered this discussion
   - Current relevance of this topic

3. Key Phrases and Concepts:
   - List important phrases, terms, or concepts that are central to understanding this topic
   - Include relevant quotes or specific language used in the text
   - Highlight any recurring themes or patterns

4. Overall Summary:
   - Summarize the topic in a concise, high-level overview that captures the essence of the discussion

Note: Focus on extracting meaningful connections and context for each topic while maintaining the relationship between topics where relevant. 
Take ample time to thoroughly analyze the input text, ensuring a nuanced and comprehensive understanding.
- If it helps clarity, feel free to use:
  - Emojis to highlight key ideas
  - Simple tables to compare points or summarize data
  - ASCII-based diagrams or flowcharts (textual graphs) for conceptual relationships

Input text:
{text}
"""
    return prompt

def make_summary_prompt(transcript, chapters=None, video_title=None, lang='en'):
    """
    Make a prompt for summarizing a YouTube transcript (or any text).
    
    If `chapters` is provided and not empty:
      - Use these chapters as topics.
    If `chapters` is None or empty:
      - Use the `video_title` or the transcript to infer possible topics.

    The summary should be structured into:
        1. Detailed Explanation
        2. Background Context
        3. Key Phrases and Concepts
        4. Overall Summary
    """
    if chapters and len(chapters) > 0:
        # 챕터가 있을 때: 챕터 목록을 그대로 토픽으로 활용
        topic_instruction = "\n".join(
            f"- {idx+1}. {chapter}" for idx, chapter in enumerate(chapters)
        )
        prompt = f"""
You are provided with the following text. Please analyze it and produce a summary in {lang}.

We have identified the following Chapters (topics):
{topic_instruction}

For each chapter listed above, analyze the content of the text and provide the following:

1. Detailed Explanation:
   - A thorough explanation of the chapter’s main points
   - Any important context or subtopics

2. Background Context:
   - Reasons or triggers for this chapter being discussed
   - Current relevance or context

3. Key Phrases and Concepts:
   - Important phrases, terms, or recurring ideas central to understanding this chapter
   - Quotes or noteworthy expressions

4. Overall Summary:
   - A concise, high-level overview capturing the essence of the chapter

Note: Focus on extracting meaningful connections and context for each topic while maintaining the relationship between topics where relevant. 
Take ample time to thoroughly analyze the input text, ensuring a nuanced and comprehensive understanding.
- If it helps clarity, feel free to use:
  - Emojis to highlight key ideas
  - Simple tables to compare points or summarize data
  - ASCII-based diagrams or flowcharts (textual graphs) for conceptual relationships

Text to analyze:
\"\"\"{transcript}\"\"\"
"""
    else:
        # 챕터가 없을 때: title/내용 분석을 통해 토픽을 유추
        title_instruction = (
            f"The title is: \"{video_title}\".\n"
            if video_title
            else "No explicit title is provided.\n"
        )
        prompt = f"""
You are provided with the following text. Please analyze it and produce a summary in {lang}.

{title_instruction}
No Chapters were found. 
Based on the title (if available) and the text, please identify the main topics or sections yourself. 
Then, for each identified topic, provide:

1. Detailed Explanation:
   - A thorough explanation of the topic’s main points
   - Any important context or subtopics

2. Background Context:
   - Reasons or triggers for this topic being discussed
   - Current relevance or context

3. Key Phrases and Concepts:
   - Important phrases, terms, or recurring ideas central to understanding this topic
   - Quotes or noteworthy expressions

4. Overall Summary:
   - A concise, high-level overview capturing the essence of the topic

Note: Focus on extracting meaningful connections and context for each topic while maintaining the relationship between topics where relevant. 
Take ample time to thoroughly analyze the input text, ensuring a nuanced and comprehensive understanding.
- If it helps clarity, feel free to use:
  - Emojis to highlight key ideas
  - Simple tables to compare points or summarize data
  - ASCII-based diagrams or flowcharts (textual graphs) for conceptual relationships

Text to analyze:
\"\"\"{transcript}\"\"\"
"""
    return prompt
def detailed_prompt(transcript, chapters=None, video_title=None, lang='en'):
    """
    Make a prompt for a detailed summary of a YouTube transcript (or any text),
    using emojis for better readability.

    If `chapters` is provided and not empty, we treat it as a list of chapters (split by \n).
    If `chapters` is None or empty, we do a general overall summary plus additional analysis.
    """

    # chapters를 문자열로 받았다고 가정하고, 유효한지 체크
    if chapters and chapters.strip(): 
        # 문자열을 \n로 분리하여 리스트화
        chapter_list = chapters.split('\n')

        # 챕터 기반 상세 요약
        prompt = f"""
You are provided with the following text. Please analyze it and produce a **detailed summary** in {lang}.

**Step 1: Overall Summary (First Paragraph)**  
   Please provide a concise yet comprehensive overview of the entire text **before** diving into each chapter.

**Step 2: Chapters**  
We have identified the following chapters (topics) :
{chapter_list}

For **each chapter** listed above, please detail:

1. **Detailed Explanation**  
   - A thorough explanation of the chapter’s main points  
   - Any important context or subtopics

2. **Background Context**  
   - Reasons or triggers for this chapter being discussed  
   - Current relevance or context

3. **Key Phrases and Concepts**  
   - Important phrases, terms, or recurring ideas central to understanding this chapter  
   - Quotes or noteworthy expressions

4. **Overall Summary**  
   - A concise, high-level overview capturing the essence of the chapter

**Note**  
- Focus on extracting meaningful connections and context for each chapter while maintaining relationships among topics.  
- Take ample time to thoroughly analyze the input text to ensure a nuanced and comprehensive understanding.
- If it helps clarity, feel free to use:
  - Emojis to highlight key ideas
  - Simple tables to compare points or summarize data
  - ASCII-based diagrams or flowcharts (textual graphs) for conceptual relationships

**Text to analyze**:  
\"\"\"{transcript}\"\"\"
"""
    else:
        # chapters가 없거나 빈 문자열인 경우: 전체 요약 + 추가 분석
        prompt = f"""
You are provided with the following text. Please analyze it and produce a **detailed summary** in {lang}.

**Step 1: Overall Summary (First Paragraph)**  
   First, provide an overarching summary that captures the main points of the entire text.

**Step 2: Additional Analysis**  
   - After giving the overall summary, please elaborate on:
     - Key background/context  
     - Important phrases or concepts  
     - Any other subtopics or noteworthy details

**Note**     
- You may structure your analysis however it fits best, but ensure clarity and depth.
- Focus on extracting meaningful connections and context for each chapter while maintaining relationships among topics.  
- Take ample time to thoroughly analyze the input text to ensure a nuanced and comprehensive understanding.
- If it helps clarity, feel free to use:
  - Emojis to highlight key ideas
  - Simple tables to compare points or summarize data
  - ASCII-based diagrams or flowcharts (textual graphs) for conceptual relationships

**Text to analyze**:  
\"\"\"{transcript}\"\"\"
"""

    return prompt
    

def summarize_text(
    text,              # 분석할 텍스트(예: 전체 자막)
    lang='en',         # 요약 결과 언어
    title=None,        # 영상 제목(또는 다른 제목)
    chapters=None,     # 인식된 챕터 목록 (있다면 리스트로, 없으면 None)
    api_choice='Anthropic', # 사용할 API 종류
    summarize_way='Summary' # 요약 방식 (예: 'Chapters' vs. 'Title' 등)
):
    # Claude API 키 환경 변수에서 가져오기
    if api_choice == 'Anthropic':
        client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif api_choice == 'OpenAI':
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif api_choice == 'Gemini':
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"Invalid API choice: {api_choice}")


    
    # 2) Prompt 결정
    if summarize_way == 'Chapters' and chapters:  
        # 챕터 기준 요약
        prompt = make_summary_prompt(
            transcript=text,
            chapters=chapters,
            video_title=title,
            lang=lang
        )
    elif summarize_way == 'Detailed':
        prompt = detailed_prompt(
            transcript=text,
            chapters=chapters,
            video_title=title,
            lang=lang
        )
    else:
        # title을 이용하는 syukaworld 방식
        prompt = prompt_syukaworld(
            text=text,
            lang=lang,
            title=title
        )
    
    # if Anthropic API
    if api_choice == 'Anthropic':
        response = client.completions.create(
            prompt=f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}",
            model="claude-3-5-haiku-20241022",
            max_tokens_to_sample=2000,
            temperature=0.5
        )
        summary_text = response['completion']
    #     response = client.messages.create(
    #         model="claude-3-5-haiku-20241022",
    #         max_tokens=8000,
    #     messages=[{
    #         "role": "user",
    #         "content": prompt
    #     }]
    # )
        # response = response.content[0].text
    
    # if OpenAI API
    elif api_choice == 'OpenAI':
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        summary_text = response.choices[0].message.content
    
    # if Gemini API
    elif api_choice == 'Gemini':
        model = genai.GenerativeModel('gemini-1.5-flash')
        messages = [
            {'role':'user',
             'parts': prompt}
        ]
        summary_text = model.generate_content(messages).text

    print(summary_text)
    return summary_text

if __name__ == "__main__":
    text_to_summarize = input("Enter the text to summarize: ")
    lang = input("Enter the language for the summary: ")
    title = input("Enter the title for the summary: ")
    summary = summarize_text(text_to_summarize, lang, title)
    print("Summary:")
    print(summary)