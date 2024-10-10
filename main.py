from jsplab.core import Simulator


if __name__ == "__main__":
    sim:Simulator=Simulator()
    sim.put_job()
    sim.play()