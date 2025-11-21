/**
 * cafe24 MySQL RAG 챗봇 위젯
 * 
 * 사용법:
 * <script src="http://localhost:8080/static/js/chatbot-widget.js"></script>
 */

(function() {
    'use strict';
    
    // 설정
    const CONFIG = {
        apiUrl: 'http://localhost:8080',
        chatApiEndpoint: '/api/chat',
        cssPath: '/static/css/chatbot-widget.css'
    };
    
    // CSS 로드
    function loadCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = CONFIG.apiUrl + CONFIG.cssPath;
        document.head.appendChild(link);
    }
    
    // HTML 생성
    function createChatbotHTML() {
        const html = `
            <!-- 챗봇 버튼 (오른쪽 하단) -->
            <button id="chatbot-toggle-btn" class="chatbot-toggle" aria-label="채팅 시작">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            </button>
            
            <!-- 사이드 톡 패널 -->
            <div id="chatbot-panel" class="chatbot-panel">
                <!-- 헤더 -->
                <div class="chatbot-header">
                    <div class="chatbot-header-content">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <h3>AI 상담사</h3>
                    </div>
                    <button id="chatbot-close-btn" class="chatbot-close" aria-label="닫기">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                
                <!-- 메시지 영역 -->
                <div id="chatbot-messages" class="chatbot-messages">
                    <div class="message bot-message">
                        <div class="message-avatar">AI</div>
                        <div class="message-content">
                            <p>안녕하세요! 무엇을 도와드릴까요? 😊</p>
                        </div>
                    </div>
                </div>
                
                <!-- 로딩 표시 -->
                <div id="chatbot-loading" class="chatbot-loading" style="display: none;">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                
                <!-- 입력 영역 -->
                <div class="chatbot-input-area">
                    <textarea 
                        id="chatbot-input" 
                        class="chatbot-input" 
                        placeholder="메시지를 입력해주세요..."
                        rows="1"
                    ></textarea>
                    <button id="chatbot-send-btn" class="chatbot-send-btn" aria-label="전송">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        const container = document.createElement('div');
        container.id = 'chatbot-widget-container';
        container.innerHTML = html;
        document.body.appendChild(container);
    }
    
    // 챗봇 UI 컨트롤러
    class ChatbotWidget {
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
            
            // Enter 키로 전송
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
            
            console.log('[챗봇] 초기화 완료');
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
                const response = await fetch(CONFIG.apiUrl + CONFIG.chatApiEndpoint, {
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
                console.error('[챗봇] 오류:', error);
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
            
            // 메시지 내용
            const paragraphs = content.split('\n').filter(p => p.trim());
            paragraphs.forEach(para => {
                const p = document.createElement('p');
                p.textContent = para;
                contentDiv.appendChild(p);
            });
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            
            // 출처 정보 추가
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
    
    // 초기화 함수
    function init() {
        // CSS 로드
        loadCSS();
        
        // HTML 생성
        createChatbotHTML();
        
        // 챗봇 초기화
        window.Cafe24Chatbot = new ChatbotWidget();
        
        console.log('[챗봇] 위젯 로드 완료');
    }
    
    // DOM이 준비되면 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

