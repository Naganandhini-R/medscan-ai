const hre = require("hardhat");

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS || "0xe982E462b094850F12AF94d21D470e21bE9D0E9C";
    const MedicineBatchRegistry = await hre.ethers.getContractFactory("MedicineBatchRegistry");
    const registry = await MedicineBatchRegistry.attach(contractAddress);

    const batchId = "GF244009";
    const medicineName = "Rubired Z";
    const manufacturer = "MACLEODS PHARMACEUTICALS LTD.";
    const mfgDate = Math.floor(new Date("2024-07-01").getTime() / 1000);
    const expDate = Math.floor(new Date("2026-06-30").getTime() / 1000);
    const batchHash = hre.ethers.id("rubired-z-batch-hash");

    console.log(`Registering batch ${batchId}...`);
    try {
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
    } catch (e) {
        if (e.message.includes("Batch exists")) {
            console.log(`Batch ${batchId} already registered.`);
        } else {
            throw e;
        }
    }
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
