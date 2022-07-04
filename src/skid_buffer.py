from nmigen import *


class SkidBuffer(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.i_data = Signal(32)
        self.i_valid = Signal()
        self.o_ready = Signal()

        self.o_data = Signal(32)
        self.o_valid = Signal()
        self.i_ready = Signal()

    def elaborate(self, platform=None):
        m = Module()
        reset = ResetSignal()
        r_valid = Signal(reset=0)
        r_data = Signal(32, reset=0)

        with m.If(
            ((self.i_valid == 1) & (self.o_ready == 1))
            & ((self.o_valid == 1) & (self.i_ready == 0))
        ):
            m.d.sync += r_valid.eq(1)
        with m.Elif(self.i_ready == 1):
            m.d.sync += r_valid.eq(0)
        with m.If((self.o_ready == 1) & (self.i_valid == 1)):
            m.d.sync += r_data.eq(self.i_data)

        m.d.comb += self.o_ready.eq(r_valid == 0)

        m.d.comb += self.o_valid.eq(
            (reset == 0) & ((self.i_valid == 1) | (r_valid == 1))
        )
        with m.If(r_valid == 1):
            m.d.comb += self.o_data.eq(r_data)
        with m.Elif(self.i_valid == 1):
            m.d.comb += self.o_data.eq(self.i_data)
        with m.Else():
            m.d.comb += self.o_data.eq(0)
        return m
