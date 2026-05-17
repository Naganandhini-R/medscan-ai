const hre = require("hardhat");

async function main() {
    const MedicineBatchRegistry = await hre.ethers.getContractFactory("MedicineBatchRegistry");
    const registry = await MedicineBatchRegistry.deploy();

    await registry.waitForDeployment();

    console.log("MedicineBatchRegistry deployed to:", await registry.getAddress());
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
