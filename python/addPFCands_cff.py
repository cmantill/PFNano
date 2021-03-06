import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

def addPFCands(process, runOnMC=False, saveAll=False, saveAK4=False, saveAK8=False, saveAK15=False):
    if saveAll and (saveAK4 or saveAK8 or saveAK15):
        raise ValueError("In call to addPFCands(), argument saveAll is incompatible with other save options (saveAll={}, saveAK4={} ,saveAK8={}, saveAK15={}".format(saveAll, saveAK4, saveAK8, saveAK15))

    if not (saveAll or saveAK4 or saveAK8 or saveAK15):
        raise ValueError("In call to addPFCands(), specify at least one save option.")

    process.customizedPFCandsTask = cms.Task( )
    process.schedule.associate(process.customizedPFCandsTask)

    if saveAll:
        candInput = cms.InputTag("packedPFCandidates")
    else:
        candList = cms.VInputTag()
        if saveAK4:
            process.finalJetsAK4Constituents = cms.EDProducer("PatJetConstituentPtrSelector",
                                                    src = cms.InputTag("finalJets"),
                                                    cut = cms.string("")
                                                    )
            candList.append(cms.InputTag("finalJetsAK4Constituents", "constituents"))
            process.customizedPFCandsTask.add(process.finalJetsAK4Constituents)

        if saveAK8:
            process.finalJetsAK8Constituents = cms.EDProducer("PatJetConstituentPtrSelector",
                                                    src = cms.InputTag("finalJetsAK8"),
                                                    cut = cms.string("")
                                                    )
            candList.append(cms.InputTag("finalJetsAK8Constituents", "constituents"))
            process.customizedPFCandsTask.add(process.finalJetsAK8Constituents)
        
        if saveAK15:
            process.finalJetsAK15Constituents = cms.EDProducer("PatJetConstituentPtrSelector",
                                                               src = cms.InputTag("ak15WithUserData"),
                                                               cut = cms.string("")
            )
            candList.append(cms.InputTag("finalJetsAK15Constituents", "constituents"))
            process.customizedPFCandsTask.add(process.finalJetsAK15Constituents)

        process.finalJetsConstituents = cms.EDProducer("PackedCandidatePtrMerger", 
                                                       src = candList, 
                                                       skipNulls = cms.bool(True), 
                                                       warnOnSkip = cms.bool(True))
        candInput = cms.InputTag("finalJetsConstituents")

    process.customConstituentsExtTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
                                                        src = candInput,
                                                        cut = cms.string(""), #we should not filter after pruning
                                                        name = cms.string("PFCands"),
                                                        doc = cms.string("interesting particles from various jet collections"),
                                                        singleton = cms.bool(False), # the number of entries is variable
                                                        extension = cms.bool(False), # this is the extension table for the AK8 constituents
                                                        variables = cms.PSet(CandVars,
                                                            puppiWeight = Var("puppiWeight()", float, doc="Puppi weight",precision=10),
                                                            puppiWeightNoLep = Var("puppiWeightNoLep()", float, doc="Puppi weight removing leptons",precision=10),
                                                            vtxChi2 = Var("?hasTrackDetails()?vertexChi2():-1", float, doc="vertex chi2",precision=10),
                                                            trkChi2 = Var("?hasTrackDetails()?pseudoTrack().normalizedChi2():-1", float, doc="normalized trk chi2", precision=10),
                                                            dz = Var("?hasTrackDetails()?dz():-1", float, doc="pf dz", precision=10),
                                                            dzErr = Var("?hasTrackDetails()?dzError():-1", float, doc="pf dz err", precision=10),
                                                            d0 = Var("?hasTrackDetails()?dxy():-1", float, doc="pf d0", precision=10),
                                                            d0Err = Var("?hasTrackDetails()?dxyError():-1", float, doc="pf d0 err", precision=10),
                                                            pvAssocQuality = Var("pvAssociationQuality()", int, doc="primary vertex association quality"),
                                                            lostInnerHits = Var("lostInnerHits()", int, doc="lost inner hits"),
                                                            trkQuality = Var("?hasTrackDetails()?pseudoTrack().qualityMask():0", int, doc="track quality mask"),
                                                         )
                                    )

    process.customAK4ConstituentsTable = cms.EDProducer("PatJetConstituentTableProducer",
                                                        #candidates = cms.InputTag("packedPFCandidates"),
                                                        candidates = candInput,
                                                        jets = cms.InputTag("finalJets"),
                                                        jet_radius = cms.double(0.4),
                                                        name = cms.string("JetPFCands"),
                                                        idx_name = cms.string("pFCandsIdx"),
                                                        nameSV = cms.string("JetSVs"),
                                                        idx_nameSV = cms.string("sVIdx"),
                                                        )

    process.customAK8ConstituentsTable = cms.EDProducer("PatJetConstituentTableProducer",
                                                        candidates = candInput,
                                                        jets = cms.InputTag("finalJetsAK8"),
                                                        jet_radius = cms.double(0.8),
                                                        name = cms.string("FatJetPFCands"),
                                                        idx_name = cms.string("pFCandsIdx"),
                                                        nameSV = cms.string("FatJetSVs"),
                                                        idx_nameSV = cms.string("sVIdx"),
                                                        )

    process.customAK15ConstituentsTable = cms.EDProducer("PatJetConstituentTableProducer",
                                                         candidates = candInput,
                                                         jets       = cms.InputTag("ak15WithUserData"),
                                                         jet_radius = cms.double(1.5),
                                                         name       = cms.string("JetPFCandsAK15"),
                                                         nameSV     = cms.string("JetSVsAK15")
    )

    if not saveAll:
        process.customizedPFCandsTask.add(process.finalJetsConstituents)
    process.customizedPFCandsTask.add(process.customConstituentsExtTable)
    process.customizedPFCandsTask.add(process.customAK4ConstituentsTable)
    process.customizedPFCandsTask.add(process.customAK8ConstituentsTable)
    process.customizedPFCandsTask.add(process.customAK15ConstituentsTable)

    if runOnMC:

        process.customGenJetAK8Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
            src=cms.InputTag("ak8GenJetsNoNuSoftDrop"),
            cut=cms.string("pt > 100."),
            name=cms.string("CustomGenJetAK8"),
            doc=cms.string("AK8 GenJets made with visible genparticles"),
            singleton=cms.bool(False),  # the number of entries is variable
            extension=cms.bool(False),  # this is the main table for the genjets
            variables=cms.PSet(P4Vars,
            )
        )
        process.customGenJetAK8Table.variables.pt.precision = 10

        process.customGenJetAK15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
            src=cms.InputTag("ak15GenJetsNoNuSoftDrop"),
            cut=cms.string("pt > 100."),
            name=cms.string("CustomGenJetAK15"),
            doc=cms.string("AK15 GenJets made with visible genparticles"),
            singleton=cms.bool(False),
            extension=cms.bool(False),
            variables=cms.PSet(P4Vars,
            )
        )
        process.customGenJetAK15Table.variables.pt.precision = 10

        process.genJetsAK8Constituents = cms.EDProducer("GenJetPackedConstituentPtrSelector",
                                                    src = cms.InputTag("slimmedGenJetsAK8"),
                                                    cut = cms.string("pt > 100.")
                                                    )

      
        process.genJetsAK4Constituents = process.genJetsAK8Constituents.clone(
                                                    src = cms.InputTag("slimmedGenJets"),
                                                    cut = cms.string("pt > 20")
                                                    )

        process.genJetsAK15Constituents = process.genJetsAK8Constituents.clone(
            src = cms.InputTag("ak15GenJetsNoNu"), # "slimmedGenJetsAK15"
            cut = cms.string("pt > 100")
        )

        if saveAll:
            genCandInput = cms.InputTag("packedGenParticles")
        else:
            genCandInput =  cms.InputTag("genJetsConstituents")
            genCandList = cms.VInputTag()
            if saveAK4:
                genCandList.append(cms.InputTag("genJetsAK4Constituents", "constituents"))
            if saveAK8:
                genCandList.append(cms.InputTag("genJetsAK8Constituents", "constituents"))
            if saveAK15:
                genCandList.append(cms.InputTag("genJetsAK15Constituents", "constituents"))
            process.genJetsConstituents = cms.EDProducer("PackedGenParticlePtrMerger", 
                                                         src        = genCandList, 
                                                         skipNulls  = cms.bool(True), 
                                                         warnOnSkip = cms.bool(True))

        process.genJetsParticleTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
                                                         src = genCandInput,
                                                         cut = cms.string(""), #we should not filter after pruning
                                                         name= cms.string("GenCands"),
                                                         doc = cms.string("interesting gen particles from various jet collections"),
                                                         singleton = cms.bool(False), # the number of entries is variable
                                                         extension = cms.bool(False), # this is the main table for the AK8 constituents
                                                         variables = cms.PSet(CandVars)
                                                     )
        process.genAK4ConstituentsTable = cms.EDProducer("GenJetConstituentTableProducer",
                                                         candidates = genCandInput,
                                                         jets = cms.InputTag("genJetsAK4Constituents"), # Note: The name has "Constituents" in it, but these are the jets
                                                         name = cms.string("GenJetCands"),
                                                         nameSV = cms.string("GenJetSVs"),
                                                         idx_name = cms.string("pFCandsIdx"),
                                                         idx_nameSV = cms.string("sVIdx"),
                                                         readBtag = cms.bool(False))

        process.genAK8ConstituentsTable = cms.EDProducer("GenJetConstituentTableProducer",
                                                         candidates = genCandInput,
                                                         jets = cms.InputTag("genJetsAK8Constituents"), # Note: The name has "Constituents" in it, but these are the jets
                                                         name = cms.string("GenFatJetCands"),
                                                         nameSV = cms.string("GenFatJetSVs"),
                                                         idx_name = cms.string("pFCandsIdx"),
                                                         idx_nameSV = cms.string("sVIdx"),
                                                         readBtag = cms.bool(False))

        process.genAK15ConstituentsTable = cms.EDProducer("GenJetConstituentTableProducer",
                                                         candidates = cms.InputTag("genJetsConstituents"),
                                                         jets = cms.InputTag("genJetsAK15Constituents"), # Note: The name has "Constituents" in it, but these are the jets
                                                         name = cms.string("GenJetCandsAK15"),
                                                         nameSV = cms.string("GenJetSVsAK15"),
                                                         idx_name = cms.string("pFCandsIdx"),
                                                         idx_nameSV = cms.string("sVIdx"),
                                                         readBtag = cms.bool(False))

        process.customizedPFCandsTask.add(process.customGenJetAK8Table)
        process.customizedPFCandsTask.add(process.customGenJetAK15Table)
        process.customizedPFCandsTask.add(process.genJetsAK4Constituents) #Note: For gen need to add jets to the process to keep pt cuts.
        process.customizedPFCandsTask.add(process.genJetsAK8Constituents)
        process.customizedPFCandsTask.add(process.genJetsAK15Constituents)
        if not saveAll:
            process.customizedPFCandsTask.add(process.genJetsConstituents)
        process.customizedPFCandsTask.add(process.genJetsParticleTable)
        process.customizedPFCandsTask.add(process.genAK8ConstituentsTable)
        process.customizedPFCandsTask.add(process.genAK4ConstituentsTable)
        process.customizedPFCandsTask.add(process.genAK15ConstituentsTable)

    return process
