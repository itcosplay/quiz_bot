import json

def get_text_by_index(list, start_index):
    text = ''

    for row_index in range(start_index, len(list)):
        if list[row_index-1].startswith('\n'):
            return text

        elif not list[row_index].startswith('\n'):
            text += list[row_index]

    return None
        

with open('1vs1200.txt', 'r', encoding='KOI8-R') as questions_file:
    questions_file_rows = [row for row in questions_file]


questions_and_answers = []
for row_index in range(0, len(questions_file_rows)):
    if questions_file_rows[row_index].startswith('Вопрос') \
        and questions_file_rows[row_index-1].startswith('\n'):
        question_answer = {
            'question': None,
            'answer': None
        }
        question=get_text_by_index (
            list = questions_file_rows,
            start_index = row_index + 1
        )
        question_answer['question'] = question.replace('\n', ' ')

    if questions_file_rows[row_index].startswith('Ответ') \
        and questions_file_rows[row_index-1].startswith('\n'):

        answer=get_text_by_index (
            list = questions_file_rows,
            start_index = row_index + 1
        )
        question_answer['answer'] = answer.replace('\n', ' ')

        questions_and_answers.append(question_answer)
        question_answer = {
            'question': None,
            'answer': None
        }

print(questions_and_answers)

with open("quiz_data.json", "w") as write_file:
    json.dump(questions_and_answers, write_file)



