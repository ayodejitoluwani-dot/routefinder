# Public Transport Route Finder - User Manual

**Version 1.0**  
**Date:** April 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
   - [Google Maps Setup](#google-maps-setup)
   - [HERE Maps Setup](#here-maps-setup-recommended)
   - [Choosing Your Provider](#choosing-your-provider)
6. [Using the Application](#using-the-application)
   - [Main Interface](#main-interface)
   - [Finding Routes](#finding-routes)
   - [Viewing Results](#viewing-results)
   - [Route Details View](#route-details-view)
   - [Comparison Table](#comparison-table)
   - [User Reviews](#user-reviews)
7. [Advanced Features](#advanced-features)
   - [Departure/Arrival Time](#departurearrival-time)
   - [Real-time Traffic](#real-time-traffic)
   - [Route Scoring](#route-scoring)
8. [Troubleshooting](#troubleshooting)
9. [Project Architecture](#project-architecture)
10. [API Reference](#api-reference)
11. [Frequently Asked Questions](#frequently-asked-questions)
12. [Support & Contributing](#support--contributing)

---

## Introduction

The **Public Transport Route Finder** is a web-based application that helps users find optimal public transportation routes between any two locations. Built with Streamlit, it integrates with major mapping services (Google Maps and HERE Maps) to provide real-time transit information, multiple route options, and detailed step-by-step directions.

### Who Is This For?

- **Commuters** looking for the best transit options
- **Travelers** planning journeys in unfamiliar cities
- **Transportation planners** comparing route efficiency
- **Developers** who want to understand multi-provider API integration

### Key Benefits

- **Multi-provider support** - Switch between Google Maps and HERE Maps
- **Cost-effective** - HERE Maps offers 250K free requests/month
- **User-friendly** - Clean, intuitive interface with no technical knowledge required
- **Customizable** - Adjust scoring weights to prioritize what matters to you
- **Community-driven** - Rate and review routes to help others

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Provider Support** | Use either Google Maps or HERE Maps API |
| **Multiple Route Options** | Compare up to 5 alternative routes simultaneously |
| **Route Scoring** | Automatic ranking based on duration, transfers, and walking distance |
| **Real-time Traffic** | Optional traffic-aware duration estimates (Google Maps) |
| **Departure/Arrival Planning** | Plan trips for specific times |
| **Step-by-Step Directions** | Detailed transit instructions with vehicle types and stops |
| **User Reviews** | Rate routes and read community feedback |
- **Comparison Table** | Side-by-side route comparison
- **Favorites** | Save frequently-used routes
- **Local Storage** | All data stored locally in JSON files

---

## System Requirements

### Minimum Requirements

- **Operating System:** Windows, macOS, or Linux
- **Python:** 3.8 or higher
- **RAM:** 512 MB minimum (1 GB recommended)
- **Internet:** Required for API calls to map providers
- **Disk Space:** ~100 MB for application + dependencies

### Recommended Specifications

- **Python:** 3.10 or higher
- **RAM:** 2 GB+
- **SSD storage** for faster loading

---

## Installation

### Step 1: Prerequisites

Ensure Python is installed:

```bash
python --version
# Should show: Python 3.8 or higher
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

### Step 2: Clone or Download

```bash
# Option A: Clone the repository
git clone <repository-url>
cd routefinder

# Option B: Download and extract the ZIP
# Extract to your desired directory
cd routefinder
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected packages:**
- streamlit
- googlemaps (for Google provider)
- requests (for HERE provider)
- python-dotenv

### Step 4: Verify Installation

```bash
python -c "import streamlit; print('✓ Streamlit installed')"
python -c "import googlemaps; print('✓ Google Maps client installed')"
python -c "import requests; print('✓ Requests installed')"
```

All checks should print successfully.

---

## Configuration

Before first use, you must configure an API key for either Google Maps or HERE Maps.

### Option 1: Google Maps Setup

#### Step 1: Get API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. **Enable Billing** (required even for free tier)
4. Navigate to **APIs & Services → Library**
5. Search for **"Directions API"** and enable it
6. Go to **APIs & Services → Credentials**
7. Click **"Create Credentials" → "API Key"**
8. Copy your API key

#### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Map provider
MAPS_PROVIDER=google

# Your Google Maps API key
GOOGLE_MAPS_API_KEY=AIzaSyYourActualKeyHere

# Optional settings
APP_ENV=development
DEBUG=False
```

#### Google Pricing

- **Free tier:** $200 monthly credit (equivalent to ~40,000 requests)
- **Cost after free tier:** ~$5 per 1,000 requests
- **Directions API cost:** $5 per 1,000 requests (as of 2024)

### Option 2: HERE Maps Setup (Recommended)

#### Step 1: Get API Key

1. Go to [HERE Developer Portal](https://developer.here.com/)
2. Sign up for a free account
3. Create a new **Project**
4. Enable the **"Routing API"** (v8)
5. Go to project **Credentials**
6. Copy your **API Key**

#### Step 2: Configure Environment

Create `.env`:

```ini
# Map provider
MAPS_PROVIDER=here

# Your HERE API key
HERE_API_KEY=YOUR_HERE_API_KEY_HERE

# Optional settings
APP_ENV=development
DEBUG=False
```

#### HERE Pricing

- **Free tier:** 250,000 requests/month (no credit card required)
- **Pay-as-you-go:** ~$1-2 per 1,000 requests after free tier
- **Routing API cost:** Included in free tier

**Note:** HERE's free tier is significantly more generous than Google's.

### Choosing Your Provider

| Criteria | Google Maps | HERE Maps |
|----------|------------|-----------|
| **Free Tier** | $200 credit (~40K req) | 250,000 requests |
| **Cost** | ~$5/1K requests | ~$1-2/1K requests |
| **Global Coverage** | Excellent | Good (major cities) |
| **Transit Accuracy** | Industry leading | Very good |
| **Setup** | Requires billing | No billing required |
| **Best For** | Global enterprise | Cost-conscious projects |

**Recommendation:** Use **HERE Maps** for development and most use cases due to generous free tier. Use **Google Maps** only if you need the absolute best global coverage or advanced transit features.

### Switching Providers

To switch:

1. Edit `.env`:
   ```ini
   MAPS_PROVIDER=here  # or 'google'
   ```

2. Set the corresponding API key

3. Restart the app

The application will automatically use the new provider.

---

## Using the Application

### Starting the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

### Main Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🚇 Public Transport Route Finder                          │
├─────────────────────────────────────────────────────────────┤
│  [Sidebar]  │  [Main Content]                              │
│             │                                               │
│  • Provider │  From: [____________]                       │
│  • History  │  To:   [____________]                       │
│  • Filters  │                                               │
│             │  Departure: ○ Now ○ Arrive by ○ Custom      │
│             │                                               │
│             │  [ ] Include real-time traffic              │
│             │  Max routes: [3 ▼]                           │
│             │                                               │
│             │  [      Find Routes      ]                   │
├─────────────────────────────────────────────────────────────┤
│  Results appear here...                                    │
└─────────────────────────────────────────────────────────────┘
```

---

### Finding Routes

#### Basic Search

1. **Enter Origin:** Start location (address, landmark, city)
   - Example: `Times Square, New York`
   - Example: `Brandenburg Gate, Berlin`
   - Example: `Shibuya Station, Tokyo`

2. **Enter Destination:** End location
   - Example: `Central Park, New York`
   - Example: `Alexanderplatz, Berlin`

3. **Click "Find Routes"**

#### Tips for Better Results

✅ **DO:**
- Use specific addresses or well-known landmarks
- Include city/country for ambiguous names: `Paris, France` not just `Paris`
- Use commas to separate components: `123 Main St, City, Country`
- Test with major cities first to verify your setup

❌ **AVOID:**
- Single-word locations without context (`"London"` works, `"Springfield"` may not)
- Misspelled place names
- Locations too far apart (> 500 km may have limited transit)
- Purely residential areas with no transit

#### Example Routes That Work

- Times Square → Central Park, New York
- King's Cross Station → Tower Bridge, London
- Brandenburg Gate → Alexanderplatz, Berlin
- Shibuya Station → Tokyo Tower, Tokyo
- Eiffel Tower → Louvre Museum, Paris

---

### Viewing Results

After finding routes, you'll see:

```
Routes from [Origin] to [Destination]

[✓ Route 1 - Best Match]     ⭐ 4.2 (12 reviews)
Duration: 35 min              Transfers: 1
Distance: 8.2 km             Walking: 1.5 km

[Route 2 - Alternative]      ⭐ 3.8 (5 reviews)
Duration: 42 min              Transfers: 2
...

[Route 3 - Alternative]      ⭐ 3.5 (2 reviews)
...
```

---

### Route Details View

Click "View Details" on any route card to see:

1. **Summary Card**
   - Total duration, distance, number of transfers
   - Fare information (if available)
   - User rating and review count

2. **Step-by-Step Directions**
   ```
   Step 1: Walk 5 min (400 m) to Penn Station
   Step 2: Take A Train (Subway) 15 min, 6 stops → Times Square
   Step 3: Walk 3 min (250 m) to destination
   ```

3. **Transit Details**
   - Vehicle type (Bus, Subway, Train, Tram, etc.)
   - Line names and numbers
   - Departure/arrival stops
   - Platform information (if available)

4. **Interactive Map** (if implemented)

---

### Comparison Table

Switch to the **"📊 Comparison Table"** tab to see:

| Route | Duration | Transfers | Walking | Fare | Rating |
|-------|----------|-----------|---------|------|--------|
| 1 ⭐ | 35 min | 1 | 1.5 km | $2.75 | 4.2 ★ |
| 2 | 42 min | 2 | 0.8 km | $3.50 | 3.8 ★ |
| 3 | 48 min | 1 | 2.1 km | $2.75 | 3.5 ★ |

**Score** column shows the algorithm's ranking (0-100) based on your scoring weights.

---

### User Reviews

- **Rate routes** using the star system (1-5 stars)
- **Leave comments** with tips or caveats
- **Read others' reviews** to make informed choices
- Reviews are stored locally in `data/reviews.json`

---

## Advanced Features

### Departure/Arrival Time

Plan trips for specific times:

1. Select departure option:
   - **Now** - Immediate departure (default)
   - **Arrive by** - Set arrival time (limited support)
   - **Custom time** - Specific departure datetime

2. Click the date/time picker

3. Routes will be calculated for that time, considering:
   - Scheduled transit departures
   - Real-time traffic (if enabled)
   - Service schedules (some routes may not run at certain hours)

**Note:** Arrival time requires Google Maps with departure_time workaround; currently shows info message.

### Real-time Traffic

Enable **"Include real-time traffic"** to:

- Account for current traffic conditions
- Get more accurate duration estimates for driving legs
- See traffic-adjusted walking times

**Only available with Google Maps** (HERE Maps treats this differently)

### Route Scoring

Routes are automatically ranked using weighted factors:

```
Score = (Duration × 40%) + (Transfers × 30%) + (Walking × 30%)
```

**Lower is better** for duration and transfers; walking uses normalized distance.

To customize weights, edit `route_scorer.py`:

```python
SCORING_WEIGHTS = {
    'duration': 0.4,   # More weight = prefer faster routes
    'transfers': 0.3,  # More weight = prefer fewer transfers
    'walking': 0.3     # More weight = prefer less walking
}
```
Total must equal 1.0.

---

## Troubleshooting

### "No routes found"

**Possible causes:**

1. **Invalid locations**
   - ✓ Verify addresses are spelled correctly
   - ✓ Add city/state/country: `"Lagos"` → `"Lagos, Nigeria"`
   - ✓ Check that locations exist on Google Maps

2. **No public transit available**
   - Routes may not exist between your locations
   - Areas too far apart (> 200-300 km often have no direct transit)
   - Try a shorter distance within a city

3. **API provider lacks coverage**
   - Google Maps: Limited transit data in some countries (e.g., Nigeria)
   - HERE Maps: Better in some regions, worse in others
   - **Solution:** Switch providers via `.env`

**What to try:**
- Test with known-good route: `Times Square, NY` → `Central Park, NY`
- If that works, your API is working - the original locations just lack transit
- Switch to HERE Maps if using Google (or vice versa)

---

### API Key Errors

**"Invalid API key" / "API key not valid"**
- Check `.env` file for typos
- Ensure key is copied completely (no extra spaces)
- For Google: Create a **Server key** or **Browser key** (not Android/iOS)

**"You must enable Billing"**
- Google Maps requires billing even for free tier
- Go to Cloud Console → Billing → Link a billing account
- You won't be charged if you stay within $200 free credit

**"API key not authorized for Directions API"**
- Enable the correct API:
  - Google: **Directions API**
  - HERE: **Routing API**
- In Google Console: APIs & Services → Enable required APIs

**"over query limit" / quota exceeded**
- Check usage in provider dashboard
- For HERE: 250K/month free limit
- For Google: $200 credit limit
- Wait for quota reset or upgrade plan

---

### App Won't Start

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Python version error**
```bash
python --version  # Must be 3.8+
# Upgrade if needed: python -m pip install --upgrade python
```

**Port already in use**
```bash
# Kill existing Streamlit process
pkill -f streamlit
# Or use different port
streamlit run app.py --server.port 8502
```

---

### HERE-Specific Issues

**"HERE API HTTP error 403"**
- Make sure Routing API is enabled (not just other APIs)
- Check API key hasn't expired
- Verify project is active

**"No routes but Google works"**
- HERE coverage differs from Google
- Try a major city: London, Berlin, Tokyo, NYC
- Some countries have limited HERE transit data

---

## Project Architecture

```
routefinder/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration & environment settings
├── client_factory.py      # Factory pattern for provider selection
├── google_maps_client.py  # Google Maps API wrapper
├── here_client.py         # HERE Maps API wrapper
├── route_parser.py        # Parse API responses into Route objects
├── route_scorer.py        # Route ranking algorithm
├── route_models.py        # Data classes (Route, Step, TransitDetails)
├── storage.py             # Local JSON storage for reviews/favorites
├── ui_components.py       # Reusable Streamlit components
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── data/                 # Storage directory
    ├── reviews.json      # User reviews
    └── favorites.json    # Saved routes
```

### Data Flow

```
User Input
    ↓
ClientFactory → (GoogleMapsClient or HereClient)
    ↓
API Request → Google/HERE Directions API
    ↓
API Response
    ↓
RouteParser.parse_routes() → List[Route]
    ↓
RouteScorer.score_routes() → List[Route] (sorted)
    ↓
UI Rendering (app.py)
    ↓
User interaction → Storage.save_review()/save_favorite()
```

### Key Design Patterns

- **Factory Pattern:** `ClientFactory` creates appropriate client based on config
- **Adapter Pattern:** `HereClient._convert_to_google_format()` adapts HERE response to Google format
- **Separation of Concerns:** Each module has single responsibility
- **Dependency Injection:** API clients injected into storage/parser

---

## API Reference

### Config Class

```python
from config import Config

# Access configuration
provider = Config.MAPS_PROVIDER        # 'google' or 'here'
google_key = Config.GOOGLE_MAPS_API_KEY
here_key = Config.HERE_API_KEY
max_routes = Config.MAX_ROUTES         # Default: 5
weights = Config.SCORING_WEIGHTS       # Duration/transfers/walking weights

# Validate configuration
Config.validate()  # Raises ValueError if misconfigured
```

### RouteParser

```python
from route_parser import RouteParser

# Parse raw API response
routes = RouteParser.parse_routes(api_response)

# Returns: List[Route] with fields:
# - summary (str): Route name/ID
# - legs (List[Leg]): Journey segments
# - fare (Optional[Fare]): Cost information
# - score (float): Computed score (0-100)
# - rating (Optional[float]): User average rating
```

### RouteScorer

```python
from route_scorer import RouteScorer

# Score routes (normalizes and applies weights)
scored_routes = RouteScorer.score_routes(routes)

# Adjust weights (must sum to 1.0)
RouteScorer.set_weights(duration=0.5, transfers=0.3, walking=0.2)
```

### Storage

```python
from storage import Storage

storage = Storage()  # Auto-creates data/ directory

# Review management
storage.add_review(route_id="abc123", rating=5, comment="Great route!")
reviews = storage.get_reviews(route_id="abc123")
avg_rating = storage.get_average_rating(route_id="abc123")

# Favorites
storage.add_favorite(user_id="user1", route_id="abc123")
favorites = storage.get_favorites(user_id="user1")
```

---

## Frequently Asked Questions

**Q: Can I use this offline?**  
A: No. The app requires live API calls to Google Maps or HERE Maps to fetch transit data.

**Q: Why are some routes missing compared to Google Maps website?**  
A: The Directions API has some limitations compared to the consumer website. Also, we request transit mode only; some multimodal routes may be filtered differently.

**Q: How often is transit data updated?**  
A: Real-time depends on the transit agency feeding data to Google/HERE. Scheduled timetables are updated regularly (daily/weekly).

**Q: Can I add bicycle or walking-only routes?**  
A: Not currently. The app focuses on public transit. The code could be extended to support other modes.

**Q: Is my API usage tracked?**  
A: Only by Google/HERE in your respective developer console. The app does not track usage.

**Q: How do I add a new transit mode (e.g., ferries)?**  
A: Update `Config.DEFAULT_TRANSIT_MODE` or modify `app.py` to allow mode selection. Both APIs support ferries as part of transit.

**Q: Can I export routes to PDF or other formats?**  
A: Not yet built-in. Use browser print (Ctrl/Cmd+P) to save as PDF, or copy from the UI.

**Q: Why choose HERE over Google?**  
A: HERE offers 250K free requests/month vs Google's ~40K equivalent. HERE also has no billing requirement and sometimes better coverage in specific regions (Europe, parts of Asia/Africa).

**Q: My app shows "No routes" but Google Maps website shows routes. Why?**  
A: Possible reasons:
- API key lacks proper permissions
- Different API endpoints (Consumer Maps vs Directions API)
- Transit mode restrictions
- Try switching to HERE Maps

---

## Support & Contributing

### Getting Help

1. **Check this manual** - Most questions answered here
2. **Review code comments** - Inline documentation in source files
3. **Check logs** - Run with `DEBUG=True` in `.env` for verbose output
4. **Test with known-good routes** - Verify your API setup

### Reporting Issues

When reporting bugs, please include:

- **Provider:** Google or HERE
- **Locations tested:** Origin and destination
- **Expected vs actual behavior**
- **Error messages (full text)**
- **Screenshot** if UI issue
- **Relevant logs** (enable DEBUG=True)
- **API response** (if accessible)

Submit issues via GitHub Issues (if repository available) or to your development team.

### Contributing

We welcome contributions! Areas for improvement:

- [ ] Support for arrival_time parameter (currently limited)
- [ ] Interactive map visualization
- [ ] Export routes to GPX/JSON
- [ ] Multi-language support
- [ ] Accessibility improvements (WCAG compliance)
- [ ] Unit tests for route_scorer and route_parser
- [ ] More transit modes (bike share, scooter)
- [ ] User accounts and cloud sync

**How to contribute:**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Submit Pull Request with description

### License

MIT License - See LICENSE file for details.

---

## Appendix

### A. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAPS_PROVIDER` | Yes | `google` | Provider: `google` or `here` |
| `GOOGLE_MAPS_API_KEY` | If provider=google | - | Google API key |
| `HERE_API_KEY` | If provider=here | - | HERE API key |
| `APP_ENV` | No | `development` | Environment (development/production) |
| `DEBUG` | No | `False` | Enable debug logging (True/False) |
| `STORAGE_PATH` | No | `data/reviews.json` | Path to JSON storage |

### B. API Endpoints Used

**Google Maps:**
- `https://maps.googleapis.com/maps/api/directions/json`

**HERE Maps:**
- `https://router.hereapi.com/v8/routes`

### C. Transit Vehicle Types

Mapped from API responses:

| API Field | Display Name |
|-----------|--------------|
| `BUS` | Bus |
| `SUBWAY` | Subway/Metro |
| `RAIL` | Train/Rail |
| `TRAM` | Tram/Streetcar |
| `FERRY` | Ferry |
| `CABLE_CAR` | Cable Car |
| `GONDOLA` | Gondola/Lift |

### D. Timeout Configuration

- **API request timeout:** 30 seconds (hardcoded in `here_client.py`)
- Adjust if needed for slow connections or large cities

### E. Rate Limiting

- **No internal rate limiting** - Depends on your API quota
- Consider adding delay between requests if processing bulk queries
- Check provider dashboard for usage

---

**End of Manual**

*For updates and latest documentation, visit the project repository.*


