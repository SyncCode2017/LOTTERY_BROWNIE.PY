from brownie import network
from scripts.deploy_smartLottery import deploy_smartLottery
from scripts.helpfulFunctions import (
    LOCAL_BLOCKCHAIN,
    getAccount,
    fund_with_link,
)
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN:
        pytest.skip()
    smartLottery = deploy_smartLottery()
    account = getAccount()
    smartLottery.startLottery({"from": account})
    smartLottery.enter({"from": account, "value": smartLottery.getEntranceFee()})
    smartLottery.enter({"from": account, "value": smartLottery.getEntranceFee()})
    fund_with_link(smartLottery)
    smartLottery.endLottery({"from": account})
    time.sleep(60)
    assert smartLottery.recentWinner() == account
    assert smartLottery.balance() == 0
