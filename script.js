import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";

// Initialize Lucide Icons
lucide.createIcons();

// State Management
const state = {
    currentChatId: Date.now().toString(),
    messages: [],
    isTyping: false,
    theme: localStorage.getItem('theme') || 'light'
};

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages-container');
const emptyState = document.getElementById('empty-state');
const thinkingIndicator = document.getElementById('thinking-indicator');
const sendBtn = document.getElementById('send-btn');
const chatContainer = document.getElementById('chat-container');
const chatHistoryList = document.getElementById('chat-history-list');
const newChatBtn = document.getElementById('new-chat-btn');
const themeToggle = document.getElementById('theme-toggle');

// Theme Management
function applyTheme() {
    if (state.theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', state.theme);
}

themeToggle.addEventListener('click', () => {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    applyTheme();
    lucide.createIcons();
});

// Initialize theme
applyTheme();

// Chat History Management
function saveChatHistory() {
    const history = JSON.parse(localStorage.getItem('chemgist_history') || '[]');
    const existingIndex = history.findIndex(h => h.id === state.currentChatId);
    const chatTitle = state.messages[0]?.content.substring(0, 30) + '...' || 'New Chat';
    
    const chatData = {
        id: state.currentChatId,
        title: chatTitle,
        timestamp: Date.now(),
        preview: state.messages[state.messages.length - 1]?.content.substring(0, 50) + '...' || 'No messages'
    };

    if (existingIndex >= 0) {
        history[existingIndex] = chatData;
    } else {
        history.unshift(chatData);
    }

    if (history.length > 10) history.pop();
    
    localStorage.setItem('chemgist_history', JSON.stringify(history));
    renderChatHistory();
}

function renderChatHistory() {
    const history = JSON.parse(localStorage.getItem('chemgist_history') || '[]');
    
    if (history.length === 0) {
        chatHistoryList.innerHTML = '<p class="text-xs text-slate-400 dark:text-slate-500 px-2 italic">No chat history yet</p>';
        return;
    }

    chatHistoryList.innerHTML = history.map(chat => `
        <button onclick="loadChat('${chat.id}')" class="w-full text-left p-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors group ${chat.id === state.currentChatId ? 'bg-slate-100 dark:bg-slate-700/50 border-l-2 border-primary' : ''}">
            <div class="flex items-start gap-2">
                <i data-lucide="message-square" class="w-4 h-4 text-slate-400 dark:text-slate-500 mt-0.5 flex-shrink-0"></i>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">${chat.title}</p>
                    <p class="text-xs text-slate-400 dark:text-slate-500 truncate mt-0.5">${chat.preview}</p>
                </div>
            </div>
        </button>
    `).join('');
    
    lucide.createIcons();
}

function loadChat(chatId) {
    if (state.messages.length > 0) saveChatHistory();
    
    state.currentChatId = chatId;
    state.messages = JSON.parse(localStorage.getItem(`chat_${chatId}`) || '[]');
    
    if (state.messages.length > 0) {
        renderAllMessages();
    } else {
        startNewChat();
    }
    
    renderChatHistory();
}

// Text Processing for Chemistry
function formatChemistryText(text) {
    let formatted = text.replace(/([A-Z][a-z]?)(\d+)/g, (match, element, num) => {
        return `${element}<span class="chemistry-sub">${num}</span>`;
    });
    
    formatted = formatted.replace(/\^(-?\d+|[+-])/g, (match, num) => {
        return `<span class="chemistry-sup">${num}</span>`;
    });
    
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    return formatted;
}

// UI Helpers
function scrollToBottom() {
    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
}

function toggleEmptyState() {
    if (state.messages.length === 0) {
        emptyState.classList.remove('hidden');
        messagesContainer.classList.add('hidden');
    } else {
        emptyState.classList.add('hidden');
        messagesContainer.classList.remove('hidden');
    }
}

function setThinking(visible) {
    state.isTyping = visible;
    thinkingIndicator.classList.toggle('hidden', !visible);
    if (visible) scrollToBottom();
}

// Message Rendering
function renderMessage(message, isUser = false) {
    const div = document.createElement('div');
    div.className = `flex gap-4 message-enter ${isUser ? 'flex-row-reverse' : ''}`;
    
    const avatar = isUser 
        ? `<div class="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center text-slate-600 dark:text-slate-300 flex-shrink-0"><i data-lucide="user" class="w-4 h-4"></i></div>`
        : `<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white flex-shrink-0 shadow-md"><i data-lucide="flask-conical" class="w-4 h-4"></i></div>`;
    
    const bubbleClass = isUser
        ? 'bg-primary text-white rounded-2xl rounded-tr-none shadow-md'
        : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-2xl rounded-tl-none shadow-sm';
    
    const content = formatChemistryText(message);
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    div.innerHTML = `
        ${avatar}
        <div class="flex-1 ${isUser ? 'text-right' : ''} max-w-[85%]">
            <div class="${bubbleClass} px-5 py-3.5 inline-block text-left">
                <div class="leading-relaxed text-[15px]">${content}</div>
            </div>
            <div class="text-xs text-slate-400 dark:text-slate-500 mt-1 ${isUser ? 'mr-1' : 'ml-1'}">${time}</div>
        </div>
    `;
    
    messagesContainer.appendChild(div);
    lucide.createIcons();
    scrollToBottom();
}

function renderAllMessages() {
    messagesContainer.innerHTML = '';
    state.messages.forEach(msg => renderMessage(msg.content, msg.role === 'user'));
    toggleEmptyState();
}

// Connected to ChemGist API
async function getChemGistResponse(input) {
    try {
        const client = await Client.connect("JAZL/ChemGist-API");
        const result = await client.predict("/generate_answer", {
            message: input,
        });
        
        if (result && result.data && result.data.length > 0) {
            return result.data[0];
        } else {
            throw new Error("No response generated.");
        }
        
    } catch (error) {
        console.error('API Error:', error);
        return `⚠️ Connection error: ${error.message}.`;
    }
}

// Send Message Handler
async function handleSend(input) {
    if (!input.trim() || state.isTyping) return;
    
    emptyState.classList.add('hidden');
    messagesContainer.classList.remove('hidden');
    
    const userMessage = { role: 'user', content: input, timestamp: Date.now() };
    state.messages.push(userMessage);
    renderMessage(input, true);
    
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;
    
    localStorage.setItem(`chat_${state.currentChatId}`, JSON.stringify(state.messages));
    saveChatHistory();
    
    setThinking(true);
    
    try {
        const response = await getChemGistResponse(input);
        const aiMessage = { role: 'assistant', content: response, timestamp: Date.now() };
        state.messages.push(aiMessage);
        setThinking(false);
        renderMessage(response, false);
        
        localStorage.setItem(`chat_${state.currentChatId}`, JSON.stringify(state.messages));
        saveChatHistory();
    } catch (error) {
        setThinking(false);
        renderMessage("⚠️ Connection error. Please try again.", false);
    }
}

// New Chat Handler
function startNewChat() {
    if (state.messages.length > 0) {
        saveChatHistory();
    }
    
    state.currentChatId = Date.now().toString();
    state.messages = [];
    
    messagesContainer.innerHTML = '';
    toggleEmptyState();
    
    renderChatHistory();
    userInput.focus();
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSend(userInput.value);
});

newChatBtn.addEventListener('click', startNewChat);

userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    sendBtn.disabled = this.value.trim().length === 0;
});

userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (this.value.trim()) handleSend(this.value);
    }
});

function initializeSuggestionCards() {
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const text = card.querySelector('p').textContent;
            handleSend(text);
        });
    });
}

initializeSuggestionCards();

renderChatHistory();
toggleEmptyState();
userInput.focus();

window.loadChat = loadChat;
