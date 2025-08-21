import unittest
import sys
import logger

log = logger.Logger().logger
#logger.level = logging.DEBUG

class TestCase(unittest.TestCase):
    def testSimpleMsg(self):
        stream_handler = logger.logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
        try:
            print("AA")
            #logging.getLogger().info("BB")
        finally:
            logger.removeHandler(stream_handler)

if __name__ == '__main__':
    unittest.main()