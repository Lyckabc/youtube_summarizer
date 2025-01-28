import os
# from openai import OpenAI
# from dotenv import load_dotenv
import google.generativeai as genai
# load_dotenv()


# def test_openai_connection():
#     """
#     OpenAI API 연결을 테스트하는 함수
#     """
#     try:
#         # .env 파일에서 환경변수 로드
#         load_dotenv()
        
#         # API 키 가져오기
#         api_key = os.environ.get('OPENAI_API_KEY')
#         if not api_key:
#             raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

#         # OpenAI 클라이언트 초기화
#         client = OpenAI(api_key=api_key)

#         # 간단한 테스트 메시지 전송
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "user", "content": "Hello, API test!"}
#             ]
#         )

#         # 응답 확인
#         if response.choices[0].message.content:
#             print("✅ API 테스트 성공!")
#             print(f"응답: {response.choices[0].message.content}")
#             return True
        
#     except Exception as e:
#         print(f"❌ API 테스트 실패: {str(e)}")
#         return False

def test_gemini_connection():
    """
    Gemini API 연결을 테스트하는 함수
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        messages = [
            {'role':'user',
             'parts': ["Hello, API test!"]}
        ]
        response = model.generate_content(messages)
        print(response.text)
        return True
    except Exception as e:
        print(f"❌ Gemini API 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    # 필요한 패키지 설치 안내
    print("필요한 패키지 설치:")
    print("pip install openai python-dotenv")
    # print("\n환경 변수 설정 방법:")
    # print("1. 프로젝트 루트에 .env 파일 생성")
    # print("2. .env 파일에 다음 내용 추가:")
    # print("OPENAI_API_KEY=your-api-key-here")
    print("\n테스트 실행 중...\n")
    
    # 테스트 실행
    # test_openai_connection()
    test_gemini_connection()

    # 테스트 완료
    print("\n테스트 완료!")