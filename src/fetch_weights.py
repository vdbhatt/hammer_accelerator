from nmigen import *
from src.weight_mem import WeightMemory
from src.consts import *


class FetchWeight(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.start_addr = Signal(ADDR_WIDTH)
        self.data = Signal(MEM_BUS_WIDTH + MAC_SIZE)
        self.length = Signal(8)
        self.counter = Signal(8)
        self.current_addr = Signal(ADDR_WIDTH)
        self.done = Signal()

        self.valid = Signal(reset=1)
        self.ready = Signal()
        self.en = Signal()
        self.offset = Signal(8)

    def ports(self):
        return [
            self.start_addr,
            self.data,
            self.length,
            self.counter,
            self.current_addr,
            self.done,
            self.valid,
            self.ready,
            self.en,
        ]

    def elaborate(self, platform=None):
        m = Module()
        m.submodules.mem = self.mem = WeightMemory()
        rst = ResetSignal()
        offset = Signal(8)

        with m.If((self.ready == 1)):
            with m.If((self.counter <= self.length)):
                m.d.sync += self.counter.eq(self.counter + 1)
                m.d.comb += [
                    self.current_addr.eq(self.offset + self.counter),
                    self.mem.adr.eq(self.current_addr),
                    self.mem.we.eq(0),
                    self.done.eq(0),
                    self.data.eq(
                        Cat(
                            self.mem.dat_r[0:8],
                            0,
                            self.mem.dat_r[8:16],
                            0,
                            self.mem.dat_r[16:24],
                            0,
                            self.mem.dat_r[24:32],
                            0,
                        )
                    ),
                    self.valid.eq(1),
                ]
            with m.Else():
                m.d.comb += [
                    self.done.eq(1),
                ]
                m.d.sync += [
                    self.counter.eq(0),
                    self.offset.eq(self.offset + self.length),
                ]

        return m
