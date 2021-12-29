// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "./MockV3Aggregator.sol";

contract MockV3AggregatorETH is MockV3Aggregator {
    constructor(uint8 _decimals, int256 _initialAnswer)
        public
        MockV3Aggregator(_decimals, _initialAnswer)
    {
        decimals = _decimals;
        updateAnswer(_initialAnswer);
    }
}
