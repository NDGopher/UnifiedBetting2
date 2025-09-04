import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  SportsFootball,
  TrendingUp,
  Assessment,
  Info,
  Refresh,
  CheckCircle,
  Cancel,
  Home,
  DirectionsCar,
  TrendingDown,
  Group,
  Schedule,
  Star,
} from '@mui/icons-material';

interface TeaserLeg {
  team: string;
  original_spread: number;
  teased_spread: number;
  is_home: boolean;
  is_underdog: boolean;
  leg_type: string;
  criteria_score: number;
  win_rate_estimate: number;
  criteria_met: string[];
  optimal_filters: string[];
}

interface TeaserRecommendation {
  teaser_type: string;
  legs: TeaserLeg[];
  odds: {
    risk: number;
    win: number;
    american_odds: number;
  };
  expected_win_rate: number;
  expected_value: number;
  roi_percentage: number;
  criteria_score: number;
  total_criteria_met: number;
  max_possible_criteria: number;
  confidence_level: string;
  reasoning: string[];
}

interface WongTeaserData {
  games: Array<{
    home_team: string;
    away_team: string;
    home_spread: number;
    away_spread: number;
    total?: number;
    week?: number;
  }>;
  recommendations: TeaserRecommendation[];
  summary: {
    total_games: number;
    total_recommendations: number;
    top_recommendation?: TeaserRecommendation;
  };
}

const WongTeaserAnalyzer: React.FC = () => {
  const [data, setData] = useState<WongTeaserData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const analyzeWongTeasers = async () => {
    setLoading(true);
    setError(null);
    
    console.log('🚀 Starting Wong teaser analysis...');
    console.log('📡 Making request to: http://localhost:5001/api/wong-teaser/analyze');
    
    try {
      const response = await fetch('http://localhost:5001/api/wong-teaser/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('📊 Response status:', response.status);
      console.log('📊 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        console.error('❌ HTTP error:', response.status, response.statusText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      console.log('📊 Content-Type:', contentType);
      
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('❌ Non-JSON response:', text);
        throw new Error('Server returned non-JSON response. Check if backend is running.');
      }

      const result = await response.json();
      console.log('✅ Wong teaser analysis response:', result);
      console.log('📊 Success:', result.success);
      console.log('📊 Message:', result.message);
      console.log('📊 Games count:', result.data?.games?.length || 0);
      console.log('📊 Recommendations count:', result.data?.recommendations?.length || 0);
      
      if (result.success) {
        setData(result.data);
        setLastUpdated(new Date());
        console.log('✅ Analysis completed successfully');
      } else {
        console.error('❌ Analysis failed:', result.message);
        setError(result.message || 'Failed to analyze Wong teasers');
      }
    } catch (err) {
      console.error('❌ Wong teaser analysis error:', err);
      setError('Network error: ' + (err as Error).message);
    } finally {
      setLoading(false);
      console.log('🏁 Analysis request completed');
    }
  };

  const formatTeaserType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getConfidenceColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return '#43a047';
      case 'medium': return '#ffb300';
      case 'low': return '#e53935';
      default: return '#bdbdbd';
    }
  };

  const formatSpread = (spread: number) => {
    return spread > 0 ? `+${spread}` : spread.toString();
  };

  const formatOdds = (odds: { risk: number; win: number; american_odds: number }) => {
    if (odds.american_odds > 0) {
      return `+${odds.american_odds}`;
    }
    return odds.american_odds.toString();
  };

  const getOptimalFilterIcon = (filter: string) => {
    switch (filter) {
      case 'exact_spread': return <Star sx={{ fontSize: 16 }} />;
      case 'home_underdog': return <Home sx={{ fontSize: 16 }} />;
      case 'road_favorite': return <DirectionsCar sx={{ fontSize: 16 }} />;
      case 'low_total': return <TrendingDown sx={{ fontSize: 16 }} />;
      case 'non_divisional': return <Group sx={{ fontSize: 16 }} />;
      case 'mid_season': return <Schedule sx={{ fontSize: 16 }} />;
      default: return <CheckCircle sx={{ fontSize: 16 }} />;
    }
  };

  const getOptimalFilterLabel = (filter: string) => {
    switch (filter) {
      case 'exact_spread': return 'Perfect Spread';
      case 'home_underdog': return 'Home Dog';
      case 'road_favorite': return 'Road Favorite';
      case 'low_total': return 'Low Total';
      case 'non_divisional': return 'Non-Divisional';
      case 'mid_season': return 'Mid-Season';
      default: return filter;
    }
  };

  const renderOptimalFilters = (optimalFilters: string[]) => {
    const allFilters = ['exact_spread', 'home_underdog', 'road_favorite', 'low_total', 'non_divisional', 'mid_season'];
    
    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
        {allFilters.map((filter) => {
          const isMet = optimalFilters.includes(filter);
          return (
            <Chip
              key={filter}
              icon={isMet ? getOptimalFilterIcon(filter) : <Cancel sx={{ fontSize: 16 }} />}
              label={getOptimalFilterLabel(filter)}
              size="small"
              sx={{
                backgroundColor: isMet ? '#43a047' : '#333',
                color: isMet ? '#fff' : '#bdbdbd',
                border: isMet ? '1px solid #43a047' : '1px solid #555',
                '& .MuiChip-icon': {
                  color: isMet ? '#fff' : '#bdbdbd',
                },
              }}
            />
          );
        })}
      </Box>
    );
  };

  return (
    <Paper
      sx={{
        p: 3,
        display: "flex",
        flexDirection: "column",
        position: "relative",
        overflow: "hidden",
        transition: 'box-shadow 0.2s, transform 0.2s',
        '&:hover': {
          boxShadow: '0 8px 32px 0 rgba(67, 160, 71, 0.18)',
          transform: 'scale(1.012)',
        },
        border: '1.5px solid #333',
        '::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'linear-gradient(90deg, #43a047 0%, #23272f 100%)',
          zIndex: 1,
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          mb: 2,
        }}
      >
        <Typography
          component="h2"
          variant="h6"
          sx={{ color: '#fff', fontWeight: 700 }}
        >
          Wong Teaser Analyzer
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Tooltip title="Wong teasers are 6-point NFL teasers that cross key numbers (3 and 7)">
          <IconButton size="small" sx={{ color: '#bdbdbd' }}>
            <Info />
          </IconButton>
        </Tooltip>
        <Button
          variant="contained"
          onClick={analyzeWongTeasers}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          sx={{
            backgroundColor: '#43a047',
            '&:hover': { backgroundColor: '#2e7031' },
            fontWeight: 700,
          }}
        >
          {loading ? 'Analyzing...' : 'Analyze NFL Teasers'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {lastUpdated && (
        <Typography variant="caption" sx={{ color: '#bdbdbd', mb: 2 }}>
          Last updated: {lastUpdated.toLocaleTimeString()}
        </Typography>
      )}

      {data && (
        <>
          {/* Summary Stats */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#23272f', border: '1px solid #333' }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h4" sx={{ color: '#43a047', fontWeight: 700 }}>
                    {data.summary.total_games}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
                    NFL Games
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#23272f', border: '1px solid #333' }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h4" sx={{ color: '#ffb300', fontWeight: 700 }}>
                    {data.summary.total_recommendations}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
                    Recommendations
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Games List */}
          <Accordion sx={{ backgroundColor: '#23272f', border: '1px solid #333', mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                NFL Games ({data.games.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                {data.games.map((game, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={`${game.away_team} @ ${game.home_team}`}
                        secondary={
                          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                            <Chip
                              label={`Spread: ${formatSpread(game.away_spread)}`}
                              size="small"
                              sx={{ backgroundColor: '#43a047', color: '#fff' }}
                            />
                            {game.total && (
                              <Chip
                                label={`Total: ${game.total}`}
                                size="small"
                                sx={{ backgroundColor: '#00bcd4', color: '#fff' }}
                              />
                            )}
                            {game.week && (
                              <Chip
                                label={`Week ${game.week}`}
                                size="small"
                                sx={{ backgroundColor: '#bdbdbd', color: '#000' }}
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < data.games.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>


          {/* Recommendations */}
          {data.recommendations.length > 0 ? (
            <Box>
              <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600, mb: 2 }}>
                🏆 Ranked by Optimal Filters & ROI
              </Typography>
              {data.recommendations.slice(0, 5).map((rec, index) => (
                <Card
                  key={index}
                  sx={{
                    backgroundColor: '#23272f',
                    border: '1px solid #333',
                    mb: 2,
                    '&:hover': {
                      border: '1px solid #43a047',
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                        {formatTeaserType(rec.teaser_type)}
                      </Typography>
                      <Chip
                        label={rec.confidence_level}
                        size="small"
                        sx={{
                          backgroundColor: getConfidenceColor(rec.confidence_level),
                          color: '#fff',
                          fontWeight: 600,
                        }}
                      />
                      <Chip
                        label={`${rec.total_criteria_met}/${rec.max_possible_criteria} Optimal`}
                        size="small"
                        sx={{
                          backgroundColor: rec.total_criteria_met >= 4 ? '#43a047' : rec.total_criteria_met >= 2 ? '#ffb300' : '#e53935',
                          color: '#fff',
                          fontWeight: 600,
                        }}
                      />
                      <Box sx={{ flexGrow: 1 }} />
                    </Box>

                    {/* Optimal Filters Display */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ color: '#bdbdbd', mb: 1 }}>
                        Optimal Filters:
                      </Typography>
                      {renderOptimalFilters(rec.legs[0]?.optimal_filters || [])}
                    </Box>

                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={6} sm={4}>
                        <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
                          Your Odds
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                          {formatOdds(rec.odds)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={4}>
                        <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
                          Criteria Score
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                          {rec.criteria_score}
                        </Typography>
                      </Grid>
                    </Grid>

                    <Typography variant="subtitle2" sx={{ color: '#bdbdbd', mb: 1 }}>
                      Legs:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {rec.legs.map((leg, legIndex) => (
                        <Chip
                          key={legIndex}
                          label={`${leg.team}: ${formatSpread(leg.original_spread)} → ${formatSpread(leg.teased_spread)}`}
                          size="small"
                          sx={{
                            backgroundColor: leg.is_underdog ? '#ffb300' : '#00bcd4',
                            color: '#fff',
                          }}
                        />
                      ))}
                    </Box>

                    <Typography variant="subtitle2" sx={{ color: '#bdbdbd', mb: 1 }}>
                      Reasoning:
                    </Typography>
                    <List dense>
                      {rec.reasoning.map((reason, reasonIndex) => (
                        <ListItem key={reasonIndex} sx={{ py: 0 }}>
                          <ListItemText
                            primary={reason}
                            sx={{ '& .MuiListItemText-primary': { fontSize: '0.9rem', color: '#bdbdbd' } }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : (
            <Alert severity="info">
              No Wong teaser opportunities found in current NFL games.
            </Alert>
          )}
        </>
      )}

      {!data && !loading && !error && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <SportsFootball sx={{ fontSize: 64, color: '#bdbdbd', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#bdbdbd', mb: 1 }}>
            Ready to Analyze Wong Teasers
          </Typography>
          <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
            Click the button above to analyze current NFL games for Wong teaser opportunities
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default WongTeaserAnalyzer;
