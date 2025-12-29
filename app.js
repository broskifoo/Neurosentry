// [DETECTOR / ASSISTANT] - Frontend JavaScript

// Wait until the HTML page is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    
    // Get references to our HTML elements
    const analyzeButton = document.getElementById('analyzeButton');
    const logInput = document.getElementById('logInput');
    const statusEl = document.getElementById('status');
    const explanationEl = document.getElementById('explanation');
    const audioPlayer = document.getElementById('audioPlayer');

    // This is the URL of our FastAPI server
    const API_URL = 'http://127.0.0.1:8000';

    // Add a "click" event listener to our button
    analyzeButton.addEventListener('click', async () => {
        
        // 1. Get the text from the text box
        const rawLogs = logInput.value;
        if (!rawLogs) {
            alert("Please paste some logs first.");
            return;
        }

        // 2. Convert the text into the JSON format our API needs
        // We split the text by new lines, and for each line, create an object
        // e.g., "file_create" becomes { "action": "file_create" }
        const logEntries = rawLogs.split('\n')
                                  .filter(line => line.trim() !== '') // Remove empty lines
                                  .map(action => ({ "action": action.trim() }));

        const requestBody = {
            "logs": logEntries
        };

        // 3. Show a loading message
        statusEl.textContent = 'Analyzing...';
        explanationEl.textContent = '';
        audioPlayer.src = '';

        try {
            // 4. Send the data to our FastAPI server
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            // 5. Get the JSON response from the server
            const data = await response.json();

            // 6. Update the webpage with the results
            statusEl.textContent = data.is_threat ? 'Threat Detected!' : 'No Threat Detected.';
            statusEl.style.color = data.is_threat ? 'red' : 'green';
            explanationEl.textContent = data.explanation;

            // 7. Load and play the audio
            if (data.audio_url) {
                // We must use the full URL to the audio file
                audioPlayer.src = `${API_URL}${data.audio_url}`;
                audioPlayer.play();
            }

        } catch (error) {
            console.error('Error during analysis:', error);
            statusEl.textContent = 'Error during analysis.';
            statusEl.style.color = 'red';
            explanationEl.textContent = error.message;
        }
    });
});