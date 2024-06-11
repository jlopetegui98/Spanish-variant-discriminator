import emoji
import re

class TweetsPreprocessor():
    def __init__(self, lang='es'):
        self.lang = lang
        self.user_token = "@usuario"
        self.url_token = "url"
        self.hashtags_camelize = True
        self.emojis_to_text = True
        self.remove_multiple_end_lines = True
        self.normalize_laughing = True
        self.normalize_letter_repetitions = True


    def _replace_user_mentions(self, tweet):
        """
        Replace user mentions with a special token
        input: tweet (str)
        output: tweet (str) after replacing user mentions
        """
        return re.sub(r'@\w{0,15}', self.user_token, tweet)
    
    def _replace_urls(self, tweet):
        """
        Replace urls with a special token
        input: tweet (str)
        output: tweet (str) after replacing urls
        """
        return re.sub(r'http\S+', self.url_token, tweet)

    def _process_hashtag(self, hashtag):
        """
        Process a hashtag
        input: hashtag (str)
        output: hashtag (str) after processing
        """
        if self.hashtags_camelize:
            start_of_camel = re.compile(r'([A-Z]+)')
            hashtag = start_of_camel.sub(r' \1', hashtag).strip().lower()
        return hashtag
    def _replace_hashtags(self,tweet):
        """
        Change hashtags (expected to be in camel case) to lowercase separated by spaces
        input: tweet (str)
        output: tweet (str) after replacing hashtags
        """
        if self.hashtags_camelize:
            hashtag_regex = re.compile(r'#([A-Za-z0-9]+)')
            tweet = hashtag_regex.sub(lambda x: self._process_hashtag(x.groups()[0]), tweet)
        return tweet
        
    def _replace_emojis(self, tweet, emoji_wrapper="emoji"):
        """
        Replace emojis with text
        input: tweet (str)
        output: tweet (str) after replacing emojis
        """
        tweet = emoji.demojize(tweet, language='es', delimiters=("|", "|"))
        if self.emojis_to_text:
            emoji_regex = re.compile(r"\|([^\|]+)\|")
            wrapper = f" {emoji_wrapper} ".replace("  ", " ")
            tweet = emoji_regex.sub(
                lambda x: wrapper + " ".join(x.groups()[0].split("_")) + wrapper,
                tweet
            )
        return tweet

    def _normalize_laughing(self, tweet):
        """
        Normalize laughing expressions
        input: tweet (str)
        output: tweet (str) after normalizing laughing expressions
        """
        if self.normalize_laughing:
            laughter_regex = re.compile("[JAEIjaei][JAEIjaei][JAEIjaei][JAEIjaei]+[A-Za-z]+[JAEIjaei]+")
            tweet = laughter_regex.sub("jaja", tweet)
            laughter_regex = re.compile("[HAha][HAha][HAha][HAha]+[A-Za-z]+[HAha]+")
            tweet = laughter_regex.sub("haha", tweet)
            laughter_regex = re.compile("[GEge][GEge][GEge][GEge]+[A-Za-z]+[GEge]+")
            tweet = laughter_regex.sub("gege", tweet)
        return tweet

    def _normalize_letter_repetitions(self, tweet):
        """
        Normalize letter repetitions. Keeping up to two repetitions
        input: tweet (str)
        output: tweet (str) after normalizing letter repetitions
        """
        if self.normalize_letter_repetitions:
            tweet = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', tweet)
        return tweet
    
    def _replace_multiple_spaces(self, tweet):
        """
        Replace multiple spaces with a single space
        input: tweet (str)
        output: tweet (str) after replacing multiple spaces
        """
        # remove spaces at the beginning and end of the tweet
        tweet = tweet.strip()
        return re.sub(r'\s+', ' ', tweet)

    def _replace_end_lines(self,tweet):
        """
        Replace multiple end lines with a point.
        input: tweet (str)
        output: tweet (str) after replacing multiple end lines
        """
        if self.remove_multiple_end_lines:
            return re.sub(r'\n+', '. ', tweet)
        else:
            return tweet

    def preprocess(self, tweet):
        """
        Preprocess a tweet
        input: tweet (str)
        output: tweet (str) after preprocessing
        """
        tweet = self._replace_user_mentions(tweet)
        tweet = self._replace_urls(tweet)
        tweet = self._replace_hashtags(tweet)
        tweet = self._replace_emojis(tweet)
        tweet = self._normalize_laughing(tweet)
        tweet = self._normalize_letter_repetitions(tweet)
        tweet = self._replace_end_lines(tweet)
        tweet = self._replace_multiple_spaces(tweet)
        return tweet
    
