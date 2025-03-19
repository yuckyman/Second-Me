from typing import Dict, List, Optional, Union
import logging

from openai import OpenAI

from lpm_kernel.L1.bio import Bio, Chat, Note, Todo, UserInfo
from lpm_kernel.L1.prompt import PREFER_LANGUAGE_SYSTEM_PROMPT, STATUS_BIO_SYSTEM_PROMPT
from lpm_kernel.L1.utils import get_cur_time, is_valid_chat, is_valid_note, is_valid_todo
from lpm_kernel.api.services.user_llm_config_service import UserLLMConfigService
from lpm_kernel.configs.config import Config


class StatusBioGenerator:
    def __init__(self):
        self.preferred_language = "English"
        self.model_params = {
            "temperature": 0,
            "max_tokens": 1000,
            "top_p": 0,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "seed": 42,
        }
        self.user_llm_config_service = UserLLMConfigService()
        self.user_llm_config = self.user_llm_config_service.get_available_llm()
        if self.user_llm_config is None:
            self.client = None
            self.model_name = None
        else:
            self.client = OpenAI(
                api_key=self.user_llm_config.chat_api_key,
                base_url=self.user_llm_config.chat_endpoint,
                timeout=45.0,  # Set global timeout
            )
            self.model_name = self.user_llm_config.chat_model_name


    def _build_message(self, user_info: UserInfo, language: str) -> List[Dict[str, str]]:
        """Build message list for generating status biography.

        Args:
            user_info: User information object.
            language: Preferred language.

        Returns:
            List of messages formatted for LLM API.
        """
        messages = [
            {"role": "system", "content": STATUS_BIO_SYSTEM_PROMPT},
            {"role": "user", "content": str(user_info)},
        ]

        if language:
            messages.append(
                {
                    "role": "system",
                    "content": PREFER_LANGUAGE_SYSTEM_PROMPT.format(language=language),
                }
            )

        return messages


    def generate_status_bio(self, notes: List[Note], todos: List[Todo], 
                           chats: List[Chat]) -> Bio:
        """Generate a status biography based on user's notes, todos, and chats.

        Args:
            notes: List of user's notes.
            todos: List of user's todos.
            chats: List of user's chats.

        Returns:
            Bio object containing generated content.
        """
        cur_time = get_cur_time()

        user_info = UserInfo(cur_time, notes, todos, chats)
        messages = self._build_message(user_info, self.preferred_language)

        answer = self.client.chat.completions.create(
            model=self.model_name, messages=messages, **self.model_params
        )
        content = answer.choices[0].message.content
        logging.info(f"Generated content: {content}")

        # Create and return Bio object, ensuring all content fields have values
        return Bio(
            contentThirdView=content,  # Put generated content in third_view
            content=content,  # Put generated content in second_view
            summaryThirdView=content,  # Put generated content in third_view
            summary=content,  # Put generated content in second_view
            attributeList=[],
            shadesList=[],
        )
