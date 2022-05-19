from django.utils.translation import gettext as _

# Create choice lists to be called into models, views, etc...

ZILLOW_DEEPSEARCH = "Zillow GetDeepSearch"
BRIDGE_ZESTIMATE = "Bridge Zestimate"
BRIDGE_PUBASSESS = "Bridge Public Assessment"
GREATSCHOOLS = "Great Schools"
FEMA = "FEMA Natural Disastors"
GOOGLEMAPS = "Google Maps"
CENSUSBUREAU2019 = "US Census Bureau 2019"

API_PROVIDER = (
        (ZILLOW_DEEPSEARCH, _("Zillow GetDeepSearch")),
        (BRIDGE_ZESTIMATE, _("Bridge Zestimate")),
        (BRIDGE_PUBASSESS, _("Bridge Public Assessment")),
        (GREATSCHOOLS, _("Great Schools")),
        (FEMA, _("Femal Natural Disastors")),
        (GOOGLEMAPS, _("Google Maps")),
        (CENSUSBUREAU2019, _("US Census Bureau 2019")),
        )