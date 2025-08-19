// Bet Placement Service based on HAR file analysis
// This service handles automatic bet placement for PropBuilder EV bets

export interface BetPlacementData {
  playerId: number;
  gameId: number;
  statistic: number;
  conditionValue: number;
  provider: string;
  type: number;
  description: string;
  odds: number;
  wager: number;
  sportsbook: string;
  currency: string;
}

export interface BetPlacementRequest {
  events: Array<{
    odds: number;
    player1: number;
    game1: number;
    statistic: number;
    conditionValue: number;
    provider: string;
    type: number;
    description: string;
  }>;
  sportsbook: string;
  currency: string;
  odds: number;
  wager: number;
  token: string;
  user: string;
  group: string;
  groupType: string | null;
  description: string;
}

class BetPlacementService {
  private baseUrl = 'https://bv2-us.digitalsportstech.com';
  private apiEndpoint = '/api/bet-v2/createBulk';
  private tokenApiBase = 'http://localhost:5001'; // Main Backend (integrated)
  
  // This would need to be obtained from your authentication system
  private authToken: string | null = null;
  private userInfo: { user: string; group: string } | null = null;

  constructor() {
    // Initialize with stored credentials if available
    this.loadStoredCredentials();
  }

  private loadStoredCredentials() {
    // Load from localStorage or secure storage
    const stored = localStorage.getItem('betPlacementCredentials');
    if (stored) {
      try {
        const credentials = JSON.parse(stored);
        this.authToken = credentials.token;
        this.userInfo = credentials.userInfo;
      } catch (error) {
        console.error('Failed to load stored credentials:', error);
      }
    }
  }

  private saveCredentials(token: string, userInfo: { user: string; group: string }) {
    this.authToken = token;
    this.userInfo = userInfo;
    
    // Save to localStorage (in production, use secure storage)
    localStorage.setItem('betPlacementCredentials', JSON.stringify({
      token,
      userInfo
    }));
  }

  /**
   * Split a large wager into multiple bets based on constraints
   */
  private calculateBetSplits(totalAmount: number, maxPerBet: number = 100, maxTotalWin: number = 500, odds: number): Array<{amount: number, expectedWin: number}> {
    const splits: Array<{amount: number, expectedWin: number}> = [];
    
    // Convert American odds to decimal for calculations
    const decimalOdds = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
    
    let remainingAmount = totalAmount;
    
    while (remainingAmount > 0) {
      // Calculate max bet amount considering both constraints
      const maxBetForWinLimit = maxTotalWin / (decimalOdds - 1); // Max bet to not exceed win limit
      const maxAllowedBet = Math.min(maxPerBet, maxBetForWinLimit);
      
      // Determine actual bet amount for this split
      const betAmount = Math.min(remainingAmount, maxAllowedBet);
      const expectedWin = betAmount * (decimalOdds - 1);
      
      splits.push({
        amount: Math.round(betAmount * 100) / 100, // Round to 2 decimals
        expectedWin: Math.round(expectedWin * 100) / 100
      });
      
      remainingAmount -= betAmount;
      
      // Safety check to prevent infinite loops
      if (splits.length > 20) {
        console.warn('Too many bet splits required, stopping at 20');
        break;
      }
    }
    
    return splits;
  }

  /**
   * Place a single prop bet (or multiple splits if amount > $100)
   */
  async placePropBet(betData: BetPlacementData, wagerAmount: number, currentOdds: number): Promise<boolean> {
    try {
      if (!this.authToken || !this.userInfo) {
        throw new Error('Authentication required. Please set credentials first.');
      }

      // CRITICAL: Validate that odds haven't changed
      if (Math.abs(betData.odds - currentOdds) > 5) { // Allow 5 point variance
        throw new Error(`Odds changed! Frontend shows ${currentOdds}, bet data has ${betData.odds}. Bet cancelled for safety.`);
      }

      // Calculate bet splits if amount exceeds limits
      const betSplits = this.calculateBetSplits(wagerAmount, 100, 500, betData.odds);
      
      console.log(`[BetPlacement] Splitting $${wagerAmount} into ${betSplits.length} bets:`, betSplits);
      
      let allSuccessful = true;
      const results = [];
      
      // Place each bet split with variable delays to avoid bot detection
      for (let i = 0; i < betSplits.length; i++) {
        const split = betSplits[i];
        
        console.log(`[BetPlacement] Placing bet ${i + 1}/${betSplits.length}: $${split.amount} (expected win: $${split.expectedWin})`);
        
        const request: BetPlacementRequest = {
          events: [{
            odds: betData.odds,
            player1: betData.playerId,
            game1: betData.gameId,
            statistic: betData.statistic,
            conditionValue: betData.conditionValue,
            provider: betData.provider,
            type: betData.type,
            description: betData.description
          }],
          sportsbook: betData.sportsbook,
          currency: betData.currency,
          odds: betData.odds,
          wager: split.amount,
          token: this.authToken,
          user: this.userInfo.user,
          group: this.userInfo.group,
          groupType: null,
          description: `${betData.description} (Split ${i + 1}/${betSplits.length})`
        };

        const response = await fetch(`${this.baseUrl}${this.apiEndpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.authToken}`,
            'Accept': 'application/json, text/plain, */*',
            'Origin': this.baseUrl,
            'Referer': `${this.baseUrl}/betbuilder?sb=${betData.sportsbook}&user=${this.userInfo.user}&token=${this.authToken}`
          },
          body: JSON.stringify([request])
        });

        if (response.ok) {
          const result = await response.json();
          results.push(result);
          console.log(`[BetPlacement] Bet ${i + 1} placed successfully:`, result);
          
          // Variable delay between bets (200-800ms) to avoid bot detection
          if (i < betSplits.length - 1) {
            const delay = 200 + Math.random() * 600; // Random delay between 200-800ms
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        } else {
          const errorText = await response.text();
          console.error(`[BetPlacement] Bet ${i + 1} failed:`, response.status, errorText);
          
          // Try to handle auth errors with token refresh
          const tokenRefreshed = await this.handleAuthError(errorText);
          if (tokenRefreshed) {
            console.log('[BetPlacement] Token refreshed, retrying bet...');
            // Retry this bet with new token
            i--; // Retry the same bet
            continue;
          }
          
          allSuccessful = false;
          break; // Stop placing remaining bets if one fails
        }
      }
      
      if (allSuccessful) {
        console.log(`[BetPlacement] All ${betSplits.length} bets placed successfully. Total wagered: $${wagerAmount}`);
        return true;
      } else {
        console.error(`[BetPlacement] Failed to place all bets. Some may have been placed successfully.`);
        return false;
      }
    } catch (error) {
      console.error('Error placing bet:', error);
      return false;
    }
  }

  /**
   * Set authentication credentials
   */
  setCredentials(token: string, user: string, group: string = 'bb') {
    this.saveCredentials(token, { user, group });
  }

  /**
   * Check if credentials are set
   */
  isAuthenticated(): boolean {
    return !!(this.authToken && this.userInfo);
  }

  /**
   * Clear stored credentials
   */
  clearCredentials() {
    this.authToken = null;
    this.userInfo = null;
    localStorage.removeItem('betPlacementCredentials');
  }

  /**
   * Get current authentication status
   */
  getAuthStatus() {
    return {
      isAuthenticated: this.isAuthenticated(),
      user: this.userInfo?.user || null,
      group: this.userInfo?.group || null,
      hasToken: !!this.authToken
    };
  }

  /**
   * Get fresh token from backend scraper
   */
  async refreshTokenFromScraper(forceRefresh: boolean = false): Promise<{success: boolean, message: string, tokenData?: any}> {
    try {
      console.log('[BetPlacement] Requesting token refresh from backend...');
      
      const response = await fetch(`${this.tokenApiBase}/api/token/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_refresh: forceRefresh })
      });

      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.token_data) {
          // Automatically set the credentials
          this.setCredentials(
            result.token_data.token,
            result.token_data.user,
            result.token_data.group
          );
          
          return {
            success: true,
            message: `Token refreshed successfully. Valid for ${Math.floor(result.token_data.expires_in / 60)} minutes.`,
            tokenData: result.token_data
          };
        } else {
          return {
            success: false,
            message: result.message || 'Failed to extract token'
          };
        }
      } else {
        const errorText = await response.text();
        return {
          success: false,
          message: `Backend error: ${response.status} ${errorText}`
        };
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';
      if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message);
      }
      return {
        success: false,
        message: 'Network error: ' + errorMessage
      };
    }
  }

  /**
   * Get token status from backend
   */
  async getTokenStatus(): Promise<{success: boolean, status?: any, message?: string}> {
    try {
      const response = await fetch(`${this.tokenApiBase}/api/token/status`);
      
      if (response.ok) {
        const result = await response.json();
        return {
          success: true,
          status: result.status
        };
      } else {
        return {
          success: false,
          message: `Failed to get token status: ${response.status}`
        };
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';
      if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message);
      }
      return {
        success: false,
        message: 'Network error: ' + errorMessage
      };
    }
  }

  /**
   * Auto-refresh token if API call fails due to auth issues
   */
  private async handleAuthError(errorText: string): Promise<boolean> {
    const authErrorIndicators = [
      'unauthorized',
      'token expired',
      'invalid token',
      'authentication failed',
      '401',
      'forbidden',
      '403'
    ];

    const isAuthError = authErrorIndicators.some(indicator => 
      errorText.toLowerCase().includes(indicator)
    );

    if (isAuthError) {
      console.log('[BetPlacement] Auth error detected, attempting token refresh...');
      const refreshResult = await this.refreshTokenFromScraper(true);
      return refreshResult.success;
    }

    return false;
  }

  /**
   * Validate bet data before placement
   */
  validateBetData(betData: BetPlacementData, wagerAmount: number): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!betData.playerId || betData.playerId <= 0) {
      errors.push('Invalid player ID');
    }

    if (!betData.gameId || betData.gameId <= 0) {
      errors.push('Invalid game ID');
    }

    if (!betData.statistic || betData.statistic <= 0) {
      errors.push('Invalid statistic type');
    }

    if (wagerAmount <= 0) {
      errors.push('Wager amount must be greater than 0');
    }

    if (!betData.odds || betData.odds <= 1) {
      errors.push('Invalid odds');
    }

    if (!betData.description) {
      errors.push('Bet description is required');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Place bet using backend API with enhanced tracking
   */
  async placeBetWithBackend(betData: BetPlacementData, wagerAmount: number, currentOdds: number): Promise<{
    success: boolean;
    message: string;
    betId?: string;
    status?: string;
    details?: any;
  }> {
    try {
      console.log('[BetPlacement] Placing bet via backend API...');
      
      const response = await fetch(`${this.tokenApiBase}/api/bet/place`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bet_data: betData,
          wager_amount: wagerAmount,
          current_odds: currentOdds
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('[BetPlacement] Backend response:', result);
        return result;
      } else {
        const errorText = await response.text();
        console.error('[BetPlacement] Backend error:', response.status, errorText);
        
        // Try to handle auth errors with token refresh
        const tokenRefreshed = await this.handleAuthError(errorText);
        if (tokenRefreshed) {
          console.log('[BetPlacement] Token refreshed, retrying bet...');
          return this.placeBetWithBackend(betData, wagerAmount, currentOdds);
        }
        
        return {
          success: false,
          message: `Backend error: ${response.status} ${errorText}`,
          status: 'backend_error'
        };
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';
      if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message);
      }
      console.error('[BetPlacement] Network error:', errorMessage);
      return {
        success: false,
        message: 'Network error: ' + errorMessage,
        status: 'network_error'
      };
    }
  }

  /**
   * Get bet status from backend
   */
  async getBetStatus(betId: string): Promise<{
    success: boolean;
    message: string;
    betId?: string;
    status?: string;
    details?: any;
  }> {
    try {
      const response = await fetch(`${this.tokenApiBase}/api/bet/status/${betId}`);
      
      if (response.ok) {
        const result = await response.json();
        return result;
      } else {
        const errorText = await response.text();
        return {
          success: false,
          message: `Failed to get bet status: ${response.status} ${errorText}`
        };
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';
      if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message);
      }
      return {
        success: false,
        message: 'Network error: ' + errorMessage
      };
    }
  }

  /**
   * Simulate bet placement for testing (doesn't actually place bet)
   */
  simulateBetPlacement(betData: BetPlacementData, wagerAmount: number): Promise<boolean> {
    return new Promise((resolve) => {
      // Simulate API delay
      setTimeout(() => {
        console.log('SIMULATION: Bet placement request:', {
          betData,
          wagerAmount,
          timestamp: new Date().toISOString()
        });
        
        // Simulate success (90% success rate for testing)
        const success = Math.random() > 0.1;
        resolve(success);
      }, 1000);
    });
  }
}

// Export singleton instance
export const betPlacementService = new BetPlacementService();

export default BetPlacementService;
