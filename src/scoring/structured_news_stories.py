import logging
import spacy
import pandas as pd

from typing import List, Dict
from spacy.matcher import PhraseMatcher

from src.news_story import NewsStory
from src.utils.pandas import convert_list_of_dict_to_dataframe

logger = logging.getLogger(__name__)


class StructuredNewsStories():
    def __init__(self, list_news_stories: List[NewsStory]):
        news_stories_keys = NewsStory.__annotations__.keys()
        self.df_news_stories: pd.DataFrame = convert_list_of_dict_to_dataframe(
            list_news_stories, news_stories_keys
        )
        self._tmp_col = "metadata_txt"
        self.nlp = spacy.load("en_core_web_sm")
    
    def add_all_metadata_and_score(self, all_target_fields: Dict[str, Dict[str, List[str]]]) -> None:
        self.add_all_metadata(all_target_fields=all_target_fields)
        self.calculate_score()
    
    def add_all_metadata(self, all_target_fields: Dict[str, Dict[str, List[str]]]) -> None:
        self.scor_col = []
        self._create_tmp_col()
        for category, target_fields in all_target_fields.items():
            self.add_metadata(category=category, target_fields=target_fields)
            self.scor_col.append(category)
        self._delete_tmp_col()

    def add_metadata(self, category: str, target_fields: Dict[str, List[str]]) -> None:
        all_tags = []
        for tag, terms in target_fields.items():
            patterns = [self.nlp.make_doc(text) for text in terms]
            matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            matcher.add("TerminologyList", patterns)
            all_tags.append(self.df_news_stories[self._tmp_col].apply(lambda x: tag * bool(len(matcher(self.nlp(x))))))
        self.df_news_stories[category] = pd.Series(list(zip(*all_tags))).apply(lambda x: [item for item in x if item])

    def _create_tmp_col(self):
        tmp_series = self.df_news_stories["title"] + ". " + self.df_news_stories["news_summary"] + ". " + self.df_news_stories["text"]
        self.df_news_stories[self._tmp_col] = tmp_series.apply(lambda x: self._preprocessing(x))
    
    def _delete_tmp_col(self):
        self.df_news_stories.drop(columns=self._tmp_col, inplace=True)

    # TODO: Investigate whether I need to handle the case of plurals. Probably, yes. Maybe not a top priority
    def _preprocessing(self, text: str) -> spacy.tokens.doc.Doc:
        # remove extra spaces and separators
        text_split = ' '.join(text.split())
        return text_split
        """
        # lemmatize to handle plurals
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_split)
        lemmas = [token.lemma_ for token in doc]
        # re-build document
        lemmas_text = " ".join(lemmas)
        new_doc = nlp(lemmas_text)
        return new_doc
        """
    
    def calculate_score(self):
        score = 0
        for col in self.scor_col:
            score += self.df_news_stories[col].apply(lambda x: len(x))
        self.df_news_stories["score"] = score

