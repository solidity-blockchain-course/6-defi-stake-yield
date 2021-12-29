// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    mapping(address => mapping(address => uint256)) internal stakingBalance;
    mapping(address => address) public priceFeedMapping;
    mapping(address => bool) public uniqueStakers;

    address[] public allowedTokens;
    address[] public stakers;

    IERC20 internal kappContract;

    constructor(address _kappContract, address[] memory _allowedTokens) {
        kappContract = IERC20(_kappContract);
        allowedTokens = _allowedTokens;
    }

    function getStakingBalance(address _staker, address _contract)
        external
        view
        returns (uint256)
    {
        return stakingBalance[_staker][_contract];
    }

    function stake(address _tokenContract, uint256 _amount) public {
        require(_amount > 0, "Staked amount should be greater than 0 !");
        require(
            isTokenAllowed(_tokenContract),
            "This token is not allowed for staking !"
        );

        stakingBalance[msg.sender][_tokenContract] += _amount;
        if (!uniqueStakers[msg.sender]) {
            stakers.push(msg.sender);
            uniqueStakers[msg.sender] = true;
        }

        IERC20(_tokenContract).transferFrom(msg.sender, address(this), _amount);
    }

    function unstakeAll(address _contract) external {
        uint256 amount = stakingBalance[msg.sender][_contract];
        require(amount > 0, "No tokens are staked !");

        stakingBalance[msg.sender][_contract] = 0;
        IERC20(_contract).transfer(msg.sender, amount);
    }

    function payRewards() external onlyOwner {
        for (uint256 i = 0; i < stakers.length; i++) {
            uint256 accumulated = getStakerTotalValue(stakers[i]);
            if (accumulated <= 0) {
                continue;
            }
            kappContract.transfer(stakers[i], accumulated);
        }
    }

    function getStakerTotalValue(address _staker)
        internal
        view
        returns (uint256)
    {
        uint256 accumulated = 0;
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            uint256 contractBalance = stakingBalance[_staker][allowedTokens[i]];
            if (contractBalance <= 0) {
                continue;
            }

            (uint256 value, uint256 decimals) = getUsdValue(
                allowedTokens[i],
                contractBalance
            );

            uint256 total = (contractBalance * value) / (10**decimals);
            accumulated += total;
        }
        return accumulated;
    }

    function getUsdValue(address _contract, uint256 _stakedAmount)
        public
        view
        returns (uint256, uint256)
    {
        if (_stakedAmount == 0) {
            return (0, 0);
        }
        address priceFeedAddress = priceFeedMapping[_contract];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = priceFeed.decimals();
        return (uint256(price), decimals);
    }

    function isTokenAllowed(address _token) internal view returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _token) {
                return true;
            }
        }
        return false;
    }

    function addAllowedToken(address _token) external onlyOwner {
        allowedTokens.push(_token);
    }

    function setTokenPriceFeed(address _token, address _priceFeed)
        public
        onlyOwner
    {
        priceFeedMapping[_token] = _priceFeed;
    }
}
