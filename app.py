import uuid

from flask import Flask, render_template, request, jsonify
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

app = Flask(__name__)

# 配置 PostgreSQL 数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/aihelper'  # 修改数据库连接配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10  # 设置数据库连接池的大小
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600  # 设置连接的回收时间（单位：秒）
db = SQLAlchemy(app)  # 初始化 SQLAlchemy
# 配置API相关信息
API_URL = "http://localhost:3001/api/v1/workspace/scmudbgroup/chat"
API_KEY = "G0TWDDS-6M94ZFY-P5QWP3S-6X5XSFZ"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 会话存储
sessions = {}


# 首页路由，显示聊天界面
@app.route('/')
def index():
    return render_template('index.html')


# 测试数据库连接
@app.route('/test_db')
def test_db():
    try:
        # 执行一个简单的查询来检查数据库连接
        result = db.session.execute(text('SELECT 1'))
        return "数据库连接成功！"
    except Exception as e:
        return f"数据库连接失败: {str(e)}"


# 存储聊天记录
def store_chat_history(session_id, message, keyword):
    from models import ChatHistory  # 延迟导入避免循环导入
    chat = ChatHistory(session_id=session_id, message=message, keyword=keyword)
    db.session.add(chat)
    db.session.commit()
    print(f"聊天记录已存入：{chat}")  # 打印存入的聊天记录


# 查询历史记录（根据关键字）
@app.route('/history', methods=['GET'])
def get_history():
    from models import ChatHistory  # 延迟导入避免循环导入
    keyword = request.args.get('keyword')
    print(f"查询历史记录，关键词: {keyword}")  # 打印接收到的关键词

    if keyword:
        history = ChatHistory.query.filter(ChatHistory.keyword == keyword).all()
    else:
        history = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()

    print(f"查询结果: {history}")  # 打印查询到的历史记录

    history_data = [{"session_id": record.session_id, "message": record.message, "timestamp": record.timestamp} for
                    record in history]
    return jsonify({"history": history_data})


# 新开对话的路由
@app.route('/new_conversation', methods=['POST'])
def new_conversation():
    # 创建新的会话ID（可以使用随机字符串或其他方式）
    session_id = str(uuid.uuid4())  # 使用UUID生成一个新的sessionId
    sessions[session_id] = []  # 初始化会话历史
    return jsonify({"sessionId": session_id})


# 普通聊天请求
@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    session_id = request.json.get('sessionId', 'user-session')
    keyword = request.json.get('keyword', 'default-keyword')

    # 如果没有会话历史，则初始化
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({"role": "user", "content": message})

    # 存储聊天记录
    store_chat_history(session_id, message, keyword)

    payload = {
        "message": message,
        "mode": "chat",
        "sessionId": session_id,
        "history": sessions[session_id]
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            data = response.json()
            resources = []
            if "sources" in data:
                for source in data["sources"]:
                    resources.append(source.get("title", "Unknown Document"))

            return jsonify({
                "textResponse": data.get("textResponse", ""),
                "resources": resources
            })
        else:
            return jsonify({
                "error": f"请求失败: {response.status_code}",
                "textResponse": ""
            })
    except Exception as e:
        return jsonify({
            "error": f"请求失败: {str(e)}",
            "textResponse": ""
        })


if __name__ == '__main__':
    # 在第一次运行时创建数据库表
    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5000)
