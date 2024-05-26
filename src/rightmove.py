import asyncio
import json
from httpx import AsyncClient, Response
from parsel import Selector
from typing import TypedDict
import jmespath
import asyncio
import json
from typing import TypedDict
from urllib.parse import urlencode
from src.log import logger

log = logger.get(__name__)


class Property(TypedDict):
    id: str
    available: bool
    archived: bool
    phone: str
    url: str
    bedrooms: int
    bathrooms: int
    type: str
    property_type: str
    tags: list
    description: str
    title: str
    subtitle: str
    price: str
    price_sqft: str
    address: dict
    latitude: float
    longitude: float
    features: list
    history: dict
    photos: list
    floorplans: list
    agency: dict
    industryAffiliations: list
    nearest_airports: list
    nearest_stations: list
    sizings: list
    brochures: list


class RightMoveAPI:
    """Scrape Rightmove property URLS returning a Property object or from the API returning

    find_locations - find location ids from a string location (eg 'manchester')
    scrape_search - scrape all properties given a location id
    scrape_urls - scrape all properties from a list of property urls
    """

    parse_map = {
        "search": {
            "id": "id",
            "available": None,
            "archived": None,
            "phone": None,
            "url": "propertyUrl",
            "bedrooms": "bedrooms",
            "bathrooms": "bathrooms",
            "type": "transactionType",
            "property_type": "propertySubType",
            "tags": "tags",
            "description": "summary",
            "title": None,
            "subtitle": None,
            "price": "price.amount",
            "price_sqft": None,
            "address": "displayAddress",
            "latitude": "location.latitude",
            "longitude": "location.longitude",
            "features": None,
            "history": None,
            "photos": "propertyImages.images[*].{url: srcUrl, caption: caption}",
            "floorplans": "floorplans[*].{url: url, caption: caption}",
            "agency": """customer.{
                id: branchId, 
                branch: branchName, 
                company: companyName, 
                address: displayAddress, 
                commercial: commercial, 
                buildToRent: buildToRent,
                isNew: isNewHomeDeveloper
            }""",
            "industryAffiliations": None,
            "nearest_airports": None,
            "nearest_stations": None,
            "sizings": None,
            "brochures": None,
        },
        "url": {
            "id": "id",
            "available": "status.published",
            "archived": "status.archived",
            "phone": "contactInfo.telephoneNumbers.localNumber",
            "bedrooms": "bedrooms",
            "bathrooms": "bathrooms",
            "type": "transactionType",
            "property_type": "propertySubType",
            "tags": "tags",
            "description": "text.description",
            "title": "text.pageTitle",
            "subtitle": "text.propertyPhrase",
            "price": "prices.primaryPrice",
            "price_sqft": "prices.pricePerSqFt",
            "address": "address",
            "latitude": "location.latitude",
            "longitude": "location.longitude",
            "features": "keyFeatures",
            "history": "listingHistory",
            "photos": "images[*].{url: url, caption: caption}",
            "floorplans": "floorplans[*].{url: url, caption: caption}",
            "agency": """customer.{
                id: branchId, 
                branch: branchName, 
                company: companyName, 
                address: displayAddress, 
                commercial: commercial, 
                buildToRent: buildToRent,
                isNew: isNewHomeDeveloper
            }""",
            "industryAffiliations": "industryAffiliations[*].name",
            "nearest_airports": "nearestAirports[*].{name: name, distance: distance}",
            "nearest_stations": "nearestStations[*].{name: name, distance: distance}",
            "sizings": "sizings[*].{unit: unit, min: minimumSize, max: maximumSize}",
            "brochures": "brochures",
        },
    }

    def __init__(self):
        self._client = None

    def find_locations(self, location: str) -> list[str]:
        """find location ids from a string location (eg 'manchester')"""
        return asyncio.run(self._find_locations(location))

    def scrape_search(self, location_id: str) -> list[Property]:
        """scrape all properties in the location"""
        return asyncio.run(self._scrape_search(location_id))

    def scrape_urls(self, urls: list[str]) -> list[Property]:
        """scrape from property urls"""
        return asyncio.run(self._scrape_urls(urls))

    @property
    def client(self) -> AsyncClient:
        """HTTP client with browser-like headers"""
        if self._client is None:
            self._client = self._get_client()
        return self._client

    def _get_client(self) -> AsyncClient:
        """get HTTP client with browser-like headers to avoid being blocked"""
        return AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
            },
            follow_redirects=True,
            http2=True,  # enable http2 to reduce block chance
            timeout=30,
        )

    @staticmethod
    def _parse_property(data: dict, parse_map: dict) -> Property:
        """parse rightmove cache data for property information (field name to JMESPath mapping)"""
        results = {}
        for key, path in parse_map.items():
            if path is None or path == "":
                results[key] = None
            else:
                value = jmespath.search(path, data)
                results[key] = value
        return Property(**results)

    @staticmethod
    def _extract_property(response: Response) -> dict:
        """extract property data from rightmove PAGE_MODEL javascript variable"""
        selector = Selector(response.text)
        data = selector.xpath("//script[contains(.,'PAGE_MODEL = ')]/text()").get()
        if not data:
            print(f"page {response.url} is not a property listing page")
            return
        data = data.split("PAGE_MODEL = ", 1)[1].strip()
        data = json.loads(data)
        return data["propertyData"]

    @staticmethod
    def tokenise(location: str) -> str:
        """rightmove uses two character long tokens so 'manchester' becomes 'MA/NC/ES/TE/R'"""
        return "".join(
            c + ("/" if i % 2 == 0 else "")
            for i, c in enumerate(location.upper(), start=1)
        )

    async def _find_locations(self, location: str) -> list[str]:
        """async use rightmove's typeahead api to find location IDs. Returns list of location IDs in most likely order"""
        log.info(f"Finding rightmove location ids for {location}")
        tokenised_query = self.tokenise(location)
        url = f"https://www.rightmove.co.uk/typeAhead/uknostreet/{tokenised_query.strip('/')}/"
        response = await self.client.get(url)
        data = json.loads(response.text)
        location_ids = [
            prediction["locationIdentifier"]
            for prediction in data["typeAheadLocations"]
        ]
        log.info(f"Found {len(location_ids)} location ids")
        return location_ids

    async def _scrape_search(self, location_id: str) -> list[Property]:
        """async scrape all properties in the location"""
        log.info(f"scraping all properties in location id {location_id}")
        RESULTS_PER_PAGE = 24

        def make_url(offset: int) -> str:
            url = "https://www.rightmove.co.uk/api/_search?"
            params = {
                "areaSizeUnit": "sqft",
                "channel": "BUY",  # BUY or RENT
                "currencyCode": "GBP",
                "includeSSTC": "false",
                "index": offset,  # page offset
                "isFetching": "false",
                "locationIdentifier": location_id,  # e.g.: "REGION^61294",
                "numberOfPropertiesPerPage": RESULTS_PER_PAGE,
                "radius": "3.0",  # unit miles
                "sortType": "6",
                "viewType": "LIST",
                "maxPrice": 250000,
            }
            return url + urlencode(params)

        first_page = await self.client.get(make_url(0))
        first_page_data = json.loads(first_page.content)
        total_results = int(first_page_data["resultCount"].replace(",", ""))
        results = first_page_data["properties"]

        other_pages = []
        # rightmove sets the API limit to 1000 properties
        max_api_results = 1000
        for offset in range(RESULTS_PER_PAGE, total_results, RESULTS_PER_PAGE):
            if offset >= max_api_results:
                break
            other_pages.append(self.client.get(make_url(offset)))
        for response in asyncio.as_completed(other_pages):
            response = await response
            data = json.loads(response.text)
            properties = [
                self._parse_property(p, parse_map=self.parse_map["search"])
                for p in data["properties"]
            ]
            results.extend(properties)
        log.info(f"found {len(results)} properties")
        return results

    async def _scrape_urls(self, urls: list[str]) -> list[Property]:
        """async scrape from property urls"""
        log.info(f"scraping properties from {len(urls)} urls ")
        to_scrape = [self.client.get(url) for url in urls]
        properties = []
        for response in asyncio.as_completed(to_scrape):
            response = await response
            properties.append(
                self._parse_property(
                    self._extract_property(response), parse_map=self.parse_map["url"]
                )
            )
        return properties
