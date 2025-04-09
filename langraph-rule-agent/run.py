
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting LangGraph Rule Agent...")
    print("API endpoints will be available at:")
    print("- GET /rule-agent/chat_with_tools?userMessage=...")
    print("- GET /rule-agent/chat_without_tools?userMessage=...")
    print("- GET /rule-agent/health")
    app.run(debug=True, host='0.0.0.0', port=9000)