// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract MedicineBatchRegistry {

    struct Batch {
        string batchId;
        string medicineName;
        string manufacturer;
        uint256 mfgDate;
        uint256 expDate;
        string region; // Authorized distribution region (e.g., 'TAMIL NADU')
        bytes32 batchHash;
        address registeredBy;
    }

    mapping(string => Batch) private batches;

    event BatchRegistered(string batchId, address indexed by);

    function registerBatch(
        string memory _batchId,
        string memory _medicineName,
        string memory _manufacturer,
        uint256 _mfgDate,
        uint256 _expDate,
        string memory _region,
        bytes32 _batchHash
    ) public {
        require(batches[_batchId].registeredBy == address(0), "Batch exists");

        batches[_batchId] = Batch(
            _batchId,
            _medicineName,
            _manufacturer,
            _mfgDate,
            _expDate,
            _region,
            _batchHash,
            msg.sender
        );

        emit BatchRegistered(_batchId, msg.sender);
    }

    function verifyBatch(string memory _batchId)
        public
        view
        returns (string memory, uint256, string memory, string memory)
    {
        Batch memory b = batches[_batchId];
        require(b.registeredBy != address(0), "Batch not found");
        return (b.medicineName, b.expDate, b.manufacturer, b.region);
    }
}
