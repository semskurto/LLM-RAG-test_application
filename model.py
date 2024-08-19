from transformers import T5Tokenizer, T5ForConditionalGeneration

class AnswerGenerator:
    def __init__(self, model_name='google/flan-t5-base'):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def generate_answer(self, context, question):
        input_text = f"question: {question} context: {context}"
        inputs = self.tokenizer.encode(input_text, return_tensors='pt')
        outputs = self.model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer