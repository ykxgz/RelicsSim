#include "HolesBoard.hh"
#include "PandaXSensitiveDetector.hh"

#include <G4Version.hh>
#include <G4Material.hh>
#include <G4ThreeVector.hh>
#include <G4LogicalVolume.hh>
#include <G4Box.hh>
#include <G4Tubs.hh>
#include <G4Polyhedra.hh>
#include <G4Transform3D.hh>
#include <G4SubtractionSolid.hh>
#if G4VERSION_NUMBER>=1100
  #include <G4MultiUnion.hh>
#endif

DetectorRegister<HolesBoard, std::string, BambooParameters> HolesBoard::reg("HolesBoard");

HolesBoard::HolesBoard (const std::string &n, const BambooParameters &pars)
  : Monoblock(n, pars) {
    G4cout << "create detector HolesBoard..." << G4endl;
}

bool HolesBoard::constructMainLV(const BambooParameters &) {
    using namespace CLHEP;
    auto soliname = parameters.getParameter("soliname");
    auto logivol = parameters.getParameter("logivol");
    auto height = parameters.evaluateParameter("height");
    auto radius = parameters.evaluateParameter("radius");
    auto width_x = parameters.evaluateParameter("width_x");
    auto material = parameters.getParameter("material");
    std::string source = parameters.getParameter("source");
    // default value of sides is 0
    int sides = parameters.getParameter<int>("sides");
    auto optical_sister = parameters.getParameter("optical_sister");
    if (height == 0) {
        height = 2 * m;
    }
    if (radius == 0) {
        radius = 1 * m;
    }

    G4VSolid* solid;
    if (sides == 0) {
        solid = new G4Tubs(soliname, 0, radius, height / 2, 0, 2 * M_PI);
    } else {
        G4double circumcircle_r = radius / std::cos(M_PI / sides);
        G4double r[4] = {0, circumcircle_r, circumcircle_r, 0};
        G4double z[4] = {-height / 2, -height / 2, height / 2, height / 2};
        solid = new G4Polyhedra(soliname, 0, 2 * M_PI, sides, 4, r, z);
    }

#if G4VERSION_NUMBER>=1100
    auto holes = new G4MultiUnion("Holes");
#endif
    auto box =
        new G4Box(soliname, width_x / 2, width_x / 2, height);
    std::ifstream source_stream(source);
    int index, nObjects;
    double X, Y, Z, RotY, RotZ;
    if (source_stream >> nObjects) {
      for (int il = 0; il < nObjects; ++il) {
        source_stream >> index >> X >> Y >> Z >> RotY >> RotZ;
        if (source_stream.fail())
          throw std::runtime_error("Array: error read data");
        G4RotationMatrix *mRot = new G4RotationMatrix();
        mRot->rotateZ(-RotZ * deg);
        mRot->rotateY(-RotY * deg);
        G4RotationMatrix invRot = mRot->invert();
        G4ThreeVector position = G4ThreeVector(X * cm, Y * cm, Z * cm);
        G4Transform3D transform = G4Transform3D(invRot, position);
#if G4VERSION_NUMBER>=1100
        holes->AddNode(box, transform);
#else
        solid =
            new G4SubtractionSolid(soliname, solid, box, transform);
#endif
      }
#if G4VERSION_NUMBER>=1100
      holes->Voxelize();
      solid =
            new G4SubtractionSolid(soliname, solid, holes);
#endif
    } else {
      throw std::runtime_error("Array: error read data");
    }

    auto medium = G4Material::GetMaterial(material);
    mainLV =
        new G4LogicalVolume(solid, medium, logivol, 0, 0, 0);
    return true;
}

