# Oct/09 - MS
from OpenOrange import *

ParentWallet = SuperClass("Wallet","Master",__file__)
class Wallet(ParentWallet):
    buffer = RecordBuffer("Wallet")