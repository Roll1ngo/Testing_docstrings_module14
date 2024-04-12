import asyncio


def add(a, b):
    return a + b


def sub(a, b):
    c = a - b
    if c < 0:
        raise ValueError("Negative number")


def mul(a, b):
    return a * b


def div(a, b):
    if b == 0:
        raise ZeroDivisionError("second argument can`t be 0")
    return a / b


async def async_add(a, b):
    await asyncio.sleep(1)
    return a + b
