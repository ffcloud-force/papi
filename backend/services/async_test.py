import asyncio
import time


async def brew_coffee():
    print("Brewing coffee...")
    await asyncio.sleep(2)
    print("Coffee brewed!")
    return "Coffee"


async def toast_bread():
    print("Toasting bread...")
    await asyncio.sleep(3)
    print("Bread toasted!")


async def main():
    # check the time it takes to run both functions
    start_time = time.time()
    await asyncio.gather(brew_coffee(), toast_bread())
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")


if __name__ == "__main__":
    asyncio.run(main())
