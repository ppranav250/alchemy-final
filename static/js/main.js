document.getElementById('paper-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const url = document.getElementById('paper-url').value;
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const audioPlayer = document.getElementById('audio-player');
    const videoPromptText = document.getElementById('video-prompt-text');
    const resultTitle = document.getElementById('result-title');

    loadingDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok) {
            resultTitle.textContent = data.message;
            // The backend now returns a relative path, so we prepend the media route
            audioPlayer.src = `/media/${data.audio_path.split('media/')[1]}?t=${new Date().getTime()}`;
            videoPromptText.textContent = data.video_prompt;
            audioPlayer.load();
            resultDiv.style.display = 'block';
        } else {
            document.getElementById('error-message').textContent = data.error + (data.details ? `\n\n${data.details}` : '');
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        document.getElementById('error-message').textContent = 'A network error occurred. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
    }
});
