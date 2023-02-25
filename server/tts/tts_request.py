import azure.cognitiveservices.speech as speechsdk

speech_key, service_region = "3f264881818945b396f6eb9a27ae8bb8", "japaneast"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set the voice name, refer to https://aka.ms/speech/voices/neural for full list.
speech_config.speech_synthesis_voice_name = "YunyeNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)


def audio(response):
    ssml = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='zh-CN'>" \
           "<voice name = 'zh-CN-XiaomoNeural' >" \
           "<mstts:express-as role='Girl' style='cheerful' styledegree='1'>" \
           + response + \
           "</mstts:express-as>" \
           "</voice>" \
           "</speak>"

    speech_synthesizer.speak_ssml_async(ssml).get()
