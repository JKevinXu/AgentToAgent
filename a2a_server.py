"""A2A HTTP Server - Distributed Agent Communication"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
from a2a_protocol import A2AMessage, A2AResponse
from a2a_agents import seller, buyer, buyer2
import json

app = Flask(__name__)
CORS(app)
sock = Sock(app)

@app.route('/agent/<agent_name>', methods=['POST'])
def agent_endpoint(agent_name):
    """Handle A2A messages via HTTP"""
    data = request.json

    # Parse A2A message
    message = A2AMessage(
        jsonrpc=data.get('jsonrpc', '2.0'),
        method=data.get('method'),
        params=data.get('params', {}),
        id=data.get('id', '1')
    )

    # Route to agent
    agents = {'seller': seller, 'buyer': buyer, 'buyer2': buyer2}
    agent = agents.get(agent_name)

    if not agent:
        return jsonify({'error': 'Agent not found'}), 404

    # Handle message
    response = agent.handle_message(message)

    return jsonify({
        'jsonrpc': response.jsonrpc,
        'result': response.result,
        'error': response.error,
        'id': response.id
    })

@app.route('/agent/<agent_name>/card', methods=['GET'])
def agent_card(agent_name):
    """Get agent card for discovery"""
    agents = {'seller': seller, 'buyer': buyer, 'buyer2': buyer2}
    agent = agents.get(agent_name)

    if not agent:
        return jsonify({'error': 'Agent not found'}), 404

    return jsonify(agent.get_agent_card())

@sock.route('/ws/evaluate')
def evaluate_stream(ws):
    """WebSocket endpoint for streaming evaluation"""
    from a2a_agents import handle_request_evaluation_stream
    import time
    from datetime import datetime

    data = ws.receive()
    params = json.loads(data)

    # Stream results as they come
    for result in handle_request_evaluation_stream(params):
        ws.send(json.dumps(result))

if __name__ == '__main__':
    print("Starting A2A HTTP Server...")
    print("Agents: seller, buyer, buyer2")
    print("Endpoints:")
    print("  POST /agent/<name> - Send A2A message")
    print("  GET /agent/<name>/card - Get agent card")
    app.run(port=8000, debug=True)


