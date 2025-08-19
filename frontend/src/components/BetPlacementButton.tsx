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
  Chip,
  CircularProgress,
} from '@mui/material';
import { PlayArrow, CheckCircle, Error } from '@mui/icons-material';
import { betPlacementService, BetPlacementData } from '../services/betPlacementService';
import CredentialsSetup from './CredentialsSetup';

interface BetPlacementButtonProps {
  betData: BetPlacementData;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'text' | 'outlined' | 'contained';
}

const BetPlacementButton: React.FC<BetPlacementButtonProps> = ({
  betData,
  disabled = false,
  size = 'medium',
  variant = 'contained'
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [credentialsOpen, setCredentialsOpen] = useState(false);
  const [wagerAmount, setWagerAmount] = useState(10);
  const [isPlacing, setIsPlacing] = useState(false);
  const [placementResult, setPlacementResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const handleOpenDialog = () => {
    setDialogOpen(true);
    setPlacementResult(null);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setPlacementResult(null);
  };

  const handlePlaceBet = async () => {
    if (!betPlacementService.isAuthenticated()) {
      setPlacementResult({
        success: false,
        message: 'Authentication required. Please set your credentials first.'
      });
      return;
    }

    // Validate bet data
    const validation = betPlacementService.validateBetData(betData, wagerAmount);
    if (!validation.isValid) {
      setPlacementResult({
        success: false,
        message: `Validation failed: ${validation.errors.join(', ')}`
      });
      return;
    }

    setIsPlacing(true);
    setPlacementResult(null);

    try {
      // Use backend API for bet placement with enhanced tracking
      const result = await betPlacementService.placeBetWithBackend(betData, wagerAmount, betData.odds);
      
      if (result.success) {
        setPlacementResult({
          success: true,
          message: `${result.message} ${result.betId ? `(ID: ${result.betId})` : ''}`
        });
        
        // If we have a bet ID, we can track its status
        if (result.betId) {
          console.log(`[BetPlacement] Bet placed with ID: ${result.betId}`);
          // You could store this ID for later status checking
        }
      } else {
        setPlacementResult({
          success: false,
          message: result.message || 'Bet placement failed. Please try again.'
        });
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';
      if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message);
      }
      setPlacementResult({
        success: false,
        message: 'Error: ' + errorMessage
      });
    } finally {
      setIsPlacing(false);
    }
  };

  const getAuthStatus = () => {
    return betPlacementService.getAuthStatus();
  };

  const authStatus = getAuthStatus();

  return (
    <>
      <Button
        variant={variant}
        size={size}
        startIcon={<PlayArrow />}
        onClick={handleOpenDialog}
        disabled={disabled || !authStatus.isAuthenticated}
        color="primary"
        sx={{
          minWidth: 120,
          fontWeight: 600,
        }}
      >
        {authStatus.isAuthenticated ? 'Place Bet' : 'Set Credentials'}
      </Button>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">Place Bet</Typography>
            {authStatus.isAuthenticated && (
              <Chip 
                label={`${authStatus.user} (${authStatus.group})`} 
                size="small" 
                color="success" 
              />
            )}
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {!authStatus.isAuthenticated ? (
            <Alert severity="warning" sx={{ mb: 2 }}>
              You need to set your betting credentials first. This requires your authentication token and user information.
            </Alert>
          ) : (
            <>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Bet Details
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography variant="body2">
                    <strong>Description:</strong> {betData.description}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Odds:</strong> {betData.odds}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Player ID:</strong> {betData.playerId}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Game ID:</strong> {betData.gameId}
                  </Typography>
                </Box>
              </Box>

              <TextField
                fullWidth
                label="Wager Amount ($)"
                type="number"
                value={wagerAmount}
                onChange={(e) => setWagerAmount(Number(e.target.value))}
                inputProps={{ min: 1, step: 1 }}
                sx={{ mb: 2 }}
              />

              {placementResult && (
                <Alert 
                  severity={placementResult.success ? 'success' : 'error'}
                  icon={placementResult.success ? <CheckCircle /> : <Error />}
                  sx={{ mb: 2 }}
                >
                  {placementResult.message}
                </Alert>
              )}
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          
          {authStatus.isAuthenticated ? (
            <Button
              onClick={handlePlaceBet}
              variant="contained"
              disabled={isPlacing}
              startIcon={isPlacing ? <CircularProgress size={16} /> : <PlayArrow />}
            >
              {isPlacing ? 'Placing Bet...' : 'Place Bet'}
            </Button>
          ) : (
            <Button
              onClick={() => setCredentialsOpen(true)}
              variant="contained"
            >
              Set Credentials
            </Button>
          )}
        </DialogActions>
      </Dialog>

      <CredentialsSetup 
        open={credentialsOpen} 
        onClose={() => setCredentialsOpen(false)} 
      />
    </>
  );
};

export default BetPlacementButton;
