activity_pairs = {"arrival":"TriageStartDateTime",
        "TriageStartDateTime":"TriageEndDateTime",
        "biochimieBAStartDateTime":"biochimieTakeBADateTime",
        "biochimieTakeBADateTime":"biochimieResultBADateTime",
        "hematologieBAStartDateTime":"hematologieTakeBADateTime",
        "hematologieTakeBADateTime":"hematologieResultBADateTime",
        "coagulationBAStartDateTime":"coagulationTakeBADateTime",
        "coagulationTakeBADateTime":"coagulationResultBADateTime",
        "RXPrescriptionDateTime":"RXRealizationDateTime",
        "RMIRealizationDateTime":"RMIResultBADateTime"}

distributions_list = ['gamma',  'cauchy','chi','f','norm',
                      'lognorm','expon','beta','t','triang','pareto']