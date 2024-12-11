const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const historyBox = document.getElementById('historyBox');
let sessionId = "user-session";  // 默认会话ID

// 显示消息
function displayMessage(message, isUser = false) {
    const div = document.createElement('div');
    div.textContent = (isUser ? "你: " : "Bot: ") + message;
    div.classList.add(isUser ? 'user-message' : 'bot-message');  // 添加CSS样式
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 发送消息
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    displayMessage(message, true);  // 显示用户消息
    userInput.value = '';  // 清空输入框

    await sendChatRequest(message);
}

// 普通聊天请求
async function sendChatRequest(message) {
    const url = "/chat";
    const headers = {
        "Content-Type": "application/json"
    };

    const keyword = "default-keyword";  // 这里可以根据需求获取关键词
    const body = JSON.stringify({
        message: message,
        sessionId: sessionId,
        keyword: keyword
    });

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: body
        });

        if (!response.ok) {
            displayMessage("请求失败，请稍后再试");
            return;
        }

        const data = await response.json();
        if (data.textResponse) {
            displayMessage(data.textResponse);  // 显示Bot返回的文本消息
        }
        if (data.error) {
            displayMessage(`错误: ${data.error}`);  // 显示错误消息
        }
    } catch (error) {
        displayMessage(`发生错误: ${error.message}`);
    }
}

// 查询历史记录
async function getHistory(keyword = '') {
    const response = await fetch(`/history?keyword=${keyword}`);
    if (response.ok) {
        const data = await response.json();
        historyBox.innerHTML = '';  // 清空历史记录区域
        data.history.forEach(item => {
            const button = document.createElement('button');
            button.textContent = `${item.timestamp}: ${item.message}`;
            button.onclick = () => {
                displayMessage(item.message, false);  // 显示历史记录
            };
            historyBox.appendChild(button);
        });
    } else {
        alert("查询历史记录失败！");
    }
}

// 新开对话
async function newConversation() {
    const response = await fetch('/new_conversation', { method: 'POST' });
    if (response.ok) {
        const data = await response.json();
        sessionId = data.sessionId;  // 获取新的 sessionId
        chatBox.innerHTML = '';  // 清空聊天框
        displayMessage("新对话已开始。", false);
    } else {
        displayMessage("创建新对话失败，请稍后再试。");
    }
}

// 监听回车键
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 可选：初始化获取历史记录（如果需要的话）
getHistory();
