(function () {
    // API Server URL configuration (defaults to same origin or localhost:8000)
    const API_BASE_URL = window.location.origin.includes('8000') 
        ? window.location.origin 
        : 'http://127.0.0.1:8000';

    // Inject Chat Widget Markup into Host Website DOM
    const widgetHTML = `
        <div id="verano-chat-bubble" title="Ask Verano Knowledge Assistant">
            <svg viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.2L4 17.2V4h16v12z"/>
            </svg>
        </div>

        <div id="verano-chat-drawer">
            <div class="chat-drawer-header">
                <div class="title-area">
                    <h3>Verano Knowledge Assistant</h3>
                    <span>Dual-Engine RAG & SQL Agent</span>
                </div>
                <button class="close-btn" id="verano-close-btn">&times;</button>
            </div>

            <div class="chat-messages" id="verano-message-container">
                <div class="message-bubble assistant-message">
                    👋 Hello! I am the Verano Apparel Knowledge Assistant. Ask me about HR policies, sales statistics, or inventory!
                </div>
            </div>

            <form class="chat-input-area" id="verano-chat-form">
                <input type="text" id="verano-chat-input" placeholder="Ask a question..." autocomplete="off" required />
                <button type="submit">Send</button>
            </form>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', widgetHTML);

    const bubble = document.getElementById('verano-chat-bubble');
    const drawer = document.getElementById('verano-chat-drawer');
    const closeBtn = document.getElementById('verano-close-btn');
    const form = document.getElementById('verano-chat-form');
    const input = document.getElementById('verano-chat-input');
    const messageContainer = document.getElementById('verano-message-container');

    // Toggle Drawer Open / Close
    bubble.addEventListener('click', () => drawer.classList.add('open'));
    closeBtn.addEventListener('click', () => drawer.classList.remove('open'));

    // Handle Question Submission & SSE Token Streaming
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;

        // 1. Append User Message
        appendMessage(question, 'user-message');
        input.value = '';

        // 2. Append Empty Assistant Message Bubble for Live Token Streaming
        const assistantBubble = appendMessage('', 'assistant-message');
        
        let routeBadgeCreated = false;
        let routeBadge = null;

        try {
            // 3. Connect to Production SSE Stream Endpoint
            const response = await fetch(`${API_BASE_URL}/api/chat/stream?question=${encodeURIComponent(question)}`);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            let fullText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const content = line.replace('data: ', '');

                    if (content === '[DONE]') continue;

                    // Handle Route Signal (Tabular SQL vs Prose RAG)
                    if (content.startsWith('[ROUTE:')) {
                        if (!routeBadgeCreated) {
                            routeBadge = document.createElement('div');
                            routeBadge.className = 'route-badge ' + (content.includes('TABULAR') ? 'badge-tabular' : 'badge-prose');
                            routeBadge.innerText = content.includes('TABULAR') ? '⚡ SQL Engine' : '📄 Hybrid RAG';
                            assistantBubble.prepend(routeBadge);
                            routeBadgeCreated = true;
                        }
                        continue;
                    }

                    // Unescape newlines and append token live
                    const token = content.replace(/\\n/g, '\n');
                    fullText += token;
                    
                    // Keep text inside bubble (preserving route badge)
                    const textNode = assistantBubble.querySelector('.text-content') || document.createElement('span');
                    textNode.className = 'text-content';
                    textNode.innerText = fullText;
                    
                    if (!assistantBubble.contains(textNode)) {
                        assistantBubble.appendChild(textNode);
                    }

                    // Auto-scroll to bottom of chat
                    messageContainer.scrollTop = messageContainer.scrollHeight;
                }
            }
        } catch (err) {
            console.error("Streaming error:", err);
            assistantBubble.innerText = "Error connecting to server. Is FastAPI server running?";
        }
    });

    function appendMessage(text, className) {
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `message-bubble ${className}`;
        if (text) bubbleDiv.innerText = text;
        messageContainer.appendChild(bubbleDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
        return bubbleDiv;
    }
})();
