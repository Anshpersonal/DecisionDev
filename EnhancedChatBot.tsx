import React, { useState, useEffect, useCallback, useRef, ChangeEvent } from 'react';
import { Paper, Box, CircularProgress, Typography } from '@mui/material';
import { v4 as uuidv4 } from 'uuid';
import ChatHeader from './ChatHeader';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
// Existing API functions; be sure to implement uploadPdf in your backend API module.
import { sendMessage, initializeConversation, resetConversation, inspectMemory, uploadPdf } from '../../api/rule-agent';

export interface ChatMessageType {
  id: string;
  name: string;
  message: string;
  direction: 'sent' | 'received';
  type?: 'system' | 'text' | 'error';
}

export default function EnhancedChatBot({ useDE }: { useDE: boolean }) {
  const botName = 'Bot';
  const backendName = useDE ? 'Decision Services' : 'RAG';
  const [messages, setMessages] = useState<ChatMessageType[]>([{
    id: uuidv4(),
    name: botName,
    message: "Hi, I am MAAS.AI, Your personal AI agent to help you with complete automated Form Validation Flow.",
    direction: 'received'
  }]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [input, setInput] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const init = async () => {
      try {
        await initializeConversation();
      } catch (error) {
        console.error("Initialization error:", error);
      } finally {
        setInitializing(false);
      }
    };
    init();
  }, []);

  // Auto-scroll when messages update.
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(scrollToBottom, [messages]);

  const addMessage = (msg: ChatMessageType) => {
    setMessages(prev => [...prev, msg]);
  };

  const handleSend = async () => {
    if (initializing || loading || !input.trim()) return;
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    addMessage({
      id: uuidv4(),
      name: `You ${timestamp}`,
      message: input,
      direction: 'sent'
    });
    const responseName = `${botName} (${backendName}) ${timestamp}`;
    setLoading(true);
    try {
      const response = await sendMessage(input, useDE);
      addMessage({
        id: uuidv4(),
        name: responseName,
        message: response.output,
        direction: 'received',
        type: response.type === 'error' ? 'error' : 'text'
      });
    } catch (error) {
      addMessage({
        id: uuidv4(),
        name: responseName,
        message: "Error: Could not fetch response.",
        direction: 'received',
        type: 'error'
      });
    }
    setLoading(false);
    setInput('');
  };

  const handleReset = useCallback(async () => {
    await resetConversation();
    setMessages([{
      id: uuidv4(),
      name: botName,
      message: "Hi, I'm ChatBot. Ask me anything!",
      direction: 'received'
    }]);
  }, [botName]);

  const handleDebug = useCallback(async () => {
    try {
      const memData = await inspectMemory();
      if (memData && memData.status === 'success') {
        const memContent = JSON.stringify(memData.memory, null, 2);
        addMessage({
          id: uuidv4(),
          name: 'System',
          message: `Memory Contents:\n${memContent}\nSize: ${memData.memory_size} characters`,
          direction: 'received',
          type: 'system'
        });
      } else {
        addMessage({
          id: uuidv4(),
          name: 'System',
          message: `Memory retrieval failed: ${memData?.message || 'Unknown error'}`,
          direction: 'received',
          type: 'error'
        });
      }
    } catch (error) {
      addMessage({
        id: uuidv4(),
        name: 'System',
        message: `Memory inspection error: ${error}`,
        direction: 'received',
        type: 'error'
      });
    }
  }, []);

  const handlePdfUpload = async (file: File, prompt?: string) => {
    setLoading(true);
    try {
      // Use the prompt if provided, otherwise pass an empty string
      const promptText = prompt || '';
      
      // Upload the PDF with the prompt
      const result = await uploadPdf(file, promptText);
      
      // Add system message about the PDF upload
      addMessage({
        id: uuidv4(),
        name: 'System',
        message: `PDF "${file.name}" uploaded successfully.`,
        direction: 'received',
        type: 'system'
      });
      
      // If there's a prompt, send it as a user message
      if (promptText.trim()) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        // Add the user's prompt as a message
        addMessage({
          id: uuidv4(),
          name: `You ${timestamp}`,
          message: `${promptText} (regarding the uploaded PDF: ${file.name})`,
          direction: 'sent'
        });
        
        // Process the prompt about the PDF
        const responseName = `${botName} (${backendName}) ${timestamp}`;
        // const response = await sendMessage(promptText, useDE);
        
        // Add the AI response
        addMessage({
          id: uuidv4(),
          name: responseName,
          message: result.output || result.final_response || "No response returned.",
          direction: 'received',
          type: result.type === 'error' ? 'error' : 'text'
        });
      }
    } catch (error) {
      addMessage({
        id: uuidv4(),
        name: 'System',
        message: `Error uploading PDF: ${error}`,
        direction: 'received',
        type: 'error'
      });
    }
    setLoading(false);
  };

  return (
    <Paper 
      elevation={3}
      sx={{
        height: 640,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden'
      }}
    >
      <ChatHeader 
        onDebug={handleDebug} 
        onReset={handleReset} 
        onPdfUpload={handlePdfUpload}
        loading={initializing || loading}
      />
      <Box sx={{ flex: 1, p: 2, overflowY: 'auto', backgroundColor: 'background.paper' }}>
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </Box>
      <ChatInput
        input={input}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
        onSend={handleSend}
        onPdfUpload={handlePdfUpload}
        disabled={initializing || loading}
        loading={initializing || loading}
      />
      {(initializing || loading) && (
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <CircularProgress size={24} />
          <Typography variant="body2" sx={{ ml: 1 }}>
            {initializing ? 'Initializing conversation...' : `${botName} is typing...`}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}