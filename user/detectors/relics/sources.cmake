message("enable relics")
set(source_path ${PROJECT_SOURCE_DIR}/user/detectors/relics)
set(Detector ${Detector} ${source_path}/Material.cc)
set(Detector ${Detector} ${source_path}/Monoblock.cc)
set(Detector ${Detector} ${source_path}/Cuboid.cc)
set(Detector ${Detector} ${source_path}/Cylinder.cc)
set(Detector ${Detector} ${source_path}/Prism.cc)
set(Detector ${Detector} ${source_path}/Polyhedra.cc)
set(Detector ${Detector} ${source_path}/HolesBoard.cc)
set(Detector ${Detector} ${source_path}/MeshGrid.cc)
set(Detector ${Detector} ${source_path}/World.cc)
set(Detector ${Detector} ${source_path}/PMTsR8520.cc)
set(Detector ${Detector} ${source_path}/Array.cc)
set(Detector ${Detector} ${source_path}/GetMass.cc)
configure_file("${CMAKE_SOURCE_DIR}/data/botPMTs.txt" "${CMAKE_BINARY_DIR}/data/botPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/topPMTs.txt" "${CMAKE_BINARY_DIR}/data/topPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/downtopVetoPMTs.txt" "${CMAKE_BINARY_DIR}/data/downtopVetoPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/upbotVetoPMTs.txt" "${CMAKE_BINARY_DIR}/data/upbotVetoPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/midtopVetoPMTs.txt" "${CMAKE_BINARY_DIR}/data/midtopVetoPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/midbotVetoPMTs.txt" "${CMAKE_BINARY_DIR}/data/midbotVetoPMTs.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/XeVetoInBell.txt" "${CMAKE_BINARY_DIR}/data/XeVetoInBell.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/OuterContainerRZ.txt" "${CMAKE_BINARY_DIR}/data/OuterContainerRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/VacuumRZ.txt" "${CMAKE_BINARY_DIR}/data/VacuumRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/InnerContainerRZ.txt" "${CMAKE_BINARY_DIR}/data/InnerContainerRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/InnerTeflonRZ.txt" "${CMAKE_BINARY_DIR}/data/InnerTeflonRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/OuterGasXeRZ.txt" "${CMAKE_BINARY_DIR}/data/OuterGasXeRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/XenonVetoRZ.txt" "${CMAKE_BINARY_DIR}/data/XenonVetoRZ.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/XeInTopPMTTeflon.txt" "${CMAKE_BINARY_DIR}/data/XeInTopPMTTeflon.txt" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/data/XeInBotPMTTeflon.txt" "${CMAKE_BINARY_DIR}/data/XeInBotPMTTeflon.txt" COPYONLY)
