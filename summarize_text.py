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

def summarize_text(text, lang='en', title=None, api_choice='Anthropic'):
    # Claude API 키 환경 변수에서 가져오기
    if api_choice == 'Anthropic':
        client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif api_choice == 'OpenAI':
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif api_choice == 'Gemini':
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"Invalid API choice: {api_choice}")

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

    Repeat the above format for each topic provided in the input.

    Note: Focus on extracting meaningful connections and context for each topic while maintaining the relationship between topics where relevant. Take ample time to thoroughly analyze the input text, ensuring a nuanced and comprehensive understanding of each topic before crafting the output. Avoid rushing the interpretation to preserve depth and accuracy.

    input text: {text}
    """


    
    # if Anthropic API
    if api_choice == 'Anthropic':
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=8000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
        response = response.content[0].text
    
    # if OpenAI API
    elif api_choice == 'OpenAI':
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        response = response.choices[0].message.content
    
    # if Gemini API
    elif api_choice == 'Gemini':
        model = genai.GenerativeModel('gemini-1.5-flash')
        messages = [
            {'role':'user',
             'parts': prompt}
        ]
        response = model.generate_content(messages).text
        # print(response.text)
    
    # 응답에서 텍스트 추출
    summary_text = response
    print(summary_text)
    return summary_text

if __name__ == "__main__":
    text_to_summarize = input("Enter the text to summarize: ")
    lang = input("Enter the language for the summary: ")
    title = input("Enter the title for the summary: ")
    summary = summarize_text(text_to_summarize, lang, title)
    print("Summary:")
    print(summary)