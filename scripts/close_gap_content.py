# -*- coding: utf-8 -*-
"""Authored enrichment content for the final 6 coverage-gap headings.

Cross-references are restricted to the candidate_codes the spec supplies:
    2006      -> 2001 2002 2003 2004 2005 2007 2008 2009
    2105      -> 2101 2102 2103 2104 2106
    chemicals -> the 48 enriched Chapter 28 headings
"""

FNB = "Food & Beverages"
CHM = "Chemicals & Pharmaceuticals"

GAP6 = {

# --- Priority: High ---------------------------------------------------------
"2105": dict(
    t="Icecream and other edible ice, whether or not containing cocoa",
    sec=[FNB],
    syn=["ice cream", "icecream", "edible ice", "frozen dessert", "kulfi", "ice candy",
         "softy", "gelato", "sorbet"],
    mkt=["ice cream manufacturing", "frozen dessert trade", "ice cream parlour supply",
         "cold chain dessert distribution"],
    hin=["kulfi", "ice cream", "barf ka gola", "thandai barf"],
    ex=["tub of vanilla ice cream sold by a dairy brand",
        "kulfi sold by a sweet shop",
        "ice candy manufactured for retail distribution",
        "cocoa-containing ice cream bars supplied to a parlour"],
    mat=["milk solids", "sugar", "water"],
    use=["human consumption", "dessert"],
    frm=["frozen", "edible ice", "tub", "bar"],
    ind=["food processing", "dairy", "confectionery"],
    cq=[("Is the product a frozen edible ice such as ice cream or kulfi, or a non-frozen "
         "food preparation such as a dessert mix or powder?",
         "form",
         ["Frozen edible ice - ice cream, kulfi, ice candy",
          "Non-frozen food preparation - mix, powder, concentrate"],
         ["HSN_2106"])],
    xn=[("HSN_2106", "2106 covers food preparations not elsewhere specified, including dessert "
                     "mixes, powders and some non-frozen preparations; 2105 is limited to "
                     "finished edible ice that is sold frozen"),
        ("HSN_2102", "2102 covers yeasts and prepared baking powders used as ingredients; 2105 "
                     "is the finished frozen dessert")],
    lvl="High",
    cr="Ice cream and other edible ice is a well-defined heading and a plain-language query "
       "for 'ice cream' or 'kulfi' maps to it directly. The one genuine boundary is against "
       "2106, since some frozen desserts and dessert preparations are classified as food "
       "preparations rather than edible ice - the deciding factor is whether the finished "
       "product is sold as a frozen edible ice.",
    amb=["ice cream", "frozen dessert", "kulfi", "dessert", "food preparation"],
    d="ice cream and other edible ice, whether or not containing cocoa - including kulfi, "
      "ice candy, softy and similar frozen desserts sold ready to eat",
),

# --- Priority: Medium -------------------------------------------------------
"2006": dict(
    t="Vegetables, fruits, nuts, fruit-peel and other parts of plants, preserved by sugar "
      "(drained, glace or crystallised)",
    sec=[FNB],
    syn=["candied fruit", "crystallised fruit", "glace fruit", "preserved by sugar",
         "candied peel", "tutti frutti"],
    mkt=["candied fruit trade", "bakery ingredient supply", "confectionery ingredient"],
    hin=["murabba", "petha", "candied fruit"],
    ex=["candied orange peel sold to a bakery",
        "tutti frutti used as a cake and ice cream topping",
        "crystallised ginger packed for retail"],
    mat=["fruit", "sugar", "vegetable"],
    use=["human consumption", "bakery ingredient"],
    frm=["candied", "crystallised", "drained", "glace"],
    ind=["food processing", "confectionery", "bakery"],
    cq=[("Is the fruit preserved by sugar as candied or crystallised pieces, or is it a jam, "
         "jelly or puree?",
         "form",
         ["Candied, crystallised or glace pieces", "Jam, jelly, marmalade or fruit puree"],
         ["HSN_2007"])],
    xn=[("HSN_2007", "2007 covers jams, jellies, marmalades and fruit purees and pastes obtained "
                     "by cooking; 2006 is limited to fruit and vegetables preserved by sugar and "
                     "kept in recognisable pieces - drained, glace or crystallised"),
        ("HSN_2008", "2008 covers fruit and nuts otherwise prepared or preserved, for example in "
                     "syrup or brine; 2006 applies specifically where sugar is the preserving "
                     "medium and the product is drained, glace or crystallised")],
    lvl="Medium",
    cr="The 'preserved by sugar' distinction is exactly what a plain-language query cannot "
       "resolve - a user typing 'preserved fruit' could equally mean 2006, 2007 or 2008. The "
       "deciding factors are the preserving medium and whether the fruit stays in recognisable "
       "pieces.",
    amb=["preserved fruit", "candied", "murabba", "jam", "syrup"],
    d="vegetables, fruit, nuts, fruit-peel and other edible parts of plants preserved by sugar "
      "and presented drained, glace or crystallised",
),

# --- Priority: Low - niche industrial chemicals ------------------------------
"2847": dict(
    t="Hydrogen peroxide, whether or not solidified with urea",
    sec=[CHM],
    syn=["hydrogen peroxide", "H2O2", "peroxide", "carbamide peroxide"],
    mkt=["industrial chemical supply", "bleaching chemical trade"],
    ex=["drum of industrial-grade hydrogen peroxide supplied to a textile bleaching unit",
        "hydrogen peroxide solidified with urea for laboratory use"],
    mat=["hydrogen peroxide"],
    use=["bleaching", "disinfecting", "oxidising"],
    frm=["solution", "solidified"],
    ind=["chemicals", "textile processing"],
    xn=[("HSN_2828", "2828 covers hypochlorites and chlorates used as bleaching agents; 2847 is "
                     "the specific heading for hydrogen peroxide")],
    lvl="Medium",
    cr="A single named compound with an unambiguous heading. The main risk is confusion with "
       "other bleaching and oxidising agents in the chapter.",
    amb=["peroxide", "bleach", "disinfectant"],
    d="hydrogen peroxide, whether or not solidified with urea",
),

"2838": dict(
    t="Fulminates, cyanates and thiocyanates",
    sec=[CHM],
    syn=["fulminate", "cyanate", "thiocyanate", "isocyanate salt"],
    mkt=["industrial chemical supply", "speciality chemical trade"],
    ex=["potassium thiocyanate supplied to a laboratory",
        "sodium cyanate used as an intermediate in chemical manufacturing"],
    mat=["inorganic salt"],
    use=["chemical intermediate", "laboratory reagent"],
    frm=["salt", "powder"],
    ind=["chemicals"],
    xn=[("HSN_2837", "2837 covers cyanides and cyanide oxides; 2838 is the separate heading for "
                     "fulminates, cyanates and thiocyanates")],
    lvl="Medium",
    cr="A narrow heading of named inorganic salts. The closest neighbour is 2837 (cyanides), "
       "which is a distinct group despite the similar chemistry and naming.",
    amb=["cyanate", "cyanide", "thiocyanate"],
    d="fulminates, cyanates and thiocyanates",
),

"2848": dict(
    t="Phosphides, whether or not chemically defined, excluding ferrophosphorus",
    sec=[CHM],
    syn=["phosphide", "aluminium phosphide", "zinc phosphide", "metal phosphide"],
    mkt=["industrial chemical supply", "fumigant chemical trade"],
    ex=["aluminium phosphide tablets supplied as a grain fumigant",
        "zinc phosphide used in industrial pest control formulations"],
    mat=["phosphide"],
    use=["fumigation", "chemical intermediate"],
    frm=["tablet", "powder"],
    ind=["chemicals", "agrochemicals"],
    xn=[("HSN_2853", "2853 covers other inorganic compounds not elsewhere specified; 2848 is the "
                     "specific heading for phosphides other than ferrophosphorus")],
    lvl="Medium",
    cr="A named group of inorganic compounds with an explicit exclusion for ferrophosphorus, "
       "which is classified as a ferro-alloy instead.",
    amb=["phosphide", "fumigant", "ferrophosphorus"],
    d="phosphides, whether or not chemically defined, excluding ferrophosphorus",
),

"2850": dict(
    t="Hydrides, nitrides, azides, silicides and borides, whether or not chemically defined, "
      "other than compounds which are also carbides of heading 2849",
    sec=[CHM],
    syn=["hydride", "nitride", "azide", "silicide", "boride"],
    mkt=["industrial chemical supply", "speciality ceramic material trade"],
    ex=["sodium borohydride supplied as a reducing agent",
        "silicon nitride powder used in technical ceramics"],
    mat=["inorganic compound"],
    use=["chemical intermediate", "ceramic material"],
    frm=["powder", "compound"],
    ind=["chemicals", "ceramics"],
    xn=[("HSN_2849", "2849 covers carbides; where a compound is also a carbide it stays in 2849 "
                     "and is excluded from 2850 by the heading text itself")],
    lvl="Medium",
    cr="A grouped heading of named binary compounds. The heading text itself carves out "
       "compounds that are also carbides, which is the only real boundary.",
    amb=["hydride", "nitride", "boride", "carbide"],
    d="hydrides, nitrides, azides, silicides and borides, whether or not chemically defined, "
      "other than compounds which are also carbides of heading 2849",
),
}
