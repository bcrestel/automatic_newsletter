import logging
from typing import Dict, List

import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher

from src.news_story import NewsStory
from src.scoring.config import SPREADSHEET_TABS_TO_ATTR
from src.utils.pandas import convert_list_of_dict_to_dataframe

logger = logging.getLogger(__name__)


class StructuredNewsStories:
    def __init__(self, list_news_stories: List[NewsStory]):
        news_stories_keys = NewsStory.__annotations__.keys()
        self.df_news_stories: pd.DataFrame = convert_list_of_dict_to_dataframe(
            list_news_stories, news_stories_keys
        )
        self._tmp_col = "metadata_txt"
        self.nlp = spacy.load("en_core_web_sm")

    def add_all_metadata_and_score(
        self, all_target_fields: Dict[str, Dict[str, List[str]]]
    ) -> None:
        self.add_all_metadata(all_target_fields=all_target_fields)
        self.calculate_score()

    def add_all_metadata(
        self, all_target_fields: Dict[str, Dict[str, List[str]]]
    ) -> None:
        self.score_col = []
        self._create_tmp_col()
        for category, target_fields in all_target_fields.items():
            self.add_metadata(category=category, target_fields=target_fields)
            self.score_col.append(category)
        self._delete_tmp_col()

    def add_metadata(self, category: str, target_fields: Dict[str, List[str]]) -> None:
        all_tags = []
        for tag, terms in target_fields.items():
            patterns = [self.nlp.make_doc(text) for text in terms]
            matcher = PhraseMatcher(
                self.nlp.vocab, attr=SPREADSHEET_TABS_TO_ATTR[category]
            )
            matcher.add("TerminologyList", patterns)
            all_tags.append(
                self.df_news_stories[self._tmp_col].apply(
                    lambda x: tag * bool(len(matcher(self.nlp(x))))
                )
            )
        self.df_news_stories[category] = pd.Series(list(zip(*all_tags))).apply(
            lambda x: [item for item in x if item]
        )

    def _create_tmp_col(self):
        tmp_series = (
            self.df_news_stories["title"]
            + ". "
            + self.df_news_stories["news_summary"]
            + ". "
            + self.df_news_stories["text"]
        )
        self.df_news_stories[self._tmp_col] = tmp_series.apply(
            lambda x: self._preprocessing(x)
        )

    def _delete_tmp_col(self):
        self.df_news_stories.drop(columns=self._tmp_col, inplace=True)

    def _preprocessing(self, text: str) -> spacy.tokens.doc.Doc:
        # remove extra spaces and separators
        text_split = " ".join(text.split())
        return text_split

    def calculate_score(self):
        score = 0
        for col in self.score_col:
            score += self.df_news_stories[col].apply(lambda x: len(x))
        self.df_news_stories["score"] = score
