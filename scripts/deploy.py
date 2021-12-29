from scripts.helpful import (
    approve_and_stake,
    bootstrap_staker,
    get_account,
    get_contract,
    get_token_balance,
)
from brownie import KappToken, TokenFarm
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_kapp_token(no_tokens_allowed=False):
    account = get_account()

    # deploy AggregatorV3Interface
    eth_usd_price_feed_mock = get_contract("eth_usd_price_feed")
    dai_eth_price_feed_mock = get_contract("dai_usd_price_feed")

    # deploy all allowed tokens (FAU(DAI), WETH, Kapp)
    weth_token_mock = get_contract("weth_token")
    dai_token_mock = get_contract("fau_token")

    # deploy our contracts
    kapp_contract = KappToken.deploy({"from": account})

    allowed_tokens = [
        weth_token_mock.address,
        dai_token_mock.address,
        kapp_contract.address,
    ]

    setted_allowed_tokens = allowed_tokens if not no_tokens_allowed else []

    token_farm_contract = TokenFarm.deploy(
        kapp_contract.address, setted_allowed_tokens, {"from": account}
    )
    kapp_contract.transfer(
        token_farm_contract.address,
        kapp_contract.totalSupply() - KEPT_BALANCE,
        {"from": account},
    )

    price_mappings = {
        kapp_contract: dai_eth_price_feed_mock,
        dai_token_mock: dai_eth_price_feed_mock,
        weth_token_mock: eth_usd_price_feed_mock,
    }

    # set contract price feeds
    for key in price_mappings:
        token_farm_contract.setTokenPriceFeed(
            key.address, price_mappings[key].address, {"from": account}
        ).wait(1)

    return (token_farm_contract, kapp_contract)


def stake_reward_workflow():
    account = get_account()
    token_farm, kapp_token = deploy_token_farm_and_kapp_token()

    weth = get_contract("weth_token")
    dai = get_contract("fau_token")

    staker = bootstrap_staker(account, weth)
    staker = bootstrap_staker(account, dai, Web3.toWei(10_000, "ether"))

    approve_and_stake(staker, token_farm, weth, Web3.toWei(3, "ether"))
    approve_and_stake(staker, token_farm, dai, Web3.toWei(250, "ether"))

    ## internal
    # res = token_farm.getStakerTotalValue(staker.address)
    # print(f"total staked: {Web3.fromWei(res, 'ether')}")

    payed_rewards = get_token_balance(staker.address, kapp_token)
    print(f"kapp before: {payed_rewards}")

    print(
        f"available kapp: {Web3.fromWei(get_token_balance(account.address, kapp_token),'ether')}"
    )

    kapp_token.approve(
        token_farm.address, Web3.toWei(1_000_000, "ether"), {"from": account}
    )
    token_farm.payRewards({"from": account}).wait(1)

    payed_rewards = get_token_balance(staker.address, kapp_token)
    print(f"kapp after: {payed_rewards}")


def main():
    stake_reward_workflow()
