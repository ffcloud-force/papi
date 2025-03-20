from backend.modules.llm.assistant import LLM_Assistant
from backend.modules.llm.prompt_manager import get_all_prompt_configs

def generate_all_questions(url_path):
    """Generate questions for all prompt types for a given case"""
    assistant = LLM_Assistant()
    assistant.load_case_document(url_path)
    results = {}
    configs = get_all_prompt_configs()
    
    for config in configs:
        if config["type"] == "general":
            key = config["general_type"]
            questions_str = assistant.formulate_general_case_question(key)
        else:
            general_type = config["general_type"]
            specific_type = config["specific_type"]
            key = f"{general_type}/{specific_type}"
            questions_str = assistant.formulate_specific_case_question(general_type, specific_type)
        import pdb; pdb.set_trace()
        parsed_questions = assistant.process_answer(questions_str, general_type, specific_type)
        results[key] = parsed_questions
        
    return results
