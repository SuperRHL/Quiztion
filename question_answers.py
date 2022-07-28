class Question:
    def __init__(self, question, answers):
        self.question = question
        self.answers = answers

class Answer:
    def __init__(self, answer, description, isright):
        self.answer = answer
        self.description = description
        self.isright = isright
