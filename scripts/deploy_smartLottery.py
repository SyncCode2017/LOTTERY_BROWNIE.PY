from scripts.helpfulFunctions import getAccount, get_contract, fund_with_link
from brownie import smart_Lottery, network, config
import time


def deploy_smartLottery():
    account = getAccount()
    smartLottery = smart_Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed smartLottery!")
    return smartLottery


def start_smartLottery():
    account = getAccount()
    smartLottery = smart_Lottery[-1]
    starting_tx = smartLottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The smartLottery is started!")


def enter_smartLottery():
    account = getAccount()
    smartLottery = smart_Lottery[-1]
    value = smartLottery.getEntranceFee() + 100000000
    tx = smartLottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the smartLottery!")


def end_smartLottery():
    account = getAccount()
    smartLottery = smart_Lottery[-1]
    # fund the contract
    # then end the smartLottery
    tx = fund_with_link(smartLottery.address)
    tx.wait(1)
    ending_transaction = smartLottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(180)
    print(f"{smartLottery.recentWinner()} is the new winner!")


def main():
    deploy_smartLottery()
    start_smartLottery()
    enter_smartLottery()
    end_smartLottery()
