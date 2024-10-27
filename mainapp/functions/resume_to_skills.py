from openai import OpenAI
from .pdf_to_txt_PyPDF2 import pdf_to_text

def getSkillsFromResume(filePath):

  # client = OpenAI()

  user_content = pdf_to_text(filePath)

# api호출 비용 아끼기
  # response = client.chat.completions.create(
  #   model="gpt-3.5-turbo-0125",
  #   messages=[
  #     {"role": "system",
  #       "content": "너는 사용자가 입력한 이력서 정보를 text로 입력받으면 이력서를 검토해서 사용자가 가진 모든 skill들을 추출해서 알려주는 시스템이다. \n이력서를 통해 알 수 있는 skill들과 그로부터 유추할 수 있는 skill들을 추출한 뒤에 알려주어야 한다.\nskill을 추출할 때 \n이전에 가졌던 직업이 있다면 직업명도 표시하여야 하고,\n자격증의 경우 자격증명을 표시해야 하고,\n외국어 시험 점수의 경우 시험명만 표시하고 몇점인지는 따로 표시하지 않아야 하고,\n가족과 관련된 정보, 신체정보는 무시해야 한다.\nskill_list에서 skill과 skill 사이를 ', '로 분리하여 출력한다.\n출력 템플릿 대로만 답변해야 한다. 다른 단어나 문장을 추가하지 마라.\n\n입력된 정보로 3번 추론해보고 마지막 결과를 템플릿에 맞춰 출력하라.\n\n출력 템플릿은 아래와 같다.\n\n스킬:{skill_list}"},
  #     {"role": "user", "content": f"{user_content}"},
  #   ]
  # )

  # answer = response.choices[0].message.content.strip()
  # skills = answer.split(": ")[1]
  # skills_list = skills.split(", ")
  skills_list = ["데이터 분석", "정보처리기사", "영어능력", "컴퓨터 프로그래밍", "리더십", "팀워크", "웹 개발", "데이터베이스 관리"]
  return skills_list
