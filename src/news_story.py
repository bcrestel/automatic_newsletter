from typing import TypedDict


class NewsStory(TypedDict):
    title: str  # title of that news story
    url: str  # link to the news story
    news_provider: str  # where that news story was found
    source_of_the_news: str  # where you heard about it
    text: str  # content of the news story
    news_summary: str  # a few sentences describing the content
    date_source: str  # date of the source_of_the_news (not the date of the article)
    date_source_time_zone: str
