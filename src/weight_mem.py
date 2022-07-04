from src.consts import *
from nmigen import *


class WeightMemory(Elaboratable):
    def __init__(self):
        self.adr = Signal(ADDR_WIDTH)
        self.dat_r = Signal(MEM_BUS_WIDTH)
        self.dat_w = Signal(MEM_BUS_WIDTH)
        self.we = Signal()
        x = [i << 24 | i << 16 | i << 8 | i for i in range(100)]
        # TODO: change this to load the trained weights
        self.mem = Memory(width=MEM_BUS_WIDTH, depth=len(x), init=x)

    def elaborate(self, platform):
        m = Module()
        m.submodules.rdport = rdport = self.mem.read_port()
        m.submodules.wrport = wrport = self.mem.write_port()
        m.d.comb += [
            rdport.addr.eq(self.adr),
            self.dat_r.eq(rdport.data),
            wrport.addr.eq(self.adr),
            wrport.data.eq(self.dat_w),
            wrport.en.eq(self.we),
        ]
        return m

    def ports(self):
        return [self.adr, self.dat_r, self.dat_w, self.we]
