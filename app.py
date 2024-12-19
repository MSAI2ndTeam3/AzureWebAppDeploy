from flask import Flask, render_template, request, jsonify, send_file
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import os
import time
import io
from datetime import datetime
import sounddevice as sd
import numpy as np
import queue
import threading
import soundfile as sf
app = Flask(__name__)
load_dotenv()

# Azure OpenAI 설정
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version='2024-08-01-preview',
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

# Azure Speech 설정
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SPEECH_REGION")

def generate_response(messages, persona, topic, mood):
    """
    Azure OpenAI를 사용하여 응답을 생성합니다.

    Args:
        messages: 대화 히스토리 (list of dict)
        persona: 화자의 페르소나 (dict)
        topic: 대화 주제
        mood: 대화 분위기

    Returns:
        생성된 응답 텍스트
    """
    # 시스템 메시지 대신 사용자 메시지에 페르소나 정보를 포함
    persona_prompt = f"You are a helpful assistant. You will act according to the following persona: Language: {persona['language']}, Gender: {persona['gender']}, Tone: {persona['tone']}, Manner: {persona['manner']}. The conversation topic is '{topic}' and the mood is '{mood}'. "
    
    # 메시지 목록에 persona_prompt 추가 (첫 번째 메시지로)
    messages_with_persona = [{"role": "system", "content": persona_prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages_with_persona,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def text_to_speech(text, language, voice_name, output_file):
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
    
def play_audio(file_path):
    """
    오디오 파일을 재생합니다.

    Args:
        file_path: 재생할 오디오 파일 경로
    """
    try:
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")

@app.route('/')
def index():
    """
    메인 페이지를 렌더링합니다.
    """
    return render_template('index.html')

@app.route('/converse', methods=['POST'])
def converse():
    """
    대화를 생성하고 음성으로 변환합니다.

    Args:
        POST 요청 데이터:
            - persona_a: 화자 A의 페르소나 (JSON)
            - persona_b: 화자 B의 페르소나 (JSON)
            - turns: 대화 턴 수
            - topic: 대화 주제
            - mood: 대화 분위기

    Returns:
        JSON 응답:
            - messages: 대화 히스토리
            - audio_files: 생성된 음성 파일 목록 (base64 인코딩)
    """
    data = request.get_json()
    persona_a = data['persona_a']
    persona_b = data['persona_b']
    turns = int(data['turns'])
    topic = data['topic']
    mood = data['mood']

    messages = []
    audio_files = []
    
    audio_dir = "static/audio"
    
    script = []

    for i in range(turns):
        # 화자 A의 응답 생성
        response_a = generate_response(messages, persona_a, topic, mood)
        messages.append({"role": "system", "content": response_a, "name": "speaker_a"})
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        audio_file_path_a = os.path.join(audio_dir, f"speaker_a_{i}_{timestamp}.wav")
        script.append({"speaker": "A", "text": response_a, "file": audio_file_path_a, "language": persona_a['language'], "voice": persona_a['voice']})
        audio_files.append({"speaker": "A", "file": audio_file_path_a})

        # 화자 B의 응답 생성
        response_b = generate_response(messages, persona_b, topic, mood)
        messages.append({"role": "system", "content": response_b, "name": "speaker_b"})
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        audio_file_path_b = os.path.join(audio_dir, f"speaker_b_{i}_{timestamp}.wav")
        script.append({"speaker": "B", "text": response_b, "file": audio_file_path_b, "language": persona_b['language'], "voice": persona_b['voice']})
        audio_files.append({"speaker": "B", "file": audio_file_path_b})

    # 스크립트 기반 오디오 생성 및 재생
    for item in script:
        text_to_speech(item["text"], item["language"], item["voice"], item["file"])
        play_audio(item["file"])

    return jsonify({'messages': messages, 'audio_files': audio_files})

@app.route('/audio/<filename>')
def audio(filename):
    """
    음성 파일을 제공합니다.
    """
    return send_file(os.path.join("static/audio", filename), mimetype="audio/wav")

@app.route('/voices', methods=['GET'])
def get_voices():
    """
    사용 가능한 음성 목록을 반환합니다.
    """
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    voices_result = synthesizer.get_voices_async().get()

    voices = []
    for voice in voices_result.voices:
        voices.append({
            'name': voice.name,
            'short_name': voice.short_name,
            'gender': str(voice.gender),
            'locale': voice.locale
        })

    return jsonify({'voices': voices})

if __name__ == '__main__':
    app.run(debug=True)