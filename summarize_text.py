import os
import anthropic

def summarize_text(text, lang='en'):
    # Claude API 키 환경 변수에서 가져오기
    client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # 프롬프트 구성
    prompt = f"""
    The following text is in its original language. Provide the output in this language: {lang}.
    
    Format the output as follows:
    Summary:
    short summary of the text
    
    Key Takeaways:
    succinct bullet point list of key takeaways
    
    input text: {text}
    """
    
    # Claude API 호출
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # 응답에서 텍스트 추출
    summary_text = response.content[0].text
    return summary_text

if __name__ == "__main__":
    text_to_summarize = input("Enter the text to summarize: ")
    lang = input("Enter the language for the summary: ")
    summary = summarize_text(text_to_summarize, lang)
    print("Summary:")
    print(summary)