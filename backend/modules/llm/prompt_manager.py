from backend.modules.llm.prompts.exam_prompts import EXAM_PROMPTS

def get_all_prompt_configs():
    """Returns a list of all prompt configurations"""
    configs = []
    
    # Process simple prompts
    for question_type in EXAM_PROMPTS["case_questions"].keys():
        configs.append({"type": "general", "general_type": question_type})
    
    # Process nested prompts
    for general_type, specific_types in EXAM_PROMPTS["case_questions_tp"].items():
        for specific_type in specific_types.keys():
            configs.append({
                "type": "specific", 
                "general_type": general_type, 
                "specific_type": specific_type
            })
            
    return configs
