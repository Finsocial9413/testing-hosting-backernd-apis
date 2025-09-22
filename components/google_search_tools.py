from agno.tools.duckdb import DuckDbTools
from agno.tools.python import PythonTools
from agno.tools.youtube import YouTubeTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.pubmed import PubmedTools
from agno.tools.jina import JinaReaderTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
# Initialize Searxng with your Searxng instance URL

def get_google_Search_tools(google_search:str):
    return  [DuckDuckGoTools(),GoogleSearchTools()
             ,DuckDbTools(), PythonTools(cache_results=True),
                       YouTubeTools(cache_results=True), Crawl4aiTools(max_length=None),
                       PubmedTools(cache_results=True), WikipediaTools(cache_results=True),
                       JinaReaderTools(cache_results=True), Newspaper4kTools(cache_results=True),
                       YFinanceTools(stock_price=True, analyst_recommendations=True,
                                   company_info=True, company_news=True, cache_results=True)]
    
    
    