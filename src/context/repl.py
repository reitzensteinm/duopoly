def repl():
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ("exit", "quit"):
            break
        print(user_input)
