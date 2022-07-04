from amaranth import *
# from nmigen.back.pysim import Simulator, Delay, Settle, Tick
# from nmigen.sim.core import Tick

from amaranth.sim import Tick, Simulator, Delay, Settle


import sys
from pathlib import Path
import os

path = Path(__file__)
module_path = path.parent.absolute().parent.absolute()
sys.path.append(os.path.join(module_path, ""))

filename = os.path.splitext(__file__)[0].split("/")[-1]
vcd_file = os.path.join(module_path, "sim", "vcd_dump", filename + "_new.vcd")


from src.fc_layer import FCLayer
from src.consts import *

if __name__ == "__main__":

    m = Module()
    m.submodules.fc_layer = fc_layer = FCLayer()

    weight_addr = Signal(ADDR_WIDTH)
    input_addr = Signal(ADDR_WIDTH)
    output_addr = Signal(ADDR_WIDTH)
    neuron_count = Signal(8)
    synapses = Signal(8)

    m.d.comb += [
        fc_layer.weight_addr.eq(weight_addr),
        fc_layer.input_addr.eq(input_addr),
        fc_layer.output_addr.eq(output_addr),
        fc_layer.neuron_count.eq(neuron_count),
        fc_layer.synapses.eq(synapses),
    ]
    sim = Simulator(m)

    def process():
        total_data_to_read = 10
        start_addr = 0
        yield synapses.eq(5)
        yield neuron_count.eq(2)
        yield weight_addr.eq(0)
        yield input_addr.eq(0)
        yield output_addr.eq(0)

        for i in range(total_data_to_read + 5):
            yield Tick()

    sim.add_clock(1e-6)
    sim.add_process(process)
    with sim.write_vcd(vcd_file):  # traces=fc_layer.ports()):
        sim.run()
