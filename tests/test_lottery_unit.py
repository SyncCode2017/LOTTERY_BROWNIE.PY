import py
from scripts.helpfulFunctions import (
    LOCAL_BLOCKCHAIN,
    getAccount,
    fund_with_link,
    get_contract,
)
from brownie import smart_Lottery, accounts, config, network, exceptions
from scripts.deploy_smartLottery import deploy_smartLottery
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN:
        pytest.skip()
    # Arrange
    smartLottery = deploy_smartLottery()
    # Act
    # if eth = 2000usd, and usdEntryFee is 50usd
    # then EntryFee = 50/2000 = 0.025 eth
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = smartLottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # testing to ensure only when the smartLottery is open that people can enter
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN:
        pytest.skip()
    smartLottery = deploy_smartLottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        smartLottery.enter(
            {"from": getAccount(), "value": smartLottery.getEntranceFee()}
        )


def test_can_start_and_enter_smartLottery():
    # testing to ensure only when the smartLottery is open that pple can enter
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN:
        pytest.skip()
    smartLottery = deploy_smartLottery()
    account = getAccount()
    smartLottery.startLottery({"from": account})
    # Act
    smartLottery.enter({"from": account, "value": smartLottery.getEntranceFee()})
    # Assert
    assert smartLottery.players(0) == account


def test_can_end_smartLottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN:
        pytest.skip()
    smartLottery = deploy_smartLottery()
    account = getAccount()
    smartLottery.startLottery({"from": account})
    smartLottery.enter({"from": account, "value": smartLottery.getEntranceFee()})
    fund_with_link(smartLottery)
    # Act
    smartLottery.endLottery({"from": account})
    # Assert
    smartLottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN:
        pytest.skip()
    smartLottery = deploy_smartLottery()
    account = getAccount()
    smartLottery.startLottery({"from": account})
    smartLottery.enter({"from": account, "value": smartLottery.getEntranceFee()})
    smartLottery.enter(
        {"from": getAccount(index=1), "value": smartLottery.getEntranceFee()}
    )
    smartLottery.enter(
        {"from": getAccount(index=2), "value": smartLottery.getEntranceFee()}
    )
    fund_with_link(smartLottery)
    transaction = smartLottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777

    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, smartLottery.address, ({"from": account})
    )
    starting_balance_of_account = account.balance()
    balance_of_smartLottery = smartLottery.balance()
    # 777 % 3 = 0
    # Assert
    assert smartLottery.recentWinner() == account
    assert smartLottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_smartLottery
