document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const historyList = document.getElementById('history-list');
    const newChatBtn = document.getElementById('new-chat-btn');

    let sessions = JSON.parse(localStorage.getItem('chat_sessions')) || [];
    let currentSessionId = localStorage.getItem('current_session_id') || null;

    const saveToLocalStorage = () => {
        localStorage.setItem('chat_sessions', JSON.stringify(sessions));
        localStorage.setItem('current_session_id', currentSessionId);
    };

    const renderHistory = () => {
        historyList.innerHTML = '';
        sessions.slice().reverse().forEach(session => {
            const li = document.createElement('li');
            li.textContent = session.title || "Cuộc trò chuyện mới";
            if (session.id === currentSessionId) li.classList.add('active');
            li.onclick = () => switchSession(session.id);
            historyList.appendChild(li);
        });
    };

    const addMessage = (role, content, animate = true) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        if (!animate) messageDiv.style.animation = 'none';
        
        let htmlContent = content.replace(/\n/g, '<br>');
        // Basic list formatting
        htmlContent = htmlContent.replace(/^\* (.*)$/gm, '<li>$1</li>');
        if (htmlContent.includes('<li>')) {
            htmlContent = htmlContent.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${htmlContent}
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const switchSession = (id) => {
        currentSessionId = id;
        const session = sessions.find(s => s.id === id);
        messagesContainer.innerHTML = '';
        
        if (session && session.history.length > 0) {
            session.history.forEach(msg => addMessage(msg.role, msg.content, false));
        } else {
            addMessage('assistant', 'Chào bạn! Mình có thể giúp gì cho bạn hôm nay? 🔥', false);
        }
        
        renderHistory();
        saveToLocalStorage();
    };

    const createNewChat = () => {
        const id = Date.now().toString();
        const newSession = {
            id: id,
            title: "Cuộc trò chuyện mới",
            history: []
        };
        sessions.push(newSession);
        switchSession(id);
    };

    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        if (!currentSessionId) {
            createNewChat();
        }

        const session = sessions.find(s => s.id === currentSessionId);
        
        // Update title if it's the first message
        if (session.history.length === 0) {
            session.title = message.substring(0, 30) + (message.length > 30 ? "..." : "");
        }

        addMessage('user', message);
        userInput.value = '';

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading';
        loadingDiv.innerHTML = '<div class="message-content"><i class="fas fa-circle-notch fa-spin"></i> Đang suy nghĩ...</div>';
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: session.history
                }),
            });

            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            messagesContainer.removeChild(loadingDiv);
            addMessage('assistant', data.answer);
            
            session.history.push({ role: 'user', content: message });
            session.history.push({ role: 'assistant', content: data.answer });
            
            saveToLocalStorage();
            renderHistory();

        } catch (error) {
            console.error('Error:', error);
            if (loadingDiv.parentNode) messagesContainer.removeChild(loadingDiv);
            addMessage('assistant', 'Xin lỗi, đã có lỗi xảy ra hoặc máy chủ đang gặp sự cố. 🛑');
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    newChatBtn.addEventListener('click', createNewChat);

    // Initial Load
    if (sessions.length > 0 && currentSessionId) {
        switchSession(currentSessionId);
    } else if (sessions.length > 0) {
        switchSession(sessions[sessions.length - 1].id);
    } else {
        createNewChat();
    }
});
