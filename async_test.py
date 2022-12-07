import asyncio


async def async_func():
    task = asyncio.create_task(async_func_2())
    print("A")
    await asyncio.sleep(5)
    print("B")
    return_value = await task
    print(f'Value was: {return_value}')


async def async_func_2():
    print("1")
    await asyncio.sleep(2)
    print("2")
    return 10


asyncio.run(async_func())
