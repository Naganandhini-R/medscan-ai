const hre = require("hardhat");

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS || "0x5FbDB2315678afecb367f032d93F642f64180aa3";
    const MedicineBatchRegistry = await hre.ethers.getContractFactory("MedicineBatchRegistry");
    const registry = await MedicineBatchRegistry.attach(contractAddress);

    // Get arguments from command line
    const args = process.argv.slice(2);
    if (args.length < 5) {
        console.error("Usage: npx hardhat run scripts/register_batch.js --network localhost -- <batchId> <name> <manufacturer> <mfgDate> <expDate>");
        process.exit(1);
    }

    const [batchId, medicineName, manufacturer, mfgDateStr, expDateStr] = args;

    const mfgDate = Math.floor(new Date(mfgDateStr).getTime() / 1000);
    const expDate = Math.floor(new Date(expDateStr).getTime() / 1000);

    // Create a deterministic hash for the batch
    const batchHash = hre.ethers.id(batchId + manufacturer + medicineName);

    console.log(`Registering batch: ${batchId} - ${medicineName}`);

    const tx = await registry.registerBatch(
        batchId,
        medicineName,
        manufacturer,
        mfgDate,
        expDate,
        batchHash
    );

    await tx.wait();
    console.log(`Batch ${batchId} registered successfully!`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
