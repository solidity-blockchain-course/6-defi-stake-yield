- create KappToken.sol
  - 1 million supply
  - 1:1 to FAU(DAI)
- create TokenFarm.sol functionality:
  - stakeToken
  - unstakeToken
  - userTotalValueInUSD
  - issuance (as reward)
  - allowance for other supported tokens

Issuance/Reward will iterate through valid stakers and for each USD will be payed 1 kapp token
with the help of Chainlink price feeds
