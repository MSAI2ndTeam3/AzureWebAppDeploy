import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

load_dotenv()

# Azure Speech 설정
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

def text_to_speech_test(text, language, voice_name, output_file):
    """
    Azure Speech를 사용하여 텍스트를 음성으로 변환하고 파일로 저장합니다.

    Args:
        text: 변환할 텍스트
        language: 언어 코드 (예: "ko-KR", "en-US")
        voice_name: 음성 이름 (예: "ko-KR-SunHiNeural", "en-US-JennyNeural")
        output_file: 저장할 오디오 파일 경로
    """
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = voice_name

    # 파일에 저장하기 위한 오디오 출력 설정
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesis completed. Audio saved to: {output_file}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

if __name__ == "__main__":
    text_to_convert = "안녕하세요. Azure Speech SDK 테스트입니다."
    language_code = "ko-KR"
    voice_name = "ko-KR-SunHiNeural"
    output_file_path = "test_output.wav"

    text_to_speech_test(text_to_convert, language_code, voice_name, output_file_path)

    text_to_convert_en = "Hello, this is an Azure Speech SDK test."
    language_code_en = "en-US"
    voice_name_en = "en-US-JennyNeural"
    output_file_path_en = "test_output_en.wav"
    
    text_to_speech_test(text_to_convert_en, language_code_en, voice_name_en, output_file_path_en)