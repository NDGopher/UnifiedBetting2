import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home,
  TrendingUp,
  Calculate,
  Settings,
  Notifications,
  InstallMobile,
  Wifi,
  WifiOff,
} from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

interface MobileLayoutProps {
  children: React.ReactNode;
  title: string;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({ children, title }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { 
    isInstalled, 
    canInstall, 
    isOnline, 
    hasNotifications, 
    installApp,
    sendNotification 
  } = usePWA();
  
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const speedDialActions = [
    { icon: <Home />, name: 'Home', action: () => window.scrollTo(0, 0) },
    { icon: <TrendingUp />, name: 'EV Bets', action: () => document.getElementById('ev-bets')?.scrollIntoView({ behavior: 'smooth' }) },
    { icon: <Calculate />, name: 'Calculator', action: () => document.getElementById('calculator')?.scrollIntoView({ behavior: 'smooth' }) },
    { icon: <Settings />, name: 'Settings', action: () => console.log('Settings') },
  ];

  if (!isMobile) {
    return <>{children}</>;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Mobile App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, #43a047 0%, #2e7031 100%)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          
          {/* Status Indicators */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {!isOnline && (
              <IconButton color="inherit" size="small">
                <WifiOff />
              </IconButton>
            )}
            
            {canInstall && !isInstalled && (
              <IconButton 
                color="inherit" 
                size="small"
                onClick={installApp}
                title="Install App"
              >
                <InstallMobile />
              </IconButton>
            )}
            
            <IconButton 
              color="inherit" 
              size="small"
              onClick={() => sendNotification('Test', { body: 'Mobile notification test' })}
              title={hasNotifications ? 'Notifications Enabled' : 'Enable Notifications'}
            >
              <Notifications />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: 280,
            background: theme.palette.background.default,
            borderRight: `1px solid ${theme.palette.divider}`,
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem button onClick={() => window.scrollTo(0, 0)}>
              <ListItemIcon>
                <Home />
              </ListItemIcon>
              <ListItemText primary="Home" />
            </ListItem>
            
            <Divider />
            
            <ListItem button onClick={() => document.getElementById('ev-bets')?.scrollIntoView({ behavior: 'smooth' })}>
              <ListItemIcon>
                <TrendingUp />
              </ListItemIcon>
              <ListItemText primary="EV Bets" />
            </ListItem>
            
            <ListItem button onClick={() => document.getElementById('calculator')?.scrollIntoView({ behavior: 'smooth' })}>
              <ListItemIcon>
                <Calculate />
              </ListItemIcon>
              <ListItemText primary="Calculator" />
            </ListItem>
            
            <Divider />
            
            <ListItem>
              <ListItemIcon>
                <Wifi />
              </ListItemIcon>
              <ListItemText 
                primary="Status" 
                secondary={isOnline ? 'Online' : 'Offline'} 
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <Notifications />
              </ListItemIcon>
              <ListItemText 
                primary="Notifications" 
                secondary={hasNotifications ? 'Enabled' : 'Disabled'} 
              />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, pt: 8 }}>
        <Container maxWidth="sm" sx={{ pb: 8 }}>
          {children}
        </Container>
      </Box>

      {/* Mobile Speed Dial */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{ 
          position: 'fixed', 
          bottom: 16, 
          right: 16,
          '& .MuiFab-primary': {
            background: theme.palette.primary.main,
            '&:hover': {
              background: theme.palette.primary.dark,
            },
          },
        }}
        icon={<SpeedDialIcon />}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.action}
          />
        ))}
      </SpeedDial>
    </Box>
  );
};

export default MobileLayout;
