import openai


class GPT:
    tokens = 1024
    temperature = 0.7
    n = 1

    def __init__(self, config):
        self.config = config
        openai.api_key = config["openai"]["openai_key"]
        self.tokens = config["openai"]["tokens"]
        self.temperature = config["openai"]["temperature"]
        self.n = config["openai"]["n"]

    def prompt(self, text):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            max_tokens=self.tokens,
            n=self.n,
            stop=None,
            temperature=self.temperature,
        )

        return response["choices"][0]["text"].strip()

    def question_formatted(self, text):
        prompt = (
            "Use markdown. Dont provide links or urls. All code should be in code blocks and come with explanations. In a detailed and well formatted message respond to this: %s"
            % text
        )
        return self.prompt(prompt)

    def question(self, text):
        prompt = (
            "Do not use any formatting or single or double quotes, links, code, or anything that cannot be spoken out loud. In a detailed and well formatted message respond to this: %s"
            % text
        )
        return self.prompt(prompt)

    def get_language(self, text):
        prompt = "In a single word, the following text is in what language: %s" % text
        return self.prompt(prompt)

    def translate(self, lang, text):
        prompt = "Translate the following text into %s: %s" % (lang, text)
        return self.prompt(prompt)

    def is_offensive(self, text):
        prompt = (
            "In one word, yes or no, all lowercase, tell me if the following text offensive or even remotely inappropriate: %s"
            % text
        )
        res = self.prompt(prompt)
        return res == "yes"
