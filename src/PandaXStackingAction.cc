#include "PandaXStackingAction.hh"
#include "PandaXDataManager.hh"

#include <G4EventManager.hh>
#include <G4Ions.hh>
#include <G4StackManager.hh>
#include <G4Track.hh>
#include <G4Version.hh>

PandaXStackingAction::~PandaXStackingAction() {}

void addTrack(const G4Track *aTrack) {
    TemporaryParticle tp;
    tp.setParticleType(aTrack->GetParticleDefinition()->GetParticleName());
    tp.setId(aTrack->GetTrackID());
    tp.setEnergy(aTrack->GetTotalEnergy());
    tp.setPx(aTrack->GetMomentum().x());
    tp.setPy(aTrack->GetMomentum().y());
    tp.setPz(aTrack->GetMomentum().z());
    tp.setX(aTrack->GetPosition().x());
    tp.setY(aTrack->GetPosition().y());
    tp.setZ(aTrack->GetPosition().z());
    PandaXDataManager::getInstance().addTemporaryParticle(tp);
}

G4ClassificationOfNewTrack
PandaXStackingAction::ClassifyNewTrack(const G4Track *aTrack) {
    auto def = aTrack->GetParticleDefinition();
    //Debug
    //G4cout << "ClassifyNewTrack: particle " << aTrack->GetParticleDefinition()->GetParticleName()
    //    << ", track ID " << aTrack->GetTrackID()
    //   << ", kinetic energy " << aTrack->GetKineticEnergy()
    //    << ", ion life time " << aTrack->GetParticleDefinition()->GetIonLifeTime() << G4endl;
    if (def->GetParticleType() != "nucleus" || aTrack->GetTrackID() == 1) {
        return fUrgent;
    }
    if (aTrack->GetTrackStatus() == fPostponeToNextEvent) {
    //    G4cout << "fPostponeToNextEvent" << G4endl;
        addTrack(aTrack);
        return fWaiting;
    }
    if (aTrack->GetKineticEnergy() > 0.0)
        return fUrgent;
    if (def->GetIonLifeTime() > chainSplittingLifeTime) {
    //    G4cout << "time is out" << G4endl;
        if (def->GetParticleName() == "Pb210") {
    //        G4cout << "particle is Pb" << G4endl;
            return fKill;
        } else {
        addTrack(aTrack);
        return fWaiting;
        }
    }
    return fUrgent;

}

void PandaXStackingAction::NewStage() {
    // all the urgent tracks have been processed. So we can save the results.
    PandaXDataManager::getInstance().fillEvent(
        G4EventManager::GetEventManager()->GetConstCurrentEvent(), true);
}

void PandaXStackingAction::PrepareNewEvent() {}
