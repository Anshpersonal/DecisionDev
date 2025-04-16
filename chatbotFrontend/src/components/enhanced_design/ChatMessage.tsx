import React from 'react';
import { Paper, Typography, Box, Avatar } from '@mui/material';
import { ChatMessageType } from './EnhancedChatBot';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isSent = message.direction === 'sent';
  // Define custom colors for the bubbles.
  const sentBubbleColor = "#FFA500";     // light orange
  const receivedBubbleColor = "#FFF9C4"; // light yellow

  const bubbleBg = isSent ? sentBubbleColor : receivedBubbleColor;

  return (
    <Box sx={{ display: 'flex', justifyContent: isSent ? 'flex-end' : 'flex-start', mb: 1 }}>
      {!isSent && (
        <Avatar sx={{ mr: 1 }}>
          {message.name.charAt(0)}
        </Avatar>
      )}
      <Paper
        sx={{
          p: 1,
          maxWidth: '80%',
          backgroundColor: bubbleBg,
          borderRadius: 2,
          boxShadow: 1
        }}
      >
        <Typography variant="caption">{message.name}</Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
          {message.message}
        </Typography>
      </Paper>
      {isSent && (
        <Avatar sx={{ ml: 1 }}>
          {message.name.charAt(0)}
        </Avatar>
      )}
    </Box>
  );
}
