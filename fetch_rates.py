import aiohttp
import asyncio
import aioredis
import xml.etree.ElementTree as ET

URL = 'https://www.cbr.ru/scripts/XML_daily.asp'
REDIS_HOST = 'redis'
REDIS_PORT = 6379

async def fetch_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            return await response.text()

async def parse_and_store_rates(xml_data):
    root = ET.fromstring(xml_data)
    redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT))

    for currency in root.findall('Valute'):
        char_code = currency.find('CharCode').text
        value = float(currency.find('Value').text.replace(',', '.'))
        await redis.set(char_code, value)

    await redis.close()

async def main():
    xml_data = await fetch_rates()
    await parse_and_store_rates(xml_data)

if __name__ == '__main__':
    asyncio.run(main())
