message("enable relics")
set(source_path ${PROJECT_SOURCE_DIR}/user/mc/relics)
set(UserMC ${UserMC} ${source_path}/MuonGenerator.cc)
set(UserMC ${UserMC} ${source_path}/NeutronGenerator.cc)
set(UserMC ${UserMC} ${source_path}/GammaGenerator.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalPhysics.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalHit.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalSD.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalDataManager.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalRunAction.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalEventAction.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalSteppingAction.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalAnalysis.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalTrackingAction.cc)
set(UserMC ${UserMC} ${source_path}/RelicsOpticalStackingAction.cc)