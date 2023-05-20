import os
import openai


def gpt_query(message: str) -> str:
    """Queries GPT-4 with a given message."""
    openai.api_key = os.environ["OPENAI_API_KEY"]

    completion = openai.ChatCompletion.create(model="gpt-4", messages=[
        {"role": "system", "content": "You are a helpful programming assistant. \
        You will be given code as well as instructions to modify it. \
        Please make ONLY the changes requested, and respond only with code and no extra information or formatting \
        and follow PEP-8 formatting standards. Do not quote the output in markdown."},
        {"role": "user", "content": message}
    ])

    return completion.choices[0].message.content


def read_file(path: str) -> str:
    """Reads and returns the content of a file."""
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def write_file(path: str, contents: str) -> None:
    """Writes the contents to a file."""
    with open(path, 'w', encoding='utf-8') as file:
        file.write(contents)


def main() -> None:
    """Main function to handle program execution."""
    print("What change would you like to make?")
    prompt = input()

    path = "main.py"
    write_file(path, gpt_query(f"{prompt}\n{read_file(path)}"))


if __name__ == '__main__':
    main()