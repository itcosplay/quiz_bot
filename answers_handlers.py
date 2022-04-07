def get_short_answer(unswer):
    return unswer.replace(
        ',', '.').replace(
        '(', '.').replace('"', '.').split('.')[0].strip().lower()


def get_explanation(right_answer):
    index = 0
    for char in right_answer:
        if char == '.':
            index += 1
            break
        if char == ',':
            break
        if char == '(':
            index -= 1
            break

        index += 1

    explanation = right_answer[index:].strip()

    if len(explanation) > 2:

        return right_answer[index:]

    return ''
