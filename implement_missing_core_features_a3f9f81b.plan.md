---
name: Implement Missing Core Features
overview: |
  Implement the four highest-impact missing features from the overview: Kalshi ingestion, Twitter social feed, AI event extraction/contradiction detection, and real cross-market comparison.
isProject: true
createdAt: 2026-05-13T21:14:33.815Z
updatedAt: 2026-05-13T21:14:33.815Z
estimatedCost: 2.00
costLimit: 5
todos:
  - id: "1"
    content: "Create backend/ingestion/kalshi.py with market fetcher"
    status: "pending"
  - id: "2"
    content: "Map Kalshi categories to our taxonomy (politics, macro, crypto, tech, sports)"
    status: "pending"
  - id: "3"
    content: "Store Kalshi markets in Market table with source='Kalshi'"
    status: "pending"
  - id: "4"
    content: "Create backend/ingestion/twitter.py for tweet fetching"
    status: "pending"
  - id: "5"
    content: "Support Twitter API v2 (free tier) with graceful fallback"
    status: "pending"
  - id: "6"
    content: "Extract tweet sentiment, engagement, and narrative velocity signals"
    status: "pending"
  - id: "7"
    content: "Store tweets as social posts linked to topics"
    status: "pending"
  - id: "8"
    content: "Create backend/ai/event_extractor.py with structured event extraction"
    status: "pending"
  - id: "9"
    content: "Extract entities, timeline, event type, involved parties from news"
    status: "pending"
  - id: "10"
    content: "Create backend/ai/contradiction_detector.py to flag news vs market divergences"
    status: "pending"
  - id: "11"
    content: "Update opportunity engine to use event extraction scores"
    status: "pending"
  - id: "12"
    content: "Update backend/api/markets.py cross-market endpoint to group by actual event"
    status: "pending"
  - id: "13"
    content: "Match Polymarket and Kalshi markets using keyword + semantic similarity"
    status: "pending"
  - id: "14"
    content: "Show real multi-platform disagreement scores"
    status: "pending"
  - id: "15"
    content: "Update frontend cross-market table to display real comparisons"
    status: "pending"
---

## Overview
Implement the four highest-impact missing features from the overview: Kalshi ingestion, Twitter social feed, AI event extraction/contradiction detection, and real cross-market comparison.

## Progress
- Total Tasks: 15
- Completed: 0/15 (0%)
- Estimated Cost: ~$2.00

## Implementation Tasks

### 1. Kalshi Market Ingestion

- [x] Create backend/ingestion/kalshi.py with market fetcher
- [x] Map Kalshi categories to our taxonomy (politics, macro, crypto, tech, sports)
- [ ] Store Kalshi markets in Market table with source='Kalshi'

### 2. X/Twitter Social Feed Ingestion

- [ ] Create backend/ingestion/twitter.py for tweet fetching
- [ ] Support Twitter API v2 (free tier) with graceful fallback
- [ ] Extract tweet sentiment, engagement, and narrative velocity signals
- [ ] Store tweets as social posts linked to topics

### 3. AI Event Extraction & Contradiction Detection

- [ ] Create backend/ai/event_extractor.py with structured event extraction
- [ ] Extract entities, timeline, event type, involved parties from news
- [ ] Create backend/ai/contradiction_detector.py to flag news vs market divergences
- [ ] Update opportunity engine to use event extraction scores

### 4. Real Cross-Market Comparison

- [ ] Update backend/api/markets.py cross-market endpoint to group by actual event
- [ ] Match Polymarket and Kalshi markets using keyword + semantic similarity
- [ ] Show real multi-platform disagreement scores
- [ ] Update frontend cross-market table to display real comparisons
