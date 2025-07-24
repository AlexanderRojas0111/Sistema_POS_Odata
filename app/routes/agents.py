from flask import Blueprint, request, jsonify
from app.agents.inventory_agent import InventoryAgent
from app.mcp.protocol import MCPProtocol, MCPContext
from typing import Dict, Any

agents = Blueprint('agents', __name__)
mcp = MCPProtocol()

# Diccionario para mantener instancias de agentes
active_agents = {}

@agents.route('/api/v2/agents', methods=['POST'])
def create_agent():
    """Crea un nuevo agente"""
    data = request.get_json()
    agent_type = data.get('type')
    
    if agent_type == 'inventory':
        agent = InventoryAgent(
            low_stock_threshold=data.get('low_stock_threshold', 5)
        )
        active_agents[agent.agent_id] = agent
        return jsonify(agent.to_dict())
    
    return jsonify({'error': 'Tipo de agente no soportado'}), 400

@agents.route('/api/v2/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Obtiene información de un agente"""
    agent = active_agents.get(agent_id)
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
        
    return jsonify(agent.to_dict())

@agents.route('/api/v2/agents/<agent_id>/tasks', methods=['POST'])
async def execute_task(agent_id):
    """Ejecuta una tarea en un agente"""
    agent = active_agents.get(agent_id)
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
        
    data = request.get_json()
    result = await agent.execute_task(data)
    return jsonify(result)

@agents.route('/api/v2/agents/communication', methods=['POST'])
async def agent_communication():
    """Maneja la comunicación entre agentes"""
    data = request.get_json()
    from_agent_id = data.get('from_agent')
    to_agent_id = data.get('to_agent')
    content = data.get('content')
    
    from_agent = active_agents.get(from_agent_id)
    to_agent = active_agents.get(to_agent_id)
    
    if not from_agent or not to_agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    # Crear contexto MCP
    context = MCPContext.create(
        user_id=data.get('user_id'),
        metadata=data.get('metadata', {})
    )
    
    # Crear mensaje MCP
    message = mcp.create_message(
        source_model=from_agent_id,
        target_model=to_agent_id,
        content=content,
        context=context
    )
    
    # Procesar mensaje
    response = await to_agent.process_message(content)
    
    return jsonify({
        'message_id': message.message_id,
        'response': response
    }) 