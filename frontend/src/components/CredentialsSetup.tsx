import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Alert,
  Box,
  IconButton,
  InputAdornment,
  Chip,
} from '@mui/material';
import { Visibility, VisibilityOff, Settings, CheckCircle } from '@mui/icons-material';
import { betPlacementService } from '../services/betPlacementService';

interface CredentialsSetupProps {
  open: boolean;
  onClose: () => void;
}

const CredentialsSetup: React.FC<CredentialsSetupProps> = ({ open, onClose }) => {
  const [token, setToken] = useState('');
  const [user, setUser] = useState('');
  const [group, setGroup] = useState('bb');
  const [showToken, setShowToken] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const currentAuthStatus = betPlacementService.getAuthStatus();

  const handleSave = async () => {
    if (!token.trim() || !user.trim()) {
      setMessage({ type: 'error', text: 'Token and user are required' });
      return;
    }

    setIsSaving(true);
    setMessage(null);

    try {
      betPlacementService.setCredentials(token.trim(), user.trim(), group);
      
      setMessage({ 
        type: 'success', 
        text: 'Credentials saved successfully! You can now place bets automatically.' 
      });
      
      // Close dialog after a short delay
      setTimeout(() => {
        onClose();
        setMessage(null);
      }, 2000);
      
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: `Failed to save credentials: ${error instanceof Error ? error.message : 'Unknown error'}` 
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleClear = () => {
    betPlacementService.clearCredentials();
    setToken('');
    setUser('');
    setGroup('bb');
    setMessage({ type: 'success', text: 'Credentials cleared successfully' });
  };

  const handleClose = () => {
    setMessage(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings />
          <Typography variant="h6">Betting Credentials Setup</Typography>
          {currentAuthStatus.isAuthenticated && (
            <Chip 
              label="Authenticated" 
              size="small" 
              color="success" 
              icon={<CheckCircle />}
            />
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          To enable automatic bet placement, you need to provide your betting credentials. 
          These are used to authenticate with the betting platform.
        </Typography>

        {message && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        {currentAuthStatus.isAuthenticated && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Currently authenticated as <strong>{currentAuthStatus.user}</strong> 
            in group <strong>{currentAuthStatus.group}</strong>
          </Alert>
        )}

        <TextField
          fullWidth
          label="Authentication Token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          type={showToken ? 'text' : 'password'}
          placeholder="eyJhbGciOiJIUzI1NiJ9..."
          sx={{ mb: 2 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowToken(!showToken)}
                  edge="end"
                >
                  {showToken ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
          helperText="Your JWT authentication token from the betting platform"
        />

        <TextField
          fullWidth
          label="User ID"
          value={user}
          onChange={(e) => setUser(e.target.value)}
          placeholder="e.g., XYZ005"
          sx={{ mb: 2 }}
          helperText="Your user identifier on the betting platform"
        />

        <TextField
          fullWidth
          label="Group"
          value={group}
          onChange={(e) => setGroup(e.target.value)}
          placeholder="bb"
          sx={{ mb: 2 }}
          helperText="Your group identifier (usually 'bb' for buckeye)"
        />

        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Security Note:</strong> These credentials are stored locally in your browser. 
            Never share them with others and ensure you're on a secure connection.
          </Typography>
        </Alert>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          Cancel
        </Button>
        
        {currentAuthStatus.isAuthenticated && (
          <Button onClick={handleClear} color="error">
            Clear Credentials
          </Button>
        )}
        
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={isSaving || !token.trim() || !user.trim()}
          startIcon={isSaving ? <CheckCircle /> : undefined}
        >
          {isSaving ? 'Saving...' : 'Save Credentials'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CredentialsSetup;
