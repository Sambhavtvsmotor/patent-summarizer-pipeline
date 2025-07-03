import nltk

# Ensure NLTK 'punkt' and 'punkt_tab' are downloaded before running the summarizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Currently we are having the text here but we will load the text from the excel file 
original_text = 'The present subject matter also provides a method for starting a power unit (125, 425) of a vehicle (100). The method includes the steps of initially enabling cranking of the power unit (125, 425) through a starter means (125E) at a first speed. Then checking for at least a first parameter of the power unit (125, 425). Subsequently, depending on the first parameter enabling cranking of the power unit (125, 425) at a second speed. The second speed is greater than the first speed. The method improves startability and also reduces power consumption of power source (205) driving the starter means (125E).'

# Initializing the parser
my_parser = PlaintextParser(original_text, Tokenizer("english"))

lex_rank_summarizer = LexRankSummarizer()
lexrank_summary = lex_rank_summarizer(my_parser.document, sentences_count=5)

for sentence in lexrank_summary:
    print(sentence)