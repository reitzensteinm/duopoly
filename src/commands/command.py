class Command:
    name = ""

    def __init__(self):
        pass

    @staticmethod
    def schema():
        return {}

    @staticmethod
    def load_from_json(json_data):
        pass

    def execute(self):
        pass


class Think(Command):
    name = "Think"

    def __init__(self, thought):
        self.thought = thought

    @staticmethod
    def schema():
        return {
            "thought": str,
        }

    @staticmethod
    def load_from_json(json_data):
        return Think(json_data["thought"])

    def execute(self):
        return self.thought


class Verdict(Command):
    name = "Verdict"

    def __init__(self, reasoning, verdict):
        self.reasoning = reasoning
        self.pass_verdict = verdict

    @staticmethod
    def schema():
        return {
            "reasoning": str,
            "pass": bool,
        }

    @staticmethod
    def load_from_json(json_data):
        return Verdict(json_data["reasoning"], json_data["pass"])

    def execute(self):
        return self.reasoning, self.pass_verdict


commands = [Think, Verdict]
