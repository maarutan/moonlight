import asyncio


class SmoothTurn:
    def __init__(
        self,
        delay: float = 0.3,
        stop_step: int = 5,
        function_st=lambda: None,
    ):
        self.delay = delay
        self.counter = 0
        self.stop_step = stop_step
        self.running = True
        self.function_st = function_st

    async def run(self):
        while self.running and self.counter < self.stop_step:
            self.function_st()
            await asyncio.sleep(self.delay)
            self.counter += 1

    def stop(self):
        self.running = False


# def volume_handler():
#     print("hello")
#
#
# #
# st = SmoothTurn(
#     delay=0.1,
#     stop_step=5,
#     function_st=volume_handler,
# )
#
# asyncio.run(st.run())
