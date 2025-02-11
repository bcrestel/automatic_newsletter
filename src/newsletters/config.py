from pathlib import Path

from src.newsletters.parser.alpha_signal import alpha_signal_parser
from src.newsletters.parser.bloomberg_tech import bloomberg_tech_parser
from src.newsletters.parser.tldr import tldr_parser

NEWSLETTER_AND_PARSER = {
    "TLDR AI <dan@tldrnewsletter.com>": tldr_parser,
    "AlphaSignal <news@alphasignal.ai>": alpha_signal_parser,
    "TLDR <dan@tldrnewsletter.com>": tldr_parser,
    "TLDR Product <dan@tldrnewsletter.com>": tldr_parser,
    "Bloomberg Technology <noreply@news.bloomberg.com>": bloomberg_tech_parser,
}
