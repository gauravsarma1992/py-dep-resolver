from io import BytesIO
from tokenize import tokenize, NAME


class Tokenizer:
    def __init__(self, *args, **kwargs):
        self.code: str = kwargs["code"]

    def tokenize(self) -> set[str]:
        tokens = tokenize(BytesIO(self.code.encode('utf-8')).readline)
        token_set = set()
        for toknum, tokval, _, _, _ in tokens:
            if toknum == NAME:
                token_set.add(tokval)

        return token_set
