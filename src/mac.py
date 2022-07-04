from nmigen import *
from src.consts import *


class MAC(Elaboratable):
    def __init__(self):
        self.a = Signal(MEM_BUS_WIDTH + MAC_SIZE)

        self.a_valid = Signal()
        self.a_ready = Signal()

        self.b = Signal(MEM_BUS_WIDTH + MAC_SIZE)
        self.b_valid = Signal()
        self.b_ready = Signal()

        self.a_0 = Signal(9)
        self.a_1 = Signal(9)
        self.a_2 = Signal(9)
        self.a_3 = Signal(9)

        self.b_0 = Signal(9)
        self.b_1 = Signal(9)
        self.b_2 = Signal(9)
        self.b_3 = Signal(9)

        self.c_0 = Signal(9)
        self.c_1 = Signal(9)
        self.c_2 = Signal(9)
        self.c_3 = Signal(9)

        self.en = Signal()
        self.a_latched = Signal()
        self.b_latched = Signal()

        self.acc = Signal(MEM_BUS_WIDTH)
        self.acc_len = Signal(8)
        self.done = Signal()

    def elaborate(self, platform):
        m = Module()
        acc_count = Signal(8)
        dot_product = Signal(32)

        with m.If(self.en == 1):

            with m.If(self.a_valid):
                m.d.comb += self.a_ready.eq(0)
                m.d.comb += [
                    self.a_0.eq(self.a[0:9]),
                    self.a_1.eq(self.a[9:18]),
                    self.a_2.eq(self.a[18:27]),
                    self.a_3.eq(self.a[27:36]),
                    self.a_latched.eq(1),
                ]
            with m.If(self.b_valid):

                m.d.comb += self.b_ready.eq(0)
                m.d.comb += [
                    self.b_0.eq(self.b[0:9]),
                    self.b_1.eq(self.b[9:18]),
                    self.b_2.eq(self.b[18:27]),
                    self.b_3.eq(self.b[27:36]),
                    self.b_latched.eq(1),
                ]

            with m.If((self.a_latched == 1) & (self.b_latched == 1)):
                m.d.comb += [self.a_ready.eq(1), self.b_ready.eq(1)]
                m.d.comb += [
                    self.c_0.eq(self.a_0 * self.b_0),
                    self.c_1.eq(self.a_1 * self.b_1),
                    self.c_2.eq(self.a_2 * self.b_2),
                    self.c_3.eq(self.a_3 * self.b_3),
                    dot_product.eq(self.c_0 + self.c_1 + self.c_2 + self.c_3),
                ]
                with m.If(acc_count <= self.acc_len):
                    m.d.sync += [
                        acc_count.eq(acc_count + 1),
                        self.acc.eq(self.acc + dot_product),
                    ]
                    m.d.comb += self.done.eq(0)
                with m.Else():
                    m.d.comb += self.done.eq(1)
                    m.d.sync += [self.acc.eq(0), acc_count.eq(0)]

        with m.Else():
            m.d.sync += self.acc.eq(0)
        return m

    def ports(self):
        return [
            self.a,
            self.b,
            self.a_0,
            self.a_1,
            self.a_2,
            self.a_3,
            self.b_0,
            self.b_1,
            self.b_2,
            self.b_3,
        ]
