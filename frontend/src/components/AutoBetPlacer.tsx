import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Grid,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Settings,
  Delete,
  Edit,
  Notifications,
  TrendingUp,
  Warning,
} from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

interface BetStrategy {
  id: string;
  name: string;
  minEV: number;
  maxBetAmount: number;
  autoPlace: boolean;
  notifications: boolean;
  sports: string[];
  bookmakers: string[];
  active: boolean;
}

const AutoBetPlacer: React.FC = () => {
  const { sendNotification, syncBetPlacement } = usePWA();
  const [strategies, setStrategies] = useState<BetStrategy[]>([]);
  const [isAutoBettingEnabled, setIsAutoBettingEnabled] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<BetStrategy | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    minEV: 5,
    maxBetAmount: 100,
    autoPlace: false,
    notifications: true,
    sports: [] as string[],
    bookmakers: [] as string[],
  });

  const availableSports = ['NFL', 'NBA', 'MLB', 'NHL', 'Soccer', 'Tennis', 'Golf'];
  const availableBookmakers = ['BetBCK', 'Pinnacle', 'Bet365', 'DraftKings', 'FanDuel'];

  useEffect(() => {
    // Load saved strategies from localStorage
    const saved = localStorage.getItem('betStrategies');
    if (saved) {
      setStrategies(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    // Save strategies to localStorage
    localStorage.setItem('betStrategies', JSON.stringify(strategies));
  }, [strategies]);

  const handleStrategySubmit = () => {
    if (editingStrategy) {
      // Update existing strategy
      setStrategies(prev => prev.map(s => 
        s.id === editingStrategy.id ? { ...formData, id: s.id, active: s.active } : s
      ));
    } else {
      // Create new strategy
      const newStrategy: BetStrategy = {
        ...formData,
        id: Date.now().toString(),
        active: false,
      };
      setStrategies(prev => [...prev, newStrategy]);
    }
    
    setDialogOpen(false);
    setEditingStrategy(null);
    setFormData({
      name: '',
      minEV: 5,
      maxBetAmount: 100,
      autoPlace: false,
      notifications: true,
      sports: [],
      bookmakers: [],
    });
  };

  const toggleStrategy = (strategyId: string) => {
    setStrategies(prev => prev.map(s => 
      s.id === strategyId ? { ...s, active: !s.active } : s
    ));
  };

  const deleteStrategy = (strategyId: string) => {
    setStrategies(prev => prev.filter(s => s.id !== strategyId));
  };

  const editStrategy = (strategy: BetStrategy) => {
    setEditingStrategy(strategy);
    setFormData({
      name: strategy.name,
      minEV: strategy.minEV,
      maxBetAmount: strategy.maxBetAmount,
      autoPlace: strategy.autoPlace,
      notifications: strategy.notifications,
      sports: strategy.sports,
      bookmakers: strategy.bookmakers,
    });
    setDialogOpen(true);
  };

  const handleAutoBettingToggle = () => {
    setIsAutoBettingEnabled(!isAutoBettingEnabled);
    
    if (!isAutoBettingEnabled) {
      sendNotification('Auto Betting Enabled', {
        body: 'Automatic bet placement is now active',
        tag: 'auto-betting-status',
      });
    }
  };

  const simulateBetPlacement = async (strategy: BetStrategy, betData: any) => {
    try {
      // Simulate bet placement
      console.log('Placing bet with strategy:', strategy, 'Bet data:', betData);
      
      // Use PWA background sync
      await syncBetPlacement({
        strategyId: strategy.id,
        betData,
        timestamp: new Date().toISOString(),
      });
      
      // Send notification
      if (strategy.notifications) {
        sendNotification('Bet Placed', {
          body: `Automatically placed bet on ${betData.team} with ${betData.ev}% EV`,
          tag: 'bet-placed',
        });
      }
      
      return true;
    } catch (error) {
      console.error('Error placing bet:', error);
      sendNotification('Bet Placement Failed', {
        body: 'Failed to place automatic bet. Please check logs.',
        tag: 'bet-failed',
      });
      return false;
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
            Automatic Bet Placement
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={isAutoBettingEnabled}
                onChange={handleAutoBettingToggle}
                color="primary"
              />
            }
            label="Enable Auto Betting"
            sx={{ color: '#fff' }}
          />
        </Box>
        
        <Alert 
          severity={isAutoBettingEnabled ? "success" : "info"}
          sx={{ mb: 2 }}
        >
          {isAutoBettingEnabled 
            ? "Automatic bet placement is active. The system will automatically place bets based on your strategies."
            : "Automatic bet placement is disabled. Enable to start automated betting."
          }
        </Alert>

        <Button
          variant="contained"
          startIcon={<Settings />}
          onClick={() => setDialogOpen(true)}
          sx={{ mb: 2 }}
        >
          Add New Strategy
        </Button>

        <Typography variant="subtitle2" sx={{ color: '#bdbdbd', mb: 2 }}>
          Active Strategies: {strategies.filter(s => s.active).length} / {strategies.length}
        </Typography>
      </Paper>

      {/* Strategy List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, mb: 2 }}>
          Betting Strategies
        </Typography>
        
        {strategies.length === 0 ? (
          <Alert severity="info">
            No strategies configured. Create your first strategy to get started with automatic betting.
          </Alert>
        ) : (
          <List>
            {strategies.map((strategy) => (
              <React.Fragment key={strategy.id}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ color: '#fff' }}>
                          {strategy.name}
                        </Typography>
                        {strategy.active && (
                          <Chip 
                            label="Active" 
                            color="success" 
                            size="small" 
                            icon={<PlayArrow />}
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
                          Min EV: {strategy.minEV}% | Max Bet: ${strategy.maxBetAmount}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          {strategy.sports.map(sport => (
                            <Chip key={sport} label={sport} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        edge="end"
                        onClick={() => editStrategy(strategy)}
                        sx={{ color: '#43a047' }}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        edge="end"
                        onClick={() => toggleStrategy(strategy.id)}
                        sx={{ color: strategy.active ? '#e53935' : '#43a047' }}
                      >
                        {strategy.active ? <Stop /> : <PlayArrow />}
                      </IconButton>
                      <IconButton
                        edge="end"
                        onClick={() => deleteStrategy(strategy.id)}
                        sx={{ color: '#e53935' }}
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>

      {/* Strategy Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingStrategy ? 'Edit Strategy' : 'New Betting Strategy'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Strategy Name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., High EV NFL Strategy"
              />
            </Grid>
            
            <Grid item xs={6}>
              <Typography gutterBottom>Minimum EV %</Typography>
              <Slider
                value={formData.minEV}
                onChange={(_, value) => setFormData(prev => ({ ...prev, minEV: value as number }))}
                min={1}
                max={20}
                marks={[
                  { value: 1, label: '1%' },
                  { value: 10, label: '10%' },
                  { value: 20, label: '20%' },
                ]}
                valueLabelDisplay="auto"
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Max Bet Amount ($)"
                type="number"
                value={formData.maxBetAmount}
                onChange={(e) => setFormData(prev => ({ ...prev, maxBetAmount: Number(e.target.value) }))}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.autoPlace}
                    onChange={(e) => setFormData(prev => ({ ...prev, autoPlace: e.target.checked }))}
                  />
                }
                label="Automatically place bets (requires confirmation)"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.notifications}
                    onChange={(e) => setFormData(prev => ({ ...prev, notifications: e.target.checked }))}
                  />
                }
                label="Send notifications for bets"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleStrategySubmit} 
            variant="contained"
            disabled={!formData.name}
          >
            {editingStrategy ? 'Update' : 'Create'} Strategy
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutoBetPlacer;
