$(document).ready(function () {
    let isGenerating = false; // 대화 생성 중인지 여부

    async function loadVoices(languageSelectId, voiceSelectId) {
        const response = await fetch('/voices');
        const data = await response.json();
        const voices = data.voices;
        const languageSelect = document.getElementById(languageSelectId);
        const voiceSelect = document.getElementById(voiceSelectId);

        voiceSelect.innerHTML = '';
        voices.filter(v => v.locale === languageSelect.value).forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.short_name;
            option.textContent = voice.name + " (" + voice.gender + ")";
            voiceSelect.appendChild(option);
        });
    }

    // 페이지 로드 시 및 언어 변경 시 음성 목록 로드
    loadVoices('persona-a-language', 'persona-a-voice');
    loadVoices('persona-b-language', 'persona-b-voice');
    $('#persona-a-language').change(() => loadVoices('persona-a-language', 'persona-a-voice'));
    $('#persona-b-language').change(() => loadVoices('persona-b-language', 'persona-b-voice'));

    $('#start-conversation').click(async () => {
        // 대화 생성 중일 때는 중복 클릭 방지
        if (isGenerating) {
            return;
        }
        isGenerating = true;

        const personaA = {
            language: $('#persona-a-language').val(),
            gender: $('#persona-a-gender').val(),
            voice: $('#persona-a-voice').val(),
            tone: $('#persona-a-tone').val(),
            manner: $('#persona-a-manner').val()
        };
        const personaB = {
            language: $('#persona-b-language').val(),
            gender: $('#persona-b-gender').val(),
            voice: $('#persona-b-voice').val(),
            tone: $('#persona-b-tone').val(),
            manner: $('#persona-b-manner').val()
        };
        const turns = $('#turns').val();
        const topic = $('#topic').val();
        const mood = $('#mood').val();

        $('#chat-log').empty();

        try {
            const response = await fetch('/converse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    persona_a: personaA,
                    persona_b: personaB,
                    turns: turns,
                    topic: topic,
                    mood: mood
                })
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            data.messages.forEach((message, index) => {
                if (message.role !== 'system') {
                    const speaker = message.name === 'speaker_a' ? 'A' : 'B';
                    const messageClass = speaker === 'A' ? 'message-a' : 'message-b';
                    const audioFile = data.audio_files.find(f => f.speaker === speaker && parseInt(f.file.split('_')[2]) === Math.floor(index / 2));
                    const audioPlayer = audioFile ? `<audio class="audio-player" controls><source src="/${audioFile.file}" type="audio/wav"></audio>` : '';
                    $('#chat-log').append(`<div class="message ${messageClass}">${speaker}: ${message.content} ${audioPlayer}</div>`);
                }
            });

            // 스크롤 최하단으로 이동
            $('.chat-container').scrollTop($('.chat-container')[0].scrollHeight);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the conversation.');
        } finally {
            isGenerating = false; // 대화 생성 완료
        }
    });
});