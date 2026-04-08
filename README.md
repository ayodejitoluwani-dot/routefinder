# Public Transport Route Finder

A Streamlit app that finds the best public transport routes between two points. **Supports both Google Maps and HERE Maps APIs.**

## Features

- Find multiple route options between any two locations
- Compare routes by duration, walking distance, and transfers
- Step-by-step transit directions with vehicle types and stops
- User reviews and ratings for routes
- Real-time traffic consideration (optional)
- Clean, responsive interface
- **Multi-provider support** (Google Maps or HERE Maps)

## Choose Your Map Provider

| Feature | Google Maps | HERE Maps |
|---------|-------------|-----------|
| Free tier | $200 credit/month | 250,000 requests/month |
| Pricing after free | ~$5 per 1000 requests | ~$1-2 per 1000 requests |
| Transit coverage | Excellent (global) | Good (major cities) |
| Billing required | Yes | Yes |
| Signup | cloud.google.com | developer.here.com |

**Recommendation:** Use **HERE Maps** for generous free tier and lower costs. Use **Google Maps** for best global transit coverage.

## Setup

### Prerequisites

- Python 3.8+
- API key from either Google Maps or HERE (see setup instructions below)

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and configure your provider (see sections below)
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Google Maps API Setup (Option 1)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. **Enable billing** for your project (required even for free tier)
4. Enable the **Directions API**
5. Go to "Credentials" and create an API key
6. Add the API key to your `.env` file:
   ```
   MAPS_PROVIDER=google
   GOOGLE_MAPS_API_KEY=your_google_api_key_here
   ```
7. Restart the app

## HERE API Setup (Option 2) - Recommended

1. Go to [HERE Developer Portal](https://developer.here.com/)
2. Sign up for a free account
3. Create a new project
4. Enable the **Routing API**
5. Get your API key from the project credentials
6. Add the API key to your `.env` file:
   ```
   MAPS_PROVIDER=here
   HERE_API_KEY=your_here_api_key_here
   ```
7. Remove or comment out `GOOGLE_MAPS_API_KEY` if not using Google
8. Restart the app

**Note:** HERE offers 250,000 free requests per month, which is much more generous than Google's $200 credit (equivalent to ~40,000 requests).

## Usage

1. Enter your origin and destination (addresses, landmarks, or coordinates)
2. Adjust optional settings:
   - Departure time (now, arrival by, or custom)
   - Include real-time traffic
   - Maximum number of routes to show
3. Click "Find Routes"
4. Browse results in the "Route Details" or "Comparison Table" tabs
5. Rate routes and read reviews from other users

## Project Structure

```
├── app.py                 # Main Streamlit application
├── config.py              # Configuration and API settings
├── client_factory.py      # Factory for creating API clients
├── google_maps_client.py  # Google Maps API wrapper
├── here_client.py         # HERE Maps API wrapper
├── route_models.py        # Data classes (Route, Step)
├── route_parser.py        # API response parser
├── route_scorer.py        # Route ranking algorithm
├── storage.py             # User reviews and favorites storage
├── ui_components.py       # Reusable UI components
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
├── data/                 # JSON storage directory
└── README.md             # This file
```

## Switching Providers

To switch between Google Maps and HERE Maps:

1. Edit your `.env` file
2. Change `MAPS_PROVIDER=google` to `MAPS_PROVIDER=here` (or vice versa)
3. Make sure the corresponding API key is set
4. Restart the app

The app will automatically use the configured provider on next start.

## HERE API Notes

### Transit Coverage
HERE provides public transport data for major cities worldwide. Coverage may be slightly different from Google - some cities have better coverage in HERE, others in Google.

### Rate Limits
- 250,000 free requests per month
- Burst limits apply (usually 10-50 requests/second)
- For development/testing, you won't hit limits

### Known Limitations
- HERE uses different transit line names compared to Google
- Real-time traffic estimates may vary slightly
- Some advanced features (like accessibility preferences) not yet implemented for HERE

### Differences from Google
- HERE API returns routes with "sections" instead of "steps"
- Fare information may be less detailed
- Transit vehicle types mapped differently (BUS, SUBWAY, RAIL)

All these differences are handled by the converter layer, so the UI remains identical.

## Optional Features

### Real-time Traffic
Enable the "Include real-time traffic" checkbox to get more accurate duration estimates based on current traffic conditions. Requires the Directions API with traffic model support.

### User Reviews
Rate routes and leave comments. Reviews are stored locally in `data/reviews.json` and help others choose the best routes. Average ratings are displayed on each route card.

### Route Scoring
Routes are automatically ranked based on:
- Total duration (40%)
- Number of transfers (30%)
- Walking distance (30%)

These weights can be customized in `route_scorer.py`.

## Troubleshooting

### General Issues

**No routes found:**
- Check that both origin and destination are valid addresses or landmarks
- Verify that public transit exists between these locations
- Try different cities (some smaller towns have no transit data)
- Ensure your API key has the correct API enabled (Directions API for Google, Routing API for HERE)

**API key errors:**
- Double-check the API key in `.env`
- Verify the API key isn't restricted or expired
- For Google: Check billing is enabled
- For HERE: Ensure the Routing API is enabled in your project

**App crashes on start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.8 or higher
- Verify `.env` file exists and is properly formatted

### HERE-Specific Issues

**"HERE API HTTP error 403":**
- Make sure you enabled the **Routing API** in your HERE project (not just other APIs)
- Check your API key hasn't expired or been revoked

**"HERE API error: Invalid credentials":**
- Your API key is incorrect or missing
- Double-check the `HERE_API_KEY` in your `.env` file

**No routes with HERE but Google works:**
- HERE may not have transit data for that specific city
- Try a major city like New York, London, Berlin, Tokyo

### Google-Specific Issues

**"You must enable Billing":**
- Google requires a billing account even for the $200 free credit
- Go to Cloud Console → Billing → Link billing account
- See "Google Maps API Setup" section above

**"API key not valid":**
- Make sure you're using a **Browser key** or **Server key** (not Android/iOS keys)
- Add no restrictions for testing, or add localhost restrictions

## Testing Your Setup

After configuration, test with these known-good routes:

- **New York:** Times Square → Central Park
- **London:** King's Cross Station → Tower Bridge
- **Berlin:** Brandenburg Gate → Alexanderplatz
- **Tokyo:** Shibuya Station → Tokyo Tower

If routes display correctly, your setup is working!

## Comparing Providers

Run the same route on both providers to compare:
1. Set `MAPS_PROVIDER=google`, run, note route details
2. Set `MAPS_PROVIDER=here`, restart, run same route
3. Compare: number of options, accuracy, speed, cost estimate

This helps you decide which provider works best for your location.

## License

MIT

## Contributing

Feel free to open issues or submit pull requests with improvements!
