import ollama

ollama_client = ollama.Client(host="192.168.1.42:11435")


def extract_boolean_model_response(model_response: str) -> bool:
    match model_response:
        case "0":
            return False
        case "1":
            return True
        case _:
            print(
                "Error the model did not return neither true or false. Counting that as false"
            )
            return False


def get_llm_response(system_prompt: str, text: str):
    res = ollama_client.generate(
        model="gemma2:2b",
        options={"temperature": 0.15},
        prompt=f"## Task \n {system_prompt} \n ## Text \n {text}",
    )["response"]
    return res


def _get_ai_advice(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to: \
                    Identify what went well in the presentation excerpt – this includes strengths \
                    in the flow, coherence, tone, and any other effective elements. Identify any \
                    aspects that could be improved – such as grammatical errors, awkward phrasings, \
                    or disruptions in the logical flow. Provide clear, actionable advice for \
                    enhancing the overall quality of the presentation. Note that the presentation \
                    text may not include the typical opening or closing statements. Your feedback \
                    should focus mainly on the flow of sentences, clarity, engagement, and overall \
                    delivery of the content. Also take into cosideration if the speaker switched topics \
                    throughout the presentation and if too many numbers were used. The response should be \
                    short and concise. Your should always respond in Polish."

    return get_llm_response(system_prompt, text)


def _did_change_topics(text: str) -> bool:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    identify if the speaker changed topics during the presentation. \
                    If the speaker did not change topics during the presentation output \
                    '0', otherwise, if the speaker did change topics during the presentation, \
                    output '1'. Always respond with only one character (1 or 0)."

    return extract_boolean_model_response(get_llm_response(system_prompt, text))


def _did_use_too_many_numbers(text: str) -> bool:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    identify if there are too many numbers used in the presentation. \
                    If there are too many numberse used in the presentation you should \
                    respond with '1', otherwise, if the presentation does not contain too \
                    many numbers, respond with '0'. Be liberal with the ammount of numbers \
                    the speaker is allowed to use. Always respond with only one character \
                    (1 or 0)."

    return extract_boolean_model_response(get_llm_response(system_prompt, text))


def _did_make_repetitions(text: str) -> bool:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    identify if there are repetitions in the presentation. \
                    If there are repetitions in the presentation you should \
                    respond with '1', otherwise, if there are no repetitions, \
                    respond with '0'. Always respond with only one character (1 or 0)."

    return extract_boolean_model_response(get_llm_response(system_prompt, text))


def _did_use_passive_voice(text: str) -> bool:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    identify if the speaker used passive voice. \
                    If the speaker did use passive voice in the presentation you should \
                    respond with '1', otherwise, if the speaker did not use passive voice, \
                    respond with '0'. Always respond with only one character (1 or 0)."

    return extract_boolean_model_response(get_llm_response(system_prompt, text))


def _get_further_questions(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    create a few question based on the presentations. Separate questions \
                    with new lines. Always respond in Polish."

    return get_llm_response(system_prompt, text)


def _get_target_audience(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    determin the targe audience to the best of your ability. Answer with just one word, \
                    the target audience. Always respind in Polish."

    return get_llm_response(system_prompt, text)


def _get_revised_presentation(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to, \
                    given this presentation, prepare a revised version of it, where you \
                    strengthen its flow, coherance, tone and any other effective elements. \
                    Identify any aspects that could be improved – such as grammatical errors, \
                    awkward phrasings, or disruptions in the logical flow. Your revived presentation \
                    should not widly differ from the original presentation. Always respond in Polish."

    return get_llm_response(system_prompt, text)


def _get_translated_presentation(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis, feedback and translation. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to \
                    translate the given excerpt to English."

    return get_llm_response(system_prompt, text)


def _get_is_vulgar(text: str) -> bool:
    system_prompt = "You are an expert in presentation analysis and feedback. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to determine if any \
                    part of the given presentation is vulgar, does it contain any swear words. \
                    If so, then output '1', otherwise, if there is no vulgariy in the excerpt, output \
                    '0'. Always respond with only one character (1 or 0)."

    return extract_boolean_model_response(get_llm_response(system_prompt, text))


def _get_sentiment(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis, feedback and translation. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to determine the \
                    sentiment of the presentation. You should respond with just one word. Always \
                    respond in Polish."

    return get_llm_response(system_prompt, text)


def _get_key_phrase(text: str) -> str:
    system_prompt = "You are an expert in presentation analysis, feedback and translation. A user will \
                    provide you with an excerpt from a presentation in Polish, which may start in the \
                    middle or include only parts of the presentation. Your task is to extract the key phrase or \
                    the key sentence. Always respond in Polish."

    return get_llm_response(system_prompt, text)


def get_ai_textual_report(video_uuid, text):
    report_data = {}
    report_data["ai_advice"] = _get_ai_advice(text)
    report_data["too_many_numbers_usesd"] = _did_use_too_many_numbers(text)
    report_data["chage_of_topic"] = _did_change_topics(text)
    report_data["repetitions"] = _did_make_repetitions(text)
    report_data["passive_voice"] = _did_use_passive_voice(text)
    report_data["further_questions"] = _get_further_questions(text)
    report_data["target_audienc"] = _get_target_audience(text)
    report_data["revised_presentation"] = _get_revised_presentation(text)
    report_data["translated_presentation"] = _get_translated_presentation(text)
    report_data["is_vulgar"] = _get_is_vulgar(text)
    report_data["sentiment"] = _get_sentiment(text)
    report_data["key_phrase"] = _get_key_phrase(text)

    return report_data
