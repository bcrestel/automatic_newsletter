import logging
from typing import List

import pandas as pd
import spacy
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from src.genai_model.genai_model import GenAIModel

logger = logging.getLogger(__name__)


class ProductionEditor:
    def __init__(
        self, parameters={"temperature": 0.2, "top_p": 0.5}, model_type: str = "medium"
    ):
        system_prompt = self._generate_system_prompt()
        self.annotator = GenAIModel(model_type=model_type, system_promt=system_prompt)
        self.parameters = parameters

    def add_inline_citations(self, full_text: str, df_cite: pd.DataFrame) -> str:
        sentences = self._split_text_to_sentences(full_text=full_text)
        inline_citations = self._find_inline_citations(
            sentences=sentences, df_cite=df_cite
        )
        formatted_sentences = []
        for a, b in zip(sentences, inline_citations):
            try:
                join_a_b = self._join_cite(a, b)
            except Exception as e:
                logger.error(f"a: {a}")
                logger.error(f"b: {b}")
                raise e
            formatted_sentences.append(join_a_b)
        return (" ").join(formatted_sentences)

    def _split_text_to_sentences(self, full_text: str) -> List[str]:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(full_text)
        return [sent.text for sent in doc.sents]

    @staticmethod
    def _join_cite(sent: str, in_cite: List[int]):
        return sent[:-1] + " " + str(in_cite) + sent[-1]

    def _find_inline_citations(
        self, sentences: List[str], df_cite: pd.DataFrame
    ) -> List[List[int]]:
        inline_citations = []
        for sent in sentences:
            _local_cite = []
            for _dd in df_cite.index:
                article_summary = df_cite.loc[_dd, "news_summary"]
                response = self.annotator.completion_str(
                    user_prompt=self._generate_user_prompt(
                        sentence=sent, article_summary=article_summary
                    ),
                    parameters={"temperature": 0.2, "top_p": 0.5},
                )
                if "YES" in response:
                    _local_cite.append(int(df_cite.loc[_dd, "nb_citation"]))
            if len(_local_cite) == 0:
                _local_cite = ""
            inline_citations.append(_local_cite)
        return inline_citations

    def _generate_system_prompt(self) -> str:
        return """
You are an expert technical writer, specialized in the field of Artificial Intelligence.
You are tasked with identifying whether a given article was used to write a sentence taken from a longer text.
You need to be very precise and very careful before giving your answer.
        """

    def _generate_user_prompt(self, sentence: str, article_summary: str) -> str:
        return f"""
I wrote a text using the content of multiple news articles. 
I will provide you with one sentence from that text that I wrote [SENTENCE], and with a summary of one of the articles that I used to write the entire text [ARTICLE_SUMMARY]. 
I want you to tell me whether that specific article was used to write that specific sentence. 
The input will be formatted as follows:
[SENTENCE]: <a single sentence from the text that I wrote>
[ARTICLE SUMMARY]: <the summary of an article that I used to write that text>

You response can only be one of two words: "YES" or "NO". Do not answer anything else.
"YES" means this article was used to write that sentence
"NO" means this article was not used to write that summary.

Below are the actual sentence and article summary that I want you to use:
[SENTENCE]: {sentence}
[ARTICLE SUMMARY]: {article_summary}
        """
