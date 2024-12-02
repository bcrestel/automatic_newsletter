from typing import TypedDict


class NewsStory(TypedDict):
    title: str # title of that news story
    url: str # link to the news story
    news_provider: str # where that news story was found
    source_of_the_news: str #
    news_summary: str