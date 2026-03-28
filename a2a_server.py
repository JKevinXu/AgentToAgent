"""A2A HTTP Server - Distributed Agent Communication"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from a2a_protocol import A2AMessage, A2AResponse
from a2a_agents import seller, buyer, buyer2

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

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

if __name__ == '__main__':
    print("Starting A2A HTTP Server...")
    print("Agents: seller, buyer, buyer2")
    print("Endpoints:")
    print("  POST /agent/<name> - Send A2A message")
    print("  GET /agent/<name>/card - Get agent card")
    app.run(port=8000, debug=True)


