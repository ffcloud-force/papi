from backend.modules.llm.assistant import LLM_Assistant
from backend.modules.llm.prompts.exam_prompts import get_examiner_prompt, get_prompt_by_id, get_output_format, get_all_prompt_ids

def generate_all_questions(self):
    """Generate questions for all prompt types"""
    results = {}
    for prompt_id in get_all_prompt_ids():
        results[prompt_id] = self.formulate_question(prompt_id)
    import pdb; pdb.set_trace()
    return results

def formulate_question(self, prompt_id):
    """Formulate a question for a given prompt ID"""
    if self.case_text is None:
        raise ValueError("Case text not loaded, please use load_case_document() first")

    prompt = get_examiner_prompt()
    prompt += get_prompt_by_id(prompt_id)
    prompt += "Nachfolgend bekommst du den Falltext. Erstelle Fragen zu diesem Fall, welche das oben genannte Thema betreffen: "
    prompt += "\n\n" + self.case_text
    prompt += get_output_format()
    
    return self._get_completion(prompt, json_mode=True)

def generate_exam_questions(case_file_path):
    """Service function to generate all questions for a case"""
    assistant = LLM_Assistant()
    assistant.load_case_document(case_file_path)
    return assistant.generate_all_questions()