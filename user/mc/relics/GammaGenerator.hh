#pragma once

#include "BambooFactory.hh"
#include "BambooGenerator.hh"

#include <G4ParticleGun.hh>

#include <memory>

class G4ParticleGun;
class G4Event;

class GammaGenerator : public BambooGenerator {
  public:
    GammaGenerator(const BambooParameters &pars);

    ~GammaGenerator() = default;

    virtual void GeneratePrimaries(G4Event *anEvent);

    static GeneratorRegister<GammaGenerator> reg;

  private:
    void GammaLoad(const std::string& energySpectrumFile, const std::string& angularDistributionFile);
    std::vector<double> energyBins;
    std::vector<double> energySpectrum;
    std::vector<double> energyValue;
    std::vector<double> angleBins;
    std::vector<double> angularDistribution;

    G4ParticleDefinition* getgamma();
    void LoadEnergySpectrum(const std::string& energySpectrumFile);
    void LoadAngularDistribution(const std::string& angularDistributionFile);

    std::unique_ptr<G4ParticleGun> gun;
};
