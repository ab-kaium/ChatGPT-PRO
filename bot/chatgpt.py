import config

import openai
openai.api_key = config.openai_api_key


CHAT_MODES = {
    "assistant": {
        "name": "👩🏼‍🎓 Assistant",
        "welcome_message": "👩🏼‍🎓 Hi, I'm <b>ChatGPT assistant</b>. How can I help you?",
        "prompt_start": "As an advanced chatbot named ChatGPT, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user."
    },

    "code_assistant": {
        "name": "👩🏼‍💻 Code Assistant",
        "welcome_message": "👩🏼‍💻 Hi, I'm <b>ChatGPT code assistant</b>. How can I help you?",
        "prompt_start": "As an advanced chatbot named ChatGPT, your primary goal is to assist users to write code. This may involve designing/writing/editing/describing code or providing helpful information. Where possible you should provide code examples to support your points and justify your recommendations or solutions. Make sure the code you provide is correct and can be run without errors. Be detailed and thorough in your responses. Your ultimate goal is to provide a helpful and enjoyable experience for the user. Write code inside <code>, </code> tags."
    },

    "text_improver": {
        "name": "📝 Text Improver",
        "welcome_message": "📝 Hi, I'm <b>ChatGPT text improver</b>. Send me any text – I'll improve it and correct all the mistakes",
        "prompt_start": "As an advanced chatbot named ChatGPT, your primary goal is to correct spelling, fix mistakes and improve text sent by user. Your goal is to edit text, but not to change it's meaning. You can replace simplified A0-level words and sentences with more beautiful and elegant, upper level words and sentences. All your answers strictly follows the structure (keep html tags):\n<b>Edited text:</b>\n{EDITED TEXT}\n\n<b>Correction:</b>\n{NUMBERED LIST OF CORRECTIONS}"
    },

    "text_summery": {
        "name": "Text Summery",
        "welcome_message": "🎬 Hi, I'm <b>ChatGPT Summarize a piece of text in a given length.</b>. How can I help you?",
        "prompt_start": "Summarize a piece of text in a given length. Original text: [What is the text that needs to be summarized?]
Summary length: [Enter the desired length of the summary in words or sentences].
Purpose: [What is the purpose of the summary? E.g. to provide an overview, to highlight key points, etc.]
Writing style and tone: [Choose writing styles and tones you would want]."
    },
    
     "math_teacher": {
        "name": "Math Teacher",
        "welcome_message": "🎬 Hi, I'm <b>ChatGPT Math Expert.</b>. How can I help you?",
        "prompt_start": "I want you to act as a math teacher. I will provide some mathematical equations or concepts, and it will be your job to explain them in easy-to-understand terms. This could include providing step-by-step instructions for solving a problem, demonstrating various techniques with visuals or suggesting online resources for further study. My first request is “I need help understanding how probability works.” Writing style and tone: Friendly, Write in Bengali"
    },
}

OPENAI_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}


class ChatGPT:
    def __init__(self, use_chatgpt_api=True):
        self.use_chatgpt_api = use_chatgpt_api
    
    def send_message(self, message, dialog_messages=[], chat_mode="assistant"):
        if chat_mode not in CHAT_MODES.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            try:
                if self.use_chatgpt_api:
                    messages = self._generate_prompt_messages_for_chatgpt_api(message, dialog_messages, chat_mode)
                    r = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        **OPENAI_COMPLETION_OPTIONS
                    )
                    answer = r.choices[0].message["content"]
                else:
                    prompt = self._generate_prompt(message, dialog_messages, chat_mode)
                    r = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=prompt,
                        **OPENAI_COMPLETION_OPTIONS
                    )
                    answer = r.choices[0].text

                answer = self._postprocess_answer(answer)
                n_used_tokens = r.usage.total_tokens
                
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

        return answer, n_used_tokens, n_first_dialog_messages_removed

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = CHAT_MODES[chat_mode]["prompt_start"]
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            prompt += "Chat:\n"
            for dialog_message in dialog_messages:
                prompt += f"User: {dialog_message['user']}\n"
                prompt += f"ChatGPT: {dialog_message['bot']}\n"

        # current message
        prompt += f"User: {message}\n"
        prompt += "ChatGPT: "

        return prompt

    def _generate_prompt_messages_for_chatgpt_api(self, message, dialog_messages, chat_mode):
        prompt = CHAT_MODES[chat_mode]["prompt_start"]
        
        messages = [{"role": "system", "content": prompt}]
        for dialog_message in dialog_messages:
            messages.append({"role": "user", "content": dialog_message["user"]})
            messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": message})

        return messages

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer
