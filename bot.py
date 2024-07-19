import asyncio
import aioredis
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = '7254556474:AAEJxxb75xXxiBx-rfPOoBnYFj7sqV6ztCw'
REDIS_HOST = 'redis'
REDIS_PORT = 6379

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def get_rate(currency: str):
    redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT))
    rate = await redis.get(currency)
    await redis.close()
    return float(rate) if rate else None


@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    try:
        _, from_currency, to_currency, amount = message.text.split()
        amount = float(amount)
        from_rate = await get_rate(from_currency)
        to_rate = await get_rate(to_currency)

        if from_rate and to_rate:
            result = (amount * from_rate) / to_rate
            await message.reply(f"{amount} {from_currency} = {result:.2f} {to_currency}")
        else:
            await message.reply("Невозможно получить курс для одной из валют.")
    except Exception as e:
        await message.reply("Неверный формат команды. Используйте: /exchange USD RUB 10")


@dp.message_handler(commands=['rates'])
async def rates(message: types.Message):
    redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT))
    keys = await redis.keys('*')
    rates = await redis.mget(*keys)
    await redis.close()

    response = "\n".join([f"{key.decode('utf-8')}: {rate.decode('utf-8')}" for key, rate in zip(keys, rates)])
    await message.reply(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
