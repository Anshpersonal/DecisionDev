import React, { KeyboardEvent, ChangeEvent, useState } from 'react';
import { Paper, TextField, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface ChatInputProps {
  input: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onSend: () => void;
  onPdfUpload: (file: File, prompt: string) => void;
  disabled: boolean;
  loading: boolean;
}

export default function ChatInput({ input, onChange, onSend, onPdfUpload, disabled, loading }: ChatInputProps) {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pdfPrompt, setPdfPrompt] = useState('');

  const handleKeyPress = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onSend();
    }
  };

  const fileInputRef = React.useRef<HTMLInputElement>(null);
  
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setOpenDialog(true);
    }
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
    setSelectedFile(null);
    setPdfPrompt('');
  };

  const handlePdfPromptChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPdfPrompt(e.target.value);
  };

  const handleSubmitPdfWithPrompt = () => {
    if (selectedFile) {
      onPdfUpload(selectedFile, pdfPrompt);
      handleDialogClose();
    }
  };

  return (
    <>
      <Paper
        elevation={3}
        sx={{
          p: 1,
          display: 'flex',
          alignItems: 'center',
          borderRadius: 2,
          backgroundColor: '#f5f5f5'
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={onChange}
          onKeyPress={handleKeyPress}
          disabled={disabled}
          size="small"
          sx={{ mr: 1 }}
        />
        <IconButton 
          color="primary" 
          onClick={handleUploadClick} 
          disabled={disabled || loading}
        >
          <CloudUploadIcon />
        </IconButton>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
          accept=".pdf"
        />
        <IconButton 
          color="primary" 
          onClick={onSend} 
          disabled={disabled || !input.trim() || loading}
        >
          <SendIcon />
        </IconButton>
      </Paper>

      {/* Dialog for PDF prompt */}
      <Dialog open={openDialog} onClose={handleDialogClose}>
        <DialogTitle>Add a prompt for your PDF</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="What would you like to ask about this PDF?"
            fullWidth
            variant="outlined"
            value={pdfPrompt}
            onChange={handlePdfPromptChange}
            placeholder="E.g., Summarize this document, or Extract key information about..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button 
            onClick={handleSubmitPdfWithPrompt} 
            variant="contained" 
            color="primary"
          >
            Upload with Prompt
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}