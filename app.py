from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///signals.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

CORS(app)
db = SQLAlchemy(app)

# ===== DATABASE MODELS =====

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    asset = db.Column(db.String(50), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)
    expiry_time = db.Column(db.String(20), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20))
    reason = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self. id,
            'timestamp': self.timestamp.isoformat(),
            'asset': self.asset,
            'signal_type': self.signal_type,
            'expiry_time': self.expiry_time,
            'accuracy': self.accuracy,
            'price': self.price,
            'result': self.result,
            'reason': self.reason
        }

class Statistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(50), nullable=False)
    total_signals = db.Column(db. Integer, default=0)
    winning_signals = db.Column(db.Integer, default=0)
    losing_signals = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0)
    avg_accuracy = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'asset': self.asset,
            'total_signals': self. total_signals,
            'winning_signals': self.winning_signals,
            'losing_signals':  self.losing_signals,
            'win_rate': self.win_rate,
            'avg_accuracy': self.avg_accuracy
        }

# ===== API ROUTES =====

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'Online',
        'message': 'Binary Option Signal Engine Running',
        'version': '3.0'
    })

@app.route('/api/signals/latest', methods=['GET'])
def get_latest_signals():
    signals = Signal.query.order_by(Signal.timestamp.desc()).limit(10).all()
    return jsonify([signal.to_dict() for signal in signals])

@app.route('/api/signals', methods=['GET'])
def get_signals():
    page = request.args.get('page', 1, type=int)
    per_page = request. args.get('per_page', 20, type=int)
    
    signals = Signal.query.order_by(Signal.timestamp.desc()).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'signals': [signal.to_dict() for signal in signals.items],
        'total': signals.total,
        'pages': signals.pages,
        'current_page': page
    })

@app.route('/api/signals/asset/<asset>', methods=['GET'])
def get_signals_by_asset(asset):
    signals = Signal.query.filter_by(asset=asset).order_by(
        Signal.timestamp.desc()
    ).limit(50).all()
    return jsonify([signal.to_dict() for signal in signals])

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = Statistics. query.all()
    return jsonify([stat.to_dict() for stat in stats])

@app.route('/api/statistics/<asset>', methods=['GET'])
def get_asset_statistics(asset):
    stat = Statistics.query.filter_by(asset=asset).first()
    if stat:
        return jsonify(stat.to_dict())
    else:
        return jsonify({'error': 'Asset not found'}), 404

@app.route('/api/signals/create', methods=['POST'])
def create_signal():
    data = request.json
    signal = Signal(
        asset=data. get('asset'),
        signal_type=data.get('signal_type'),
        expiry_time=data.get('expiry_time'),
        accuracy=data. get('accuracy'),
        price=data.get('price'),
        reason=data.get('reason')
    )
    db.session.add(signal)
    db.session.commit()
    return jsonify(signal.to_dict()), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database':  'connected'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server Error'}), 500

if __name__ == '__main__': 
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
