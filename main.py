import time
from classes.util import *
from classes.window import Window


if __name__ == "__main__":
    random.seed(time.time())

    window = Window()
    window.run()
