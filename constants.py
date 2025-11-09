# API Configuration
GRAPH_API_VERSION = "v24.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/ads_archive"

# Default Settings
DEFAULT_COUNTRY = "DZ"
DEFAULT_LIMIT = 10

# API Fields
API_FIELDS = (
    "id,"
    "ad_creation_time,"
    "ad_creative_bodies,"
    "ad_creative_link_titles,"
    "ad_creative_link_descriptions,"
    "page_name,"
    "ad_snapshot_url,"
    "ad_reached_countries"
)