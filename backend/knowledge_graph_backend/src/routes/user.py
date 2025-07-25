from flask import Blueprint, jsonify, request
from models.user import User, db
from functools import wraps

user_bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            current_user = User.verify_token(token)
            if not current_user:
                return jsonify({'message': '无效的令牌'}), 401
        except:
            return jsonify({'message': '令牌验证失败'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# 认证相关路由
@user_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': '用户名、邮箱和密码都是必需的'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '注册失败，请稍后重试'}), 500

@user_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': '用户名和密码都是必需的'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': '用户名或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'message': '账户已被禁用'}), 401
        
        token = user.generate_token()
        if not token:
            return jsonify({'message': '生成令牌失败'}), 500
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': '登录失败，请稍后重试'}), 500

@user_bp.route('/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'message': '令牌有效',
        'user': current_user.to_dict()
    }), 200

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    try:
        data = request.json
        if not data or not data.get('username') or not data.get('email'):
            return jsonify({'message': '用户名和邮箱都是必需的'}), 400
        
        user = User(username=data['username'], email=data['email'])
        if data.get('password'):
            user.set_password(data['password'])
        else:
            user.set_password('default123')  # 默认密码
        
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '创建用户失败'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        if data.get('password'):
            user.set_password(data['password'])
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新用户失败'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '用户删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除用户失败'}), 500
