# LLM Weather Tools demo - Capstone Project

A full-stack web application demonstrating LLM (Large Language Model) chat functionality with real-time streaming responses, built as a capstone project for an AI course.

## Features

- **Real-time Streaming Chat**: Experience seamless conversation with the AI model using Server-Sent Events (SSE)
- **Conversation History**: Maintains chat history client-side and sends it with each request
- **Weather Tool Integration**: The AI can fetch current weather data using integrated tools

### Backend
- **Python** with **FastAPI** for the API server
- **Google Gemini AI** (gemma-4-31b-it model) for LLM capabilities
- **Tool Integration**: Custom weather function using Open-Meteo API
- **CORS Support** for frontend communication

### Frontend
- **React 19** with **TypeScript**

## Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key
- Internet connection for API calls

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:8000`.

## Usage

1. Open your browser and go to `http://localhost:5173`
2. Type a message in the chat input
3. Ask about the weather to see the tool integration in action (e.g., "What's the weather in New York?")

## API Endpoints

### POST `/chat/stream`
Streams chat responses using Server-Sent Events.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "session_id": "optional-session-id"
}
```

**Response:** Server-Sent Events with the following event types:
- `{"type": "text", "content": "token(s)"}` - Streaming text chunks
- `{"type": "done", "usage": {"input_tokens": 42, "output_tokens": 9}}` - Completion with usage stats

### GET `/health`
Health check endpoint returning `{"status": "ok"}`.

## Project Structure

```
capstone_project/
├── backend/
│   ├── main.py              # FastAPI server with Gemini integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── App.tsx          # Main chat component
│   │   ├── components/      # React components
│   │   │   ├── ChatInput.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── UsageBar.tsx
│   │   ├── routes/
│   │   │   └── home.tsx     # Home route
│   │   └── welcome/
│   │       └── welcome.tsx  # Welcome component
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript config
│   └── vite.config.ts       # Vite config
└── README.md                # This file
```

## Key Learning Concepts

This project demonstrates several important concepts in AI application development:

1. **LLM Integration**: Connecting to and using large language models via APIs
2. **Streaming Responses**: Implementing real-time text streaming for better UX
3. **Tool Use**: Extending AI capabilities with custom functions (weather lookup)
4. **Full-Stack Development**: Combining Python backend with React frontend
5. **API Design**: Building RESTful APIs with proper error handling
6. **State Management**: Managing complex state in React applications
7. **Type Safety**: Using TypeScript for better code reliability

## Contributing

This is a capstone project for educational purposes. Feel free to fork and experiment with the code!

## AI Tools Used

ChatGPT to make the AI tools and handling LLM function calls. Copilot to make this README

## License

This project is for educational use only.