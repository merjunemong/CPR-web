from openai import OpenAI

def getSkillsFromAnswers(answers):

  # client = OpenAI()

# api호출 비용 아끼기
  # response = client.chat.completions.create(
  #   model="gpt-4o",
  #   messages=[
  #     {
  #       "role": "system",
  #       "content": [
  #         {
  #           "text": "저는 리스트를 입력으로 받아  각 입력의 문장에서 역량을 명사로 추출하는 것이 저의 업무입니다.  예를 들어 역량으로 판단된 단어 중에서 '명사A의 명사B' 같은 단어가 있으면 '명사A 명사B' 같은 형태로 역량을 추출합니다. 하지만 명사A 명사B가 역량이 아니라면 배제합니다.\n하지만 명사A가 명사B의 부연 설명이 아니라면 배제합니다.\n그리고 직업과 사회적 및 개인적 역량은 꼭 출력 역량에서 배제됩니다.\n출력은 꼭 추출한 역량을 열거해서 출력하되,  최종 형식은, , 의 형태로만 나열합니다.\n그리고 무조건 중복은 제거합니다."
  #           "type": "text"
  #         }
  #       ]
  #     },
  #     {
  #       "role": "user",
  #       "content": [
  #         {
  #           "text": f"{answers}"
  #           "type": "text"
  #         }
  #       ]
  #     }
  #   ],
  #   temperature=1,
  #   max_tokens=2048,
  #   top_p=1,
  #   frequency_penalty=0,
  #   presence_penalty=0,
  #   response_format={
  #     "type": "text"
  #   }
  # )

  # answer = response.choices[0].message.content.strip()
  # skills = answer.split(": ")[1]
  # skills_list = skills.split(", ")
  skills_list = ["프로그램 기획", "기획안 작성", "장단점 분석", "아이디어 기획", "촬영 편집", "아이디어 정리"]
  return skills_list
