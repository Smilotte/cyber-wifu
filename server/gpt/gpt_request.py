import openai

# gpt3 stop character
start_sequence = "\n木槿："
restart_sequence = "\n我："


def friend_chat(text):
    openai.api_key = "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"
    prompt = text
    if text == 'quit':
        return
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[start_sequence, restart_sequence]
    )
    reply = response.choices[0].text
    return reply
