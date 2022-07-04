from nmigen import *

import sys
from pathlib import Path
import os

path = Path(__file__)
module_path = path.parent.absolute()
sys.path.append(os.path.join(module_path, ""))

from src.fetch_activation import FetchActivation
from src.fetch_weights import FetchWeight
from src.mac import MAC
from src.skid_buffer import SkidBuffer

from src.consts import *


class FCLayer(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.weight_addr = Signal(ADDR_WIDTH)
        self.input_addr = Signal(ADDR_WIDTH)
        self.output_addr = Signal(ADDR_WIDTH)
        self.neuron_count = Signal(8)
        self.synapses = Signal(8)
        self.done = Signal()

    def ports(self):
        return [
            self.weight_addr,
            self.input_addr,
            self.output_addr,
            self.neuron_count,
            self.synapses,
            self.done,
        ]

    def elaborate(self, platform=None):
        m = Module()
        acc = Signal(32)
        weight_done = Signal()
        act_done = Signal()
        synapses_done = Signal()
        w_en = Signal()
        a_en = Signal()

        m.submodules.fetch_weight = fetch_weight = FetchWeight()
        m.submodules.fetch_act = fetch_act = FetchActivation()
        m.submodules.weight_sb = weight_sb = SkidBuffer()
        m.submodules.act_sb = act_sb = SkidBuffer()
        m.submodules.mac = mac = MAC()

        m.d.comb += [
            # weight fetch unit
            w_en.eq(1),
            a_en.eq(1),
            mac.en.eq(1),
            fetch_weight.start_addr.eq(self.weight_addr),
            fetch_weight.length.eq(self.synapses),
            weight_done.eq(fetch_weight.done),
            fetch_weight.en.eq(w_en),
            # -- fetch_weight ==> skid_buffer
            fetch_weight.ready.eq(weight_sb.o_ready),
            weight_sb.i_data.eq(fetch_weight.data),
            weight_sb.i_valid.eq(fetch_weight.valid),
            # connect activation fetch unit
            fetch_act.start_addr.eq(self.input_addr),
            fetch_act.length.eq(self.synapses),
            act_done.eq(fetch_act.done),
            fetch_act.en.eq(a_en),
            # -- fetch_act ==> skid_buffer
            fetch_act.ready.eq(act_sb.o_ready),
            act_sb.i_data.eq(fetch_act.data),
            act_sb.i_valid.eq(fetch_act.valid),
            # weight_sb <==> MAC
            mac.a.eq(weight_sb.o_data),
            mac.a_valid.eq(weight_sb.o_valid),
            weight_sb.i_ready.eq(mac.a_ready),
            # act_sb <==> MAC
            mac.b.eq(act_sb.o_data),
            mac.b_valid.eq(act_sb.o_valid),
            act_sb.i_ready.eq(mac.b_ready),
            mac.en.eq(1),
            mac.acc_len.eq(self.synapses),
            acc.eq(mac.acc),
        ]

        with m.If(synapses_done <= self.synapses):
            m.d.sync += [
                synapses_done.eq(synapses_done + 1),
            ]
        return m
