#!/usr/bin/env python3
"""
Fast PTO WebSocket client to tap directly into the live data stream
Based on the GraphQL WebSocket connection seen in network tab
"""

import asyncio
import websockets
import json
import time
from typing import Dict, List, Any, Optional
import threading
from dataclasses import dataclass, asdict

@dataclass
class LiveEvent:
    id: str
    sport: str
    market: str
    home: str
    away: str
    books: Dict[str, Any]
    timestamp: float
    
class PTOWebSocketClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.events: Dict[str, LiveEvent] = {}
        self.last_update = time.time()
        self.message_count = 0
        
    async def connect(self):
        """Connect to PTO's GraphQL WebSocket"""
        uri = "wss://api.picktheodds.app/graphql"
        
        # Headers based on your network capture
        headers = {
            "Sec-WebSocket-Protocol": "graphql-transport-ws",
            "Origin": "https://picktheodds.app",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
        
        try:
            print(f"[WS] Connecting to {uri}...")
            self.ws = await websockets.connect(uri, extra_headers=headers)
            self.connected = True
            print(f"[WS] ✅ Connected successfully!")
            
            # Send connection init
            await self.send_connection_init()
            return True
            
        except Exception as e:
            print(f"[WS] ❌ Connection failed: {e}")
            return False
    
    async def send_connection_init(self):
        """Initialize the GraphQL transport connection"""
        init_message = {
            "type": "connection_init",
            "payload": {}
        }
        await self.ws.send(json.dumps(init_message))
        print(f"[WS] Sent connection_init")
    
    async def subscribe_to_odds(self, selections: List[str]):
        """Subscribe to live odds for the selected sports/markets"""
        
        # Map selections to GraphQL subscriptions
        subscriptions = []
        
        for selection in selections:
            if ':' in selection:
                sport, market = selection.split(':', 1)
                sport = sport.upper()
                market = market.upper()
                
                # Create GraphQL subscription based on selection
                query = f"""
                subscription {{
                  oddsUpdated(league: "{sport}", betGroup: "{market}") {{
                    id
                    gameId
                    homeTeam
                    awayTeam
                    league
                    betGroup
                    odds {{
                      bookmaker
                      value
                      line
                    }}
                    updatedAt
                  }}
                }}
                """
                
                subscriptions.append({
                    "id": f"{sport}_{market}",
                    "type": "start",
                    "payload": {
                        "query": query.strip()
                    }
                })
        
        # Send all subscriptions
        for sub in subscriptions:
            await self.ws.send(json.dumps(sub))
            print(f"[WS] Subscribed to {sub['id']}")
            await asyncio.sleep(0.1)  # Small delay between subscriptions
    
    async def listen(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.ws:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print(f"[WS] Connection closed")
            self.connected = False
        except Exception as e:
            print(f"[WS] Listen error: {e}")
            self.connected = False
    
    async def handle_message(self, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            self.message_count += 1
            
            if msg_type == "connection_ack":
                print(f"[WS] ✅ Connection acknowledged")
                
            elif msg_type == "data":
                # This is the live odds data!
                payload = data.get("payload", {})
                odds_data = payload.get("data", {})
                
                if odds_data:
                    await self.process_odds_update(odds_data)
                    
            elif msg_type == "error":
                print(f"[WS] ❌ Error: {data.get('payload')}")
                
            elif msg_type == "complete":
                print(f"[WS] Subscription complete: {data.get('id')}")
                
            # Log message frequency
            if self.message_count % 10 == 0:
                print(f"[WS] Processed {self.message_count} messages, {len(self.events)} events")
                
        except Exception as e:
            print(f"[WS] Message handling error: {e}")
    
    async def process_odds_update(self, odds_data: Dict[str, Any]):
        """Process live odds updates"""
        try:
            # Extract event data from GraphQL response
            odds_updated = odds_data.get("oddsUpdated", {})
            
            if odds_updated:
                event_id = odds_updated.get("id") or odds_updated.get("gameId")
                
                if event_id:
                    # Create/update live event
                    event = LiveEvent(
                        id=event_id,
                        sport=odds_updated.get("league", ""),
                        market=odds_updated.get("betGroup", ""),
                        home=odds_updated.get("homeTeam", ""),
                        away=odds_updated.get("awayTeam", ""),
                        books={},
                        timestamp=time.time()
                    )
                    
                    # Process odds
                    odds_list = odds_updated.get("odds", [])
                    for odd in odds_list:
                        bookmaker = odd.get("bookmaker", "")
                        if bookmaker:
                            event.books[bookmaker] = {
                                "value": odd.get("value"),
                                "line": odd.get("line")
                            }
                    
                    self.events[event_id] = event
                    self.last_update = time.time()
                    
                    # Debug output
                    print(f"[WS] 📊 Updated: {event.sport} {event.market} - {event.home} vs {event.away} - {len(event.books)} books")
                    
        except Exception as e:
            print(f"[WS] Odds processing error: {e}")
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get current events in the format expected by the main system"""
        events = []
        
        for event in self.events.values():
            # Convert to main system format
            event_dict = {
                "id": event.id,
                "sport": event.sport,
                "market": event.market,
                "home": event.home,
                "away": event.away,
                "books": event.books,
                "timestamp": event.timestamp,
                "source": "PTO_WS"
            }
            events.append(event_dict)
        
        return events
    
    def cleanup_old_events(self, max_age_seconds: float = 300):
        """Remove events older than max_age_seconds"""
        now = time.time()
        old_event_ids = [
            event_id for event_id, event in self.events.items()
            if now - event.timestamp > max_age_seconds
        ]
        
        for event_id in old_event_ids:
            del self.events[event_id]
        
        if old_event_ids:
            print(f"[WS] 🧹 Cleaned up {len(old_event_ids)} old events")

async def test_websocket_connection(selections: List[str]):
    """Test the WebSocket connection with given selections"""
    client = PTOWebSocketClient()
    
    if await client.connect():
        # Start listening in background
        listen_task = asyncio.create_task(client.listen())
        
        # Subscribe to odds
        await client.subscribe_to_odds(selections)
        
        # Monitor for 30 seconds
        print(f"[WS] Monitoring for 30 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            await asyncio.sleep(1)
            
            events = client.get_events()
            print(f"[WS] Current events: {len(events)}")
            
            # Show sample events
            for i, event in enumerate(events[:3]):
                print(f"[WS]   Event {i+1}: {event['sport']} {event['market']} - {event['home']} vs {event['away']} ({len(event['books'])} books)")
        
        # Clean up
        listen_task.cancel()
        await client.ws.close()
    
    else:
        print(f"[WS] Failed to connect")

def run_websocket_test():
    """Run WebSocket test from main thread"""
    selections = [
        "mlb:moneyline", "mlb:spread", "mlb:total",
        "wnba:moneyline", "wnba:spread", "wnba:total"
    ]
    
    try:
        asyncio.run(test_websocket_connection(selections))
    except Exception as e:
        print(f"[WS] Test error: {e}")

if __name__ == "__main__":
    print("PTO WebSocket Fast Client Test")
    print("=" * 40)
    run_websocket_test()
