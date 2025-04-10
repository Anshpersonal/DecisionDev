import { useState, useEffect, useCallback } from 'react';
import { InlineLoading, Button } from '@carbon/react';
import { Reset, Information } from '@carbon/icons-react';
import { v4 as uuidv4 } from 'uuid';
import Header from './Header';
import Footer from './Footer';
import Message, { ChatMessage } from './Message';

import styles from './ChatBot.module.scss';
import { sendMessage, initializeConversation, resetConversation ,inspectMemory} from '../../api/rule-agent';

interface ChatBotProps {
  useDE: boolean
}

export default function ChatBot({ useDE }: ChatBotProps) {
  const botName = 'Bot';
  const backendName = useDE ? 'Using Decision Services' : 'Using RAG';
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: uuidv4(),
    name: botName,
    message: "Hi, I'm an AI to answer your questions. I can leverage your corporate decision services to generate answers compliant to your business policies",
    direction: 'received',
  }]);
  const [isProcessingAnswer, setProcessingAnswer] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // Initialize conversation when component mounts
  useEffect(() => {
    const initialize = async () => {
      try {
        await initializeConversation();
        setIsInitializing(false);
      } catch (error) {
        console.error('Failed to initialize conversation:', error);
        setIsInitializing(false);
      }
    };
    
    initialize();
  }, []);

  function addMessage(newMessage: ChatMessage) {
    setMessages((prev) => prev.concat(newMessage));
    setTimeout(() => {
      document.getElementById('bottom')?.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }, 0);
  }

  async function handleSubmit(newMessage: string) {
    if (isInitializing) return;
    if (newMessage === '') return;
    
    const currentDate = new Date();
    const timestamp = currentDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    addMessage({
      id: uuidv4(),
      name: `You ${timestamp}`,
      message: newMessage,
      direction: 'sent',
    });
    const messageName = `${botName} (${backendName}) ${timestamp}`;
    try {
      setProcessingAnswer(true);
      const messageResponse = await sendMessage(newMessage, useDE);
      addMessage({
        id: uuidv4(),
        name: messageName,
        message: messageResponse.output,
        type: (messageResponse.type == 'error')?'error':'text',
        direction: 'received',
      });
    } catch (e) {
      addMessage({
        id: uuidv4(),
        name: messageName,
        message: 'Failed to get chat response',
        direction: 'received',
        type: 'error',
      });
    } finally {
      setProcessingAnswer(false);
    }
  }

  const handleReset = useCallback(async () => {
    await resetConversation();
    setMessages([{
      id: uuidv4(),
      name: botName,
      message: "Hi, I'm an AI to answer your questions. I can leverage your corporate decision services to generate answers compliant to your business policies",
      direction: 'received',
    }]);
  }, [botName]);
  
  const handleDebug = useCallback(async () => {
    try {
      const memoryData = await inspectMemory();
      console.log('Memory inspection:', memoryData);
      
      if (memoryData && memoryData.status === 'success') {
        // Show memory as a system message
        const memoryContent = JSON.stringify(memoryData.memory, null, 2);
        addMessage({
          id: uuidv4(),
          name: 'System',
          message: `Memory Contents:\n\`\`\`json\n${memoryContent}\n\`\`\`\nMemory Size: ${memoryData.memory_size} characters`,
          direction: 'received',
          type: 'system',
        });
      } else {
        addMessage({
          id: uuidv4(),
          name: 'System',
          message: `Failed to retrieve memory: ${memoryData?.message || 'Unknown error'}`,
          direction: 'received',
          type: 'error',
        });
      }
    } catch (error) {
      console.error('Error inspecting memory:', error);
      addMessage({
        id: uuidv4(),
        name: 'System',
        message: `Error inspecting memory: ${error}`,
        direction: 'received',
        type: 'error',
      });
    }
  }, []);

  return (
    <div className={styles.chatbot}>
      <Header />
      <div className={styles.headerButtons}>
        <Button 
          kind="ghost" 
          size="sm"
          renderIcon={Information}
          onClick={handleDebug}
          iconDescription="Debug memory"
          disabled={isProcessingAnswer || isInitializing}
        >
          Debug
        </Button>
        <Button 
          kind="ghost" 
          size="sm"
          renderIcon={Reset}
          onClick={handleReset}
          iconDescription="Reset conversation"
          disabled={isProcessingAnswer || isInitializing}
          className={styles.resetButton}
        >
          Reset
        </Button>
      </div>
      <div className={styles.messages}>
        {messages.map((message) => <Message key={message.id} {...message} />)}
        <div id="bottom" style={{ marginTop: '2em' }} />
      </div>
      <div style={{ padding: '0 1em' }}>
        {isInitializing && 
          <InlineLoading status="active" iconDescription="Loading" description="Initializing conversation..." />}
        {isProcessingAnswer &&
          <InlineLoading status="active" iconDescription="Loading" description={`${botName} is thinking...`} />}
      </div>
      <Footer onSubmit={handleSubmit} disableSubmit={isProcessingAnswer || isInitializing} />
    </div>
  );
}