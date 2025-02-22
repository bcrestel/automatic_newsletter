from typing import List, Union

from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from src.genai_model.genai_model import GenAIModel


class Summarizer:
    def __init__(
        self, parameters={"temperature": 0.2, "top_p": 0.5}, model_type: str = "large"
    ):
        system_prompt = self._generate_system_prompt()
        self.summarizer = GenAIModel(model_type=model_type, system_promt=system_prompt)
        self.parameters = parameters

    #    @staticmethod
    #    def format_news_stories(bullet_list_news_stories: str) -> List[str]:
    #        txt_split = bullet_list_news_stories.split("\u2022")
    #        list_formatted_news_stories = []
    #        for txt in txt_split[1:]:
    #            txt_split2 = txt.split("Summary:")
    #            text = txt_split2[-1]
    #            title = txt_split2[0].split("(http")[0]
    #            title = title.replace("\n", " ")
    #            list_formatted_news_stories.append(f"{title}: {text}")
    #        return list_formatted_news_stories

    def summarize(
        self, list_news_stories: str
    ) -> Union[ModelResponse, CustomStreamWrapper]:
        user_prompt = self._generate_user_prompt(list_news_stories)
        response = self.summarizer.completion(
            user_prompt=user_prompt, parameters=self.parameters
        )
        return response

    def summarize_str(self, list_news_stories: str) -> str:
        return self.get_content_from_response(self.summarize(list_news_stories))

    def get_content_from_response(
        self, response: Union[ModelResponse, CustomStreamWrapper]
    ) -> str:
        return self.summarizer.get_content_from_response(response)

    def _generate_system_prompt(self) -> str:
        return """
You are an expert technical writer, specialized in the field of Artificial Intelligence.
Your speciality is to summarize multiple news articles into professional news digests.
You audience consists of senior business leaders who are interested in 
1. understanding the technological trends in AI, 
2. monitoring the fundraising activities in the ecosystem, and 
3. tracking the main AI companies.
        """

    def _generate_user_prompt(self, news_stories: str) -> str:
        return f"""
I will provide you with a list of news articles, and I want you to summarize all those articles into a single paragraph. Here are a few additional requirements:
- The summary should be as short as possible.
- The core content of all the news stories should be contained in the summary. 
- If several news stories contain similar or identical material, this should not be repeated in the summary.

To produce the summaries, I want you to follow these steps:
1. Organize the news articles into a small number of categories.
2. For each category, summarize all news articles of that category into a concise paragraph.
3. Combine the summaries of all categories together.

You must only return the output from step 3, not the intermediate steps (steps 1 and 2).
You must only return the summary, don't start with any introductory sentence.

Each news article follows the same format:
<TITLE> : <MAIN TEXT>
Here is the list of news articles that I want you to use to create your newsletter:
{news_stories}
        """


class SummarizerCompIntel(Summarizer):
    def __init__(
        self, parameters={"temperature": 0.2, "top_p": 0.5}, model_type: str = "large"
    ):
        super().__init__(parameters=parameters, model_type=model_type)

    def _generate_system_prompt(self) -> str:
        return """
You are an expert technical writer, specialized in competitive intelligence in the financial services industry.
Your speciality is to summarize multiple news articles into professional news digests.
You audience consists of senior leaders from a large Financial Services company who are interested in monitoring the activity of their competitors, with a particular emphasis on
1. how their competitors use Artificial Intelligence (AI) for their own business,
2. how their competitors invest in Technology and AI,
3. what deals large investment banks are working on in Technology and AI
        """

    def _generate_user_prompt(self, news_stories: str) -> str:
        return f"""
I will provide you with a list of news articles that all relate to a single large Bank, and I want you to summarize all those articles into a single paragraph. Here are a few additional requirements:
- The summary should be as short as possible.
- The core content of all the news stories should be contained in the summary. 
- If several news stories contain similar or identical material, this should not be repeated in the summary.

To produce the summaries, I want you to follow these steps:
1. Organize the news articles into a small number of categories.
2. For each category, summarize all news articles of that category into a concise paragraph.
3. Combine the summaries of all categories together.

You must only return the output from step 3, not the intermediate steps (steps 1 and 2).
You must only return the summary, don't start with any introductory sentence.

Each news article follows the same format:
<TITLE> : <MAIN TEXT>
Here is the list of news articles that I want you to use to create your newsletter:
{news_stories}
        """


class SummarizerMarketIntel(Summarizer):
    def __init__(
        self, parameters={"temperature": 0.2, "top_p": 0.5}, model_type: str = "large"
    ):
        super().__init__(parameters=parameters, model_type=model_type)

    def _generate_system_prompt(self) -> str:
        return """
You are an expert technical writer, specialized in market intelligence in the field of Artificial Intelligence.
Your speciality is to read multiple articles related to a specific technology company and summarize them into a professional news digest.
You audience consists of senior business leaders who are interested in 
1. understanding the technological trends in AI, 
2. monitoring the fundraising activities in the ecosystem, and 
3. tracking the main AI companies.
        """

    def _generate_user_prompt(self, news_stories: str) -> str:
        return f"""
I will provide you with a list of news articles related to a single technology company, and I want you to summarize all those articles into a single paragraph. Here are a few additional requirements:
- The summary should be as short as possible.
- The core content of all the news stories should be contained in the summary. 
- If several news stories contain similar or identical material, this should not be repeated in the summary.

To produce the summaries, I want you to follow these steps:
1. Organize the news articles into a small number of categories.
2. For each category, summarize all news articles of that category into a concise paragraph.
3. Combine the summaries of all categories together.

You must only return the output from step 3, not the intermediate steps (steps 1 and 2).
You must only return the summary, don't start with any introductory sentence.

Each news article follows the same format:
<TITLE> : <MAIN TEXT>
Here is the list of news articles that I want you to use to create your newsletter:
{news_stories}
        """
