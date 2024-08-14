#include "NeutronGenerator.hh"
#include "BambooUtils.hh"

#include <G4Event.hh>
#include <G4ParticleGun.hh>
#include <G4ParticleTable.hh>
#include <Randomize.hh>
#include <random>

using namespace CLHEP;

GeneratorRegister<NeutronGenerator>
    NeutronGenerator::reg("NeutronGenerator");

NeutronGenerator::NeutronGenerator(const BambooParameters &pars)
    : BambooGenerator{pars}, gun{new G4ParticleGun}
{
}

void NeutronGenerator::NeutronLoad(const std::string &energySpectrumFile, const std::string &angularDistributionFile)
{
    LoadEnergySpectrum(energySpectrumFile);
    LoadAngularDistribution(angularDistributionFile);
}


void NeutronGenerator::LoadEnergySpectrum(const std::string& energySpectrumFile) {
    energyBins.clear();
    energySpectrum.clear();
    std::ifstream file(energySpectrumFile);
    if (!file.is_open()) {
        std::cerr << "Error: Failed to open energy spectrum file: " << energySpectrumFile << std::endl;
        return;
    }

    double bin, value;
    while (file >> bin >> value) {
        energyBins.push_back(bin);
        energySpectrum.push_back(value);
    }
    int n = energySpectrum.size();
    
    for (int i = 0; i < n - 1; ++i) {
        double diff = energyBins[i + 1] - energyBins[i];
        double result = diff * energySpectrum[i];
        energyValue.push_back(result);
    }
    energyValue.push_back(0);
    file.close();
}


void NeutronGenerator::LoadAngularDistribution(const std::string& angularDistributionFile) {
    angleBins.clear();
    angularDistribution.clear();
    std::ifstream file(angularDistributionFile);
    if (!file.is_open()) {
        std::cerr << "Error: Failed to open angular distribution file: " << angularDistributionFile << std::endl;
        return;
    }

    double Theta, value;
    while (file >> Theta >> value) {
        angleBins.push_back(Theta);
        angularDistribution.push_back(value);
    }

    file.close();
}

G4ParticleDefinition* NeutronGenerator::getneutron() {
    G4ParticleDefinition* particle;
    auto particleTable = G4ParticleTable::GetParticleTable();
    particle = particleTable->FindParticle("neutron");
    return particle;
}

void NeutronGenerator::GeneratePrimaries(G4Event *anEvent) {
    LoadEnergySpectrum("./data/neutronE.txt");
    LoadAngularDistribution("./data/neutronA.txt");
    double energy, directionX, directionY, directionZ;
    std::random_device rd;
    std::mt19937 gen(rd());

    std::piecewise_constant_distribution<double> disEnergy(
        energyBins.begin(), energyBins.end(), energyValue.begin()
    );
    energy = disEnergy(gen);

    std::piecewise_constant_distribution<double> disAngle(
        angleBins.begin(), angleBins.end(), angularDistribution.begin()
    );
    double cosTheta = disAngle(gen);


    double sinTheta = std::sqrt(1.0 - cosTheta * cosTheta);
    double phi = G4UniformRand() * M_PI * 2;
    directionX = sinTheta * std::cos(phi);
    directionY = sinTheta * std::sin(phi);
    directionZ = -cosTheta;

    G4double posX, posY, posZ;
    // we set the emitting surface is 7m*7m.
    posX = (G4UniformRand() - 0.5) * 700*cm;
    posY = (G4UniformRand() - 0.5) * 700*cm;
    posZ = 351*cm;

    auto particle = getneutron();
    G4double mass = particle->GetPDGMass();

    gun->SetParticleDefinition(particle);
    gun->SetParticleEnergy(energy);
    gun->SetParticlePosition(G4ThreeVector(posX, posY, posZ));
    gun->SetParticleMomentumDirection(G4ThreeVector(directionX, directionY, directionZ));

    gun->GeneratePrimaryVertex(anEvent);
}

