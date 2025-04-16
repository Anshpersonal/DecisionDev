import React from 'react';
import { AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import RefreshIcon from '@mui/icons-material/Refresh';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useTheme } from '@mui/material/styles';

interface ChatHeaderProps {
  onDebug: () => void;
  onReset: () => void;
  onPdfUpload: (file: File, prompt?: string) => void;
  loading: boolean;
}

export default function ChatHeader({ onDebug, onReset, onPdfUpload, loading }: ChatHeaderProps) {
  const theme = useTheme();
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      // Pass an empty string as the prompt since we're not collecting it in the header
      onPdfUpload(e.target.files[0], "");
    }
  };

  return (
    <AppBar 
      position="static"
      sx={{ 
        backgroundColor: theme.palette.primary.main,
        borderRadius: '4px 4px 0 0' // Rounded top corners for navbar
      }}
    >
      <Toolbar variant="dense">
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ChatBot
        </Typography>
        <IconButton color="inherit" onClick={handleUploadClick} disabled={loading} aria-label="Upload PDF">
          <CloudUploadIcon />
        </IconButton>
        <input 
          type="file" 
          accept="application/pdf" 
          hidden 
          ref={fileInputRef} 
          onChange={handleFileChange} 
        />
        <IconButton color="inherit" onClick={onDebug} disabled={loading} aria-label="Debug memory">
          <InfoIcon />
        </IconButton>
        <IconButton color="inherit" onClick={onReset} disabled={loading} aria-label="Reset conversation">
          <RefreshIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}