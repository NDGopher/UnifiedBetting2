import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Collapse,
  IconButton,
  TextField,
  Divider,
} from '@mui/material';
import {
  Refresh,
  CheckCircle,
  Warning,
  Error,
  AccessTime,
  Key,
  ExpandMore,
  ExpandLess,
  Download,
} from '@mui/icons-material';
import { betPlacementService } from '../services/betPlacementService';

interface TokenStatus {
  has_token: boolean;
  is_valid: boolean;
  age_minutes: number;
  expires_in_minutes: number;
  user?: string;
  token_preview?: string;
}

const TokenManager: React.FC = () => {
  const [tokenStatus, setTokenStatus] = useState<TokenStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [manualToken, setManualToken] = useState('');
  const [manualUser, setManualUser] = useState('');

  const API_BASE = 'http://localhost:5001';

  const fetchTokenStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/token/status`);
      if (response.ok) {
        const data = await response.json();
        setTokenStatus(data);
      } else {
        setTokenStatus({ has_token: false, is_valid: false, age_minutes: 0, expires_in_minutes: 0 });
      }
    } catch (error) {
      console.error('Failed to fetch token status:', error);
      setTokenStatus({ has_token: false, is_valid: false, age_minutes: 0, expires_in_minutes: 0 });
    }
  };

  const refreshToken = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${API_BASE}/api/token/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessage({ type: 'success', text: data.message || 'Token refreshed successfully!' });
        await fetchTokenStatus();
      } else {
        const errorData = await response.json();
        setMessage({ type: 'error', text: errorData.message || 'Failed to refresh token' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error refreshing token' });
    } finally {
      setLoading(false);
    }
  };

  const extractTokenFromBetBCK = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${API_BASE}/api/token/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessage({ type: 'success', text: data.message || 'Token extracted from BetBCK successfully!' });
        await fetchTokenStatus();
      } else {
        const errorData = await response.json();
        setMessage({ type: 'error', text: errorData.message || 'Failed to extract token from BetBCK' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error extracting token from BetBCK' });
    } finally {
      setLoading(false);
    }
  };

  const handleManualTokenSubmit = async () => {
    if (!manualToken.trim()) {
      setMessage({ type: 'error', text: 'Please enter a token' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // Send the token to the backend to store it
      const response = await fetch(`${API_BASE}/api/token/set`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: manualToken,
          user: manualUser || 'manual_user'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({ type: 'success', text: data.message || 'Manual token set successfully' });
        setManualToken('');
        setManualUser('');
        
        // Update the local state to show the token is now valid
        setTokenStatus({
          has_token: true,
          is_valid: true,
          age_minutes: 0,
          expires_in_minutes: 1440, // 24 hours
          user: manualUser || 'manual_user',
          token_preview: manualToken.substring(0, 8) + '...'
        });
      } else {
        const errorData = await response.json();
        setMessage({ type: 'error', text: errorData.message || 'Failed to set token on backend' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to set manual token' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTokenStatus();
    const interval = setInterval(fetchTokenStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (!tokenStatus) return 'default';
    if (tokenStatus.has_token && tokenStatus.is_valid) return 'success';
    if (tokenStatus.has_token && !tokenStatus.is_valid) return 'warning';
    return 'error';
  };

  const getStatusText = () => {
    if (!tokenStatus) return 'Unknown';
    if (tokenStatus.has_token && tokenStatus.is_valid) return 'Valid';
    if (tokenStatus.has_token && !tokenStatus.is_valid) return 'Expired';
    return 'None';
  };

  const getStatusIcon = () => {
    if (!tokenStatus) return <Warning />;
    if (tokenStatus.has_token && tokenStatus.is_valid) return <CheckCircle />;
    if (tokenStatus.has_token && !tokenStatus.is_valid) return <Warning />;
    return <Error />;
  };

  return (
    <Box sx={{ mb: 2 }}>
      {/* Compact Status Bar */}
      <Paper sx={{ p: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between', bgcolor: '#2a2a2a' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Key sx={{ fontSize: 16, color: '#ccc' }} />
          <Typography variant="body2" sx={{ color: '#ccc', fontWeight: 500 }}>
            Token Status:
          </Typography>
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            color={getStatusColor()}
            size="small"
            sx={{ height: 24, fontSize: '0.75rem' }}
          />
          {tokenStatus?.has_token && (
            <>
              <Typography variant="caption" sx={{ color: '#999', ml: 1 }}>
                Age: {tokenStatus.age_minutes}m
              </Typography>
              {tokenStatus.expires_in_minutes > 0 && (
                <Typography variant="caption" sx={{ color: '#999' }}>
                  | Expires: {tokenStatus.expires_in_minutes}m
                </Typography>
              )}
            </>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={extractTokenFromBetBCK}
            disabled={loading}
            sx={{ height: 28, fontSize: '0.75rem', minWidth: 80, color: '#2196f3', borderColor: '#2196f3' }}
            startIcon={<Download sx={{ fontSize: 16 }} />}
          >
            {loading ? <CircularProgress size={16} /> : 'Extract'}
          </Button>
          
          <Button
            size="small"
            variant="outlined"
            onClick={refreshToken}
            disabled={loading}
            sx={{ height: 28, fontSize: '0.75rem', minWidth: 80 }}
          >
            {loading ? <CircularProgress size={16} /> : <Refresh sx={{ fontSize: 16 }} />}
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
          
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ color: '#ccc' }}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </Paper>

      {/* Expandable Details */}
      <Collapse in={expanded}>
        <Paper sx={{ p: 2, mt: 1, bgcolor: '#2a2a2a' }}>
          {/* Manual Token Input */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#ccc' }}>
              Manual Token Input
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
              <TextField
                label="JWT Token"
                value={manualToken}
                onChange={(e) => setManualToken(e.target.value)}
                size="small"
                fullWidth
                sx={{ 
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#ccc' },
                  '& .MuiOutlinedInput-root': { 
                    '& fieldset': { borderColor: '#666' },
                    '&:hover fieldset': { borderColor: '#888' }
                  }
                }}
              />
              <TextField
                label="Username (optional)"
                value={manualUser}
                onChange={(e) => setManualUser(e.target.value)}
                size="small"
                sx={{ 
                  minWidth: 120,
                  '& .MuiInputBase-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#ccc' },
                  '& .MuiOutlinedInput-root': { 
                    '& fieldset': { borderColor: '#666' },
                    '&:hover fieldset': { borderColor: '#888' }
                  }
                }}
              />
              <Button
                variant="contained"
                size="small"
                onClick={handleManualTokenSubmit}
                disabled={loading || !manualToken.trim()}
                sx={{ bgcolor: '#4caf50', '&:hover': { bgcolor: '#45a049' } }}
              >
                Set Token
              </Button>
            </Box>
          </Box>

          <Divider sx={{ my: 2, borderColor: '#444' }} />

          {/* Detailed Status */}
          {tokenStatus?.has_token && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#ccc' }}>
                Token Details
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip
                  label={`User: ${tokenStatus.user || 'Unknown'}`}
                  size="small"
                  variant="outlined"
                  sx={{ color: '#ccc', borderColor: '#666' }}
                />
                {tokenStatus.token_preview && (
                  <Chip
                    label={`Token: ${tokenStatus.token_preview}`}
                    size="small"
                    variant="outlined"
                    sx={{ color: '#ccc', borderColor: '#666' }}
                  />
                )}
                <Chip
                  label={`Age: ${tokenStatus.age_minutes} minutes`}
                  size="small"
                  variant="outlined"
                  sx={{ color: '#ccc', borderColor: '#666' }}
                />
                {tokenStatus.expires_in_minutes > 0 && (
                  <Chip
                    label={`Expires in: ${tokenStatus.expires_in_minutes} minutes`}
                    size="small"
                    variant="outlined"
                    sx={{ color: '#ccc', borderColor: '#666' }}
                  />
                )}
              </Box>
            </Box>
          )}

          {/* Messages */}
          {message && (
            <Alert 
              severity={message.type} 
              sx={{ mb: 2, fontSize: '0.875rem' }}
              onClose={() => setMessage(null)}
            >
              {message.text}
            </Alert>
          )}

          {/* Instructions */}
          <Box sx={{ color: '#ccc', fontSize: '0.875rem' }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>Extract:</strong> Automatically extracts JWT token from BetBCK PropBuilder page
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>Refresh:</strong> Gets fresh token from BetBCK scraper
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>Manual Input:</strong> Enter your JWT token directly from BetBCK URL
            </Typography>
            <Typography variant="body2">
              • <strong>Auto-refresh:</strong> Tokens auto-refresh during bet placement if they expire
            </Typography>
          </Box>
        </Paper>
      </Collapse>
    </Box>
  );
};

export default TokenManager;
