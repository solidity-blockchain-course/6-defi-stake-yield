from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    MockWETH,
    MockDAI,
    Contract,
    MockV3AggregatorETH,
    MockV3AggregatorDAI,
)
from web3 import Web3

ETH_INITIAL_PRICE_FEED_VALUE = 4000 * 10 ** 18
DAI_INITIAL_PRICE_FEED_VALUE = 1 * 10 ** 18
DECIMALS = 18

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

contract_to_mock = {
    "eth_usd_price_feed": MockV3AggregatorETH,
    "dai_usd_price_feed": MockV3AggregatorDAI,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it

        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
            )
    return contract


def get_verify_status():
    verify = (
        config["networks"][network.show_active()]["verify"]
        if config["networks"][network.show_active()].get("verify")
        else False
    )
    return verify


def deploy_mocks(decimals=DECIMALS):
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()

    print("Deploying ETH Mock Price Feeds...")
    eth_mock_price_feed = MockV3AggregatorETH.deploy(
        decimals, ETH_INITIAL_PRICE_FEED_VALUE, {"from": account}
    )
    print(f"Deployed to {eth_mock_price_feed.address}")

    print("Deploying DAI Mock Price Feeds...")
    dai_mock_price_feed = MockV3AggregatorDAI.deploy(
        decimals, DAI_INITIAL_PRICE_FEED_VALUE, {"from": account}
    )
    print(f"Deployed to {dai_mock_price_feed.address}")

    print("Deploying Mock DAI...")
    dai_token = MockDAI.deploy({"from": account})
    print(f"Deployed to {dai_token.address}")
    print("Deploying Mock WETH")
    weth_token = MockWETH.deploy({"from": account})
    print(f"Deployed to {weth_token.address}")


def get_token_balance(user_addr, token_contract):
    amount = token_contract.balanceOf(user_addr)
    return amount


def approve_and_stake(staker, token_farm, contract, amount_wei):
    contract.approve(token_farm.address, amount_wei, {"from": staker}).wait(1)
    token_farm.stake(contract.address, amount_wei, {"from": staker}).wait(1)


def bootstrap_staker(sender, contract, amount_wei=Web3.toWei(10, "ether"), index=1):
    staker = get_account(index)
    contract.transfer(staker.address, amount_wei, {"from": sender}).wait(1)

    return staker
