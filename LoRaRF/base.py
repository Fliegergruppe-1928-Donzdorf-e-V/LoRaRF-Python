import spidev
import gpiod
from gpiod.line import Direction, Value, Edge
from typing import Iterable
import time


class LoRaSpi():

    SPI_SPEED = 8000000

    def __init__(self, bus: int, device: int, speed: int = SPI_SPEED):
        self.bus = bus
        self.cs = device
        self.speed = speed

    def transfer(self, buf: Iterable) -> tuple:
        spi = spidev.SpiDev()
        spi.open(self.bus, self.cs)
        spi.lsbfirst = False
        spi.mode = 0
        spi.max_speed_hz = self.speed
        ret = spi.xfer2(buf)
        spi.close()
        return ret



class LoRaGpio:

    LOW = Value.INACTIVE
    HIGH = Value.ACTIVE

    def __init__(self, chip: int, offset: int):
        self.chip = "/dev/gpiochip" + str(chip)
        self.offset = offset
        self.seqno = 0

    def output(self, value: Value):
        self.request.set_value(self.offset, value)

    def input(self):
        return self.request.get_value(self.offset)

    def monitor(self, callback, timeout: float):
        t = time.time()        
        while (time.time() - t) < timeout or timeout == 0:
            for event in self.request.read_edge_events():
                if event.line_seqno != self.seqno:
                    self.seqno = event.line_seqno
                    callback()
                    return

class LoRaGpioOut(LoRaGpio):

    def __enter__(self):
        print(f"enter |{self.chip} {self.offset}")
        self.request = gpiod.request_lines(
            self.chip,
            consumer="LoRaGpioOut",
            config={self.offset: gpiod.LineSettings(direction=Direction.OUTPUT)}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"exit |{self.chip} {self.offset}")
        self.request.release()
    def blubb():
        print("blugg")

class LoRaGpioIn(LoRaGpio):

    def __enter__(self):
        self.request = gpiod.request_lines(
            self.chip,
            consumer="LoRaGpioOut",
            config={self.offset: gpiod.LineSettings(direction=Direction.INPUT)}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.request.release()

class LoRaGpioIrq(LoRaGpio):
    def __enter__(self):
        self.request = gpiod.request_lines(
            self.chip,
            consumer="LoRaGpioOut",
            config={self.offset: gpiod.LineSettings(edge_detection=Edge.RISING)}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.request.release()

class BaseLoRa :

    def begin(self):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def beginPacket(self):
        raise NotImplementedError

    def endPacket(self, timeout: int)-> bool:
        raise NotImplementedError

    def write(self, data, length: int):
        raise NotImplementedError

    def request(self, timeout: int)-> bool:
        raise NotImplementedError

    def available(self):
        raise NotImplementedError

    def read(self, length: int):
        raise NotImplementedError

    def wait(self, timeout: int)-> bool:
        raise NotImplementedError

    def status(self):
        raise NotImplementedError
