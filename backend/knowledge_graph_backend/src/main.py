from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path

# 导入蓝图
from routes.user import user_bp
from routes.knowledge_graph import knowledge_graph_bp
from routes.ai_assistant import ai_bp
from routes.symptom_diagnosis import symptom_diagnosis_bp, init_diagnosis_engine
from routes.ai_symptom_diagnosis import ai_symptom_diagnosis_bp, init_ai_diagnosis_engine
from models.user import db

# 创建Flask应用
app = Flask(__name__)

# 应用配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///knowledge_graph.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174", "http://127.0.0.1:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 初始化数据库
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()
    print("数据库表已创建")

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(knowledge_graph_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(symptom_diagnosis_bp, url_prefix='/api')
app.register_blueprint(ai_symptom_diagnosis_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
