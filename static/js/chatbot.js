// 챗봇 UI 컨트롤러
class ChatbotUI {
    constructor() {
        this.toggleBtn = document.getElementById('chatbot-toggle-btn');
        this.closeBtn = document.getElementById('chatbot-close-btn');
        this.panel = document.getElementById('chatbot-panel');
        this.messagesContainer = document.getElementById('chatbot-messages');
        this.input = document.getElementById('chatbot-input');
        this.sendBtn = document.getElementById('chatbot-send-btn');
        this.loading = document.getElementById('chatbot-loading');
        
        this.isOpen = false;
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        // 이벤트 리스너 등록
        this.toggleBtn.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.close());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter 키로 전송 (Shift+Enter는 줄바꿈)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 자동 높이 조절
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = this.input.scrollHeight + 'px';
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.panel.classList.add('open');
        this.toggleBtn.classList.add('hidden');
        this.isOpen = true;
        this.input.focus();
    }
    
    close() {
        this.panel.classList.remove('open');
        this.toggleBtn.classList.remove('hidden');
        this.isOpen = false;
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }
        
        // 사용자 메시지 추가
        this.addMessage(message, 'user');
        
        // 입력창 초기화
        this.input.value = '';
        this.input.style.height = 'auto';
        
        // 처리 중 상태
        this.isProcessing = true;
        this.sendBtn.disabled = true;
        this.showLoading();
        
        try {
            // API 호출
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error('API 요청 실패');
            }
            
            const data = await response.json();
            
            // 봇 응답 추가
            this.addMessage(data.answer, 'bot', data.sources);
            
        } catch (error) {
            console.error('오류:', error);
            this.addMessage(
                '죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
                'bot'
            );
        } finally {
            // 처리 완료
            this.isProcessing = false;
            this.sendBtn.disabled = false;
            this.hideLoading();
        }
    }
    
    addMessage(content, type, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? 'You' : 'AI';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // 메시지 내용을 줄바꿈 유지하며 추가
        const paragraphs = content.split('\n').filter(p => p.trim());
        paragraphs.forEach(para => {
            const p = document.createElement('p');
            p.textContent = para;
            contentDiv.appendChild(p);
        });
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        // 출처 정보 추가 (있는 경우)
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('details');
            sourcesDiv.className = 'message-sources';
            
            const summary = document.createElement('summary');
            summary.textContent = `참고 정보 (${sources.length}개)`;
            sourcesDiv.appendChild(summary);
            
            sources.forEach((source, index) => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.textContent = `${index + 1}. ${source.content}`;
                sourcesDiv.appendChild(sourceItem);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
        
        this.messagesContainer.appendChild(messageDiv);
        
        // 스크롤을 최하단으로
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    showLoading() {
        this.loading.style.display = 'block';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
}

// 전역 함수: 예시 질문 클릭 시 챗봇 열고 질문 전송
function askQuestion(question) {
    if (!window.chatbot) {
        return;
    }
    
    // 챗봇 열기
    if (!window.chatbot.isOpen) {
        window.chatbot.open();
    }
    
    // 입력창에 질문 설정 후 전송
    window.chatbot.input.value = question;
    setTimeout(() => {
        window.chatbot.sendMessage();
    }, 300);
}

// 페이지 로드 시 챗봇 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotUI();
    console.log('[완료] 챗봇 UI 초기화 완료');
});

