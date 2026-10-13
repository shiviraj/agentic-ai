from agent.interface.cli.app import user_prompt, prompt_instruction


def main() -> None:
    prompt_instruction()
    while True:
        is_exit, prompt = user_prompt()
        if is_exit:
            print(prompt)
            return
        if not prompt:
            continue
        print("PROMPT:"+prompt)
