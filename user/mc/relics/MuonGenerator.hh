#pragma once

#include "BambooFactory.hh"
#include "BambooGenerator.hh"

#include <G4ParticleGun.hh>

#include <memory>

class G4ParticleGun;
class G4Event;

class MuonGenerator : public BambooGenerator {
  public:
    MuonGenerator(const BambooParameters &pars);

    ~MuonGenerator() = default;

    virtual void GeneratePrimaries(G4Event *anEvent);

    static GeneratorRegister<MuonGenerator> reg;

  private:
    G4double n;
    G4double E0;
    G4double epsilon;
    G4double Rd;
    G4double charge_ratio;
    G4double charge_thres;
    G4double theta_max;
    G4double E_low;
    G4double E_up;
    G4double shielding_x;
    G4double shielding_z;

    G4double thetaSpectrum(G4double);
    G4double energySpectrum(G4double);
    G4double getRandomTheta();
    G4double getRandomPhi();
    G4double getRandomEnergy();
    G4ParticleDefinition* getMuonCharge();

    std::unique_ptr<G4ParticleGun> gun;
};
