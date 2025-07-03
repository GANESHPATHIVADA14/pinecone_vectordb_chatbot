// frontend/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    const API_URL = 'http://localhost:8000/chat';

    // Function to add a message to the chat box
    const addMessage = (text, sender) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = text;
        chatBox.appendChild(messageElement);
        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();

        if (!query) return;

        // Display user's message
        addMessage(query, 'user');
        
        // Clear the input field
        userInput.value = '';

        // Display a loading indicator
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'loading-message');
        loadingElement.textContent = 'Bot is thinking...';
        chatBox.appendChild(loadingElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
            });

            // Remove the loading indicator
            chatBox.removeChild(loadingElement);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const botResponse = data.response || 'Sorry, I could not get a response.';

            // Display bot's message
            addMessage(botResponse, 'bot');

        } catch (error) {
            console.error('Error:', error);
            // Ensure loading indicator is removed on error
            if (chatBox.contains(loadingElement)) {
                chatBox.removeChild(loadingElement);
            }
            addMessage('Sorry, something went wrong. Please check the console.', 'bot');
        }
    });
});