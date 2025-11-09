# ADSpy - Facebook Ad Library Scraper

A Python tool to fetch and analyze ads from the Facebook Ad Library API.

## Features

- Fetch ads based on keywords and country
- Export results to JSON and CSV formats
- Command line interface support
- Rate limiting and error handling
- Automatic pagination support

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ADSpy.git
cd ADSpy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Facebook API token:
```
ACCESS_TOKEN=your_access_token_here
```

## Usage

```bash
python app.py --country US --keyword "shoes" --limit 10
```

### Arguments:
- `--country`: Target country code (e.g., US, DZ)
- `--keyword`: Search keyword
- `--limit`: Number of ads to fetch per request (max 100)

## Output

Results are saved in the `results` directory in both JSON and CSV formats.