#!/usr/bin/env python
# coding: utf-8

import re

from morphgnt.utils import load_yaml, sorted_items

regex_templates = {
    "greek": ur"[\u0370-\u03FF\u1F00-\u1FFF]+",
    "gloss": ur"‘([^’]|’s )+’",
    "half-gloss": ur"‘[^’]+",
    "text": ur"[A-Za-z0-9.,/\-’() ]+",
    "latin": ur"[A-Za-zō]+",
    "pie": ur"\*[a-z]+",
    "skt": ur"[a-záīā]+",
    "latvian": ur"[a-zô]+",
    "lithuanian": ur"[a-záž]+",
    "ref": ur"(?:Mt|Ac) \d+:\d+",
    "see": ur"s\.|see",
    "prec": ur"prec\.|preceding",
}

regexes = [
    ur"(orig|etym)\. (complex|not determined|obscure|unclear|uncertain|unknown)$",
    ur"=Attic {greek}$",
    ur"=Lat\. {latin} {latin}$",
    ur"=Macedonian {greek} {gloss}$",
    ur"=next entry$",
    ur"=older {greek} /{greek}, fem\. of {greek}$",
    ur"={greek}$",
    ur"={greek}, cp\. {greek} {gloss}; {gloss}$",
    ur"=ὁ {greek} {gloss}; {see} {greek}$",
    ur"Aram\. ={text}; {see} explanation {ref}$",
    ur"Aram\. term ={gloss}$",
    ur"Aram\. word of uncertain mng\.$",
    ur"Aram\. {gloss}$",
    ur"Aram\. {gloss}; a common name$",
    ur"Aram\. {gloss}; cp\. next$",
    ur"Aram\.$",
    ur"Aram\., perh\. {half-gloss}$",
    ur"Aram\., prob\. ={text} {gloss}, i\. e\. {text}$",
    ur"Attic contracted form of {greek} {gloss}, perh\. Skt\. assoc\.$",
    ur"Attic form ={greek}, etym\. uncertain$",
    ur"Attic form of {greek}$",
    ur"Coptic loanword$",
    ur"Egyptian base w\. Heb\. assoc\.$",
    ur"Heb\. name, hence {gloss}$",
    ur"Heb\. {gloss}$",
    ur"Heb\. {gloss}$",
    ur"Heb\.$",
    ur"Heb\., of uncertain etymology$",
    ur"Heb\.; cp\. modern Gk\. ἀ\. {gloss}$",
    ur"Heb\.; {text} {gloss}$",
    ur"IE {pie}, cp\. {greek} {gloss}$",
    ur"IE$",
    ur"IE, cp\. Lat\. {latin}$",
    ur"IE, cp\. {greek} {gloss}; {gloss}$",
    ur"IE; mostly used by poets$",
    ur"IE; var\. senses in Gk\. lit\.$",
    ur"IE; {text}:{text}$",
    ur"I\. {greek}$",
    ur"Lat\. loanword:{gloss}, {text} ={text}$",
    ur"Lat\. orig\.; {text}$",
    ur"Lat\. {latin} {gloss}; {gloss}; {text}$",
    ur"MT",
    ur"Persian loanword rendered {gloss}$",
    ur"Roman cognomen$",
    ur"Semitic assoc\.; frequently referenced by Herodotus$",
    ur"Semitic orig\.$",
    ur"Skt\. =Lat\. {latin} {gloss}$",
    ur"Skt\. assoc\. in sense of {gloss}$",
    ur"Skt\. assoc\.$",
    ur"Skt\. assoc\., cp\. Lat\. {latin} {gloss}$",
    ur"Skt\. assoc\., cp\. {greek} /{greek} /{greek} {gloss}; orig\. {gloss}, then {gloss}$",
    ur"Skt\. assoc\., cp\. {greek} {gloss}; in Homer both as {gloss} and {gloss}$",
    ur"Skt\. assoc\., cp\. {greek}$",
    ur"Skt\. assoc\.; {text} \(esp\. of {text}\) {gloss}, {text} {gloss}$",
    ur"Skt\. via Heb\.$",
    ur"Skt\. {skt} {gloss}$",
    ur"Skt\. {skt} {gloss}$",
    ur"Skt\. {skt} {gloss}, Lat\. {latin} {gloss}; prim\. in local sense {gloss}$",
    ur"Skt\. {skt} · {gloss}$",
    ur"a Greek name$",
    ur"a city named in honor of Antipater, procurator of Judea under Julius Caesar$",
    ur"a common name in the Greco- Roman world$",
    ur"a common name$",
    ur"acc\. to Herodotus 4, 199, a Cyrenaic word$",
    ur"an onomatopoetic word ={gloss}, sim\. Lat\. {latin}; {text} {gloss}$",
    ur"apparently of Heb\. orig\.$",
    ur"apparently of foreign orig\.$",
    ur"assoc\. w\. {greek} {text}, pl\. as in {greek} {gloss}$",
    ur"assoc\. w\. {greek}; {gloss}, also {gloss}$",
    ur"association has been made principally with {greek} {gloss} {text}, and w\. {greek} \({greek}\) {gloss}$",
    ur"by- form of {greek} \({greek}, {greek} {gloss}\)$",
    ur"by- form of {greek} {gloss}$",
    ur"by- form of {greek}$",
    ur"by- form of {greek}; {gloss}$",
    ur"contracted from {greek} \(ἀ- priv\., {greek}\) {gloss}$",
    ur"cp\. Homeric {greek} {gloss}$",
    ur"cp\. Lat\. {latin} {gloss}$",
    ur"cp\. Lat\. {latin} {gloss}; in the strict sense:{text}; the synonym {greek} in the strict sense refers to {gloss} or {gloss}, {text}. Usage in the NT is much more fluid.$",
    ur"cp\. Lat\. {latin} {gloss}; prim\. {gloss} {text}, then {gloss}$",
    ur"cp\. Lat\. {latin}$",
    ur"cp\. Skt\. {skt} {gloss}$",
    ur"cp\. Skt\. {skt} {gloss}, Lat\. {latin}$",
    ur"cp\. epic noun {greek} and Attic {greek}, both {gloss}$",
    ur"cp\. epic {greek} {gloss}; {gloss}$",
    ur"cp\. the adj. {greek} {gloss}; {text}$",
    ur"cp\. the epic form {greek} {gloss}; rare in the nt\. form$",
    ur"cp\. {greek} and {greek} in sense of {gloss}$",
    ur"cp\. {greek} and {greek}$",
    ur"cp\. {greek} in sense of {gloss} {text} ={gloss}; {see} {greek}$",
    ur"cp\. {greek} opp\. {greek}$",
    ur"cp\. {greek} {gloss} and Lat\. {latin}$",
    ur"cp\. {greek} {gloss} and {greek} {gloss}; {text} {gloss}; cp\. Lat\. {latin}$",
    ur"cp\. {greek} {gloss} and {greek}$",
    ur"cp\. {greek} {gloss} and {see} {greek}$",
    ur"cp\. {greek} {gloss} in Persia$",
    ur"cp\. {greek} {gloss}$",
    ur"cp\. {greek} {gloss}, {greek} {gloss}$",
    ur"cp\. {greek} {gloss}, {text}; cp\. our {gloss} in ref\. to {text}$",
    ur"cp\. {greek}$",
    ur"cp\. {greek}, {greek} {gloss} fr\. {greek}$",
    ur"cp\. {greek}, {greek}$",
    ur"cp\. {greek}; Lat\. {latin} {gloss}$",
    ur"cp\. {greek}; mostly in pl\. {gloss}$",
    ur"cp\. {greek}; {gloss} {text}$",
    ur"cp\. {greek}; {gloss}$",
    ur"cp\. {greek}; {gloss}, {text}$",
    ur"cp\. {prec} entries$",
    ur"cp\. {prec}$",
    ur"derivation uncertain; the transl\. {greek} {greek} may reflect folk etymology$",
    ur"derivation undetermined, but a root signifying {gloss} or {gloss} has claimed attention$",
    ur"derived from {greek}, {text}$",
    ur"develops from the pf\. of {greek} {gloss}:{greek} {gloss}, hence {gloss}$",
    ur"dim\. of {greek}$",
    ur"dim\. of {greek}, which is a dim\. of {greek}$",
    ur"dim\. of {greek}; {gloss} \({text}\), hence {gloss} {text} \({text}\) {text}$",
    ur"etym\. (complex|unclear|uncertain); {gloss}$",
    ur"etym\. complex, cp\. {greek}; Lat\. {latin} {gloss} reflects {greek}$",
    ur"etym\. complex, cp\. {text} {gloss}$",
    ur"etym\. complex, perh\. a connection w\. {greek}; {text} {gloss}$",
    ur"etym\. complex; prim\. {gloss} {text}$",
    ur"etym\. complex; {gloss} \(Hom\.\), then {gloss}$",
    ur"etym\. uncertain, cp\. {greek} {gloss}$",
    ur"etym\. uncertain, perh\. associated with {greek} in sense of {text}$",
    ur"etym\. uncertain; the translation {greek} {greek} {ref} may reflect popular etym\.$",
    ur"etym\. uncertain; {text}$",
    ur"etym\. uncertain; {text}:{text}$",
    ur"etym\. unclear \(many conflicting theories\), cp\. {greek} {gloss}$",
    ur"etym\. unclear; the NT shows a preference for {greek}$",
    ur"etym\. unclear; two major significations:{gloss} with raw materials, {gloss} esp\. of athletic exercise$",
    ur"etym\. unclear; {text}, in appearance like a {gloss}, the primary meaning of {greek}\.$",
    ur"etym\. undetermined; freq\. in Homer of {gloss} or {gloss} {text}$",
    ur"etym\. unknown, Lat\. {latin} is a loanword$",
    ur"etymol\. unknown$",
    ur"folk- etymology \(ἀ- priv\., {greek} o {greek}\) underlies the Gk\. formation of this foreign word, suggesting perh\. {gloss}$",
    ur"folk- etymology \(ἀ- priv\., {greek}\) underlies the Gk\. formation of this foreign word, suggesting perh\. {gloss}$",
    ur"for older {greek}$",
    ur"formally the pres\. ptc\. of {greek}$",
    ur"fr\. a root related to Latvian {latvian} {gloss}, cp\. {greek}$",
    ur"fr\. a root related to Lithuanian {lithuanian} {gloss}, Attic form:{greek}; {gloss}, then {gloss} {text}$",
    ur"fr\. the fut\. of {greek}, {greek}$",
    ur"fr\. {text} {greek}$",
    ur"freq\. as v\. l\. for {greek}$",
    ur"from the adj\. {greek} {half-gloss}$",
    ur"from the var\. {greek} comes the customary rendering {gloss}$",
    ur"in older Gk\. also {greek}$",
    ur"late by- form of {greek}$",
    ur"later form of {greek} in same sense$",
    ur"later form of {greek}:ἀ- priv\., {greek} {gloss}$",
    ur"later form of {greek}\. IE, cp\. {greek}$",
    ur"later word for {greek} and freq\. w\. {greek} as v\. l\.$",
    ur"name found in Aegean inscriptions$",
    ur"name of {text}$",
    ur"named after {text}$",
    ur"noun from the adj\. {greek}, cp\. {greek}$",
    ur"nt\. comp\. of {greek} {gloss}$",
    ur"of Dravidian origin$",
    ur"of Heb\. derivation$",
    ur"of Oriental origin, prob\. via Egypt; {gloss}, {text}$",
    ur"of Sanskrit origin, cp\. Lat\. {latin} {gloss}$",
    ur"onomatopoetic prefix, {greek}, cp\. {greek} {gloss} and Lat\. {latin}$",
    ur"opp\. {greek} {gloss}$",
    ur"orig\. uncertain, akin to {greek}$",
    ur"orig\. uncertain, but cp\. {greek} {gloss}; {gloss}$",
    ur"orig\. uncertain; {text}$",
    ur"orig\. unclear; {text}$",
    ur"orig\. undetermined; {text}$",
    ur"perh\. short for {greek}$",
    ur"prob\. of foreign origin$",
    ur"proper name in form of a participle from {greek}$",
    ur"properly nt\. gen\. of {greek}$",
    ur"the form and textual history of this name is complex$",
    ur"the more freq\. form of {greek} in earlier Gk\. lit\.; {gloss}$",
    ur"vernacular form of {greek}$",
    ur"{greek} ={greek} \({see} {greek}\), {greek}$",
    ur"{greek} \(={greek}\); {gloss}$",
    ur"{greek} \(w\. focus on separation\), {greek} {gloss}, freq\. with connotation of {text}$",
    ur"{greek} \({greek} and {greek} via the aor\. pass\. inf\. {greek}\)$",
    ur"{greek} \({greek}, {greek} {gloss}, {greek}\) {gloss}$",
    ur"{greek} \({greek}, {greek} {gloss}\) {gloss}$",
    ur"{greek} \({greek}, {greek}\) {gloss}$",
    ur"{greek} \({greek}, {greek}\) {gloss}, {text}$",
    ur"{greek} \(ἀ- priv\., {greek} o {greek}\) {gloss}$",
    ur"{greek} \(ἀ- priv\., {greek} {half-gloss}\) {gloss}$",
    ur"{greek} \(ἀ- priv\., {greek}\) {gloss}$",
    ur"{greek} \(ἀ- priv\., {greek}\) {gloss}, fr\. {greek}$",
    ur"{greek} \(ἀ- priv\., {greek}\); {gloss} i\. e\. {gloss}$",
    ur"{greek} \+a root with focus on independent action; {gloss}$",
    ur"{greek} fr\. {greek}$",
    ur"{greek} gener\. ={gloss}$",
    ur"{greek} in sense of {gloss}, {greek}$",
    ur"{greek} ordinarily in the sense {gloss}$",
    ur"{greek} with connotation of {gloss}, {greek}$",
    ur"{greek} with its full force, {greek} {gloss}$",
    ur"{greek} with perfective force, {greek}$",
    ur"{greek} {gloss} fr\. an older ptc\. form and and connected with {greek}$",
    ur"{greek} {gloss} fr\. {greek} a later form of {greek}$",
    ur"{greek} {gloss} fr\. {greek}$",
    ur"{greek} {gloss} {text}$",
    ur"{greek} {gloss} {text}$",
    ur"{greek} {gloss} {text}:to be {greek} \(ἀ- priv\.\) means that one {text}; {gloss}$",
    ur"{greek} {gloss}$",
    ur"{greek} {gloss}, cp\. {greek} {gloss}$",
    ur"{greek} {gloss}, cp\. {greek} {gloss}; in sense ranging from {gloss} to {gloss}$",
    ur"{greek} {gloss}, cp\. {greek}$",
    ur"{greek} {gloss}, cp\. {greek}, {greek} {gloss}$",
    ur"{greek} {gloss}, mid\. {gloss}$",
    ur"{greek} {gloss}, not to be confused with the homograph {greek} {gloss}$",
    ur"{greek} {gloss}, the prefix {greek} emphasizes {text}$",
    ur"{greek} {gloss}, then also as nautical term {gloss} because {text}$",
    ur"{greek} {gloss}, then {gloss} {text}$",
    ur"{greek} {gloss}, {greek} {gloss} {text} {greek} {gloss}$",
    ur"{greek} {gloss}, {greek} {gloss}$",
    ur"{greek} {gloss}, {greek} {gloss}; {gloss}$",
    ur"{greek} {gloss}, {greek} {gloss}; {text}$",
    ur"{greek} {gloss}, {greek}; {gloss}$",
    ur"{greek} {gloss}, {greek}; {gloss}, {text}$",
    ur"{greek} {gloss}, {greek}; {text}$",
    ur"{greek} {gloss}, {text}$",
    ur"{greek} {gloss}; in non- biblical authors freq\. in sense of {gloss}$",
    ur"{greek} {gloss}; late word for {greek} \({greek} {gloss}\)$",
    ur"{greek} {gloss}; mid\. of joining pers\., ordinarily in the sense {gloss}$",
    ur"{greek} {gloss}; prim\. {gloss} esp\. as {gloss} {text}$",
    ur"{greek} {gloss}; {gloss}$",
    ur"{greek} {gloss}; {gloss}, also of foods in var\. senses of {gloss}, hence {gloss}$",
    ur"{greek} {gloss}; {gloss}, {gloss} {text} {gloss} {text}$",
    ur"{greek} {gloss}; {gloss}, {text} {gloss}$",
    ur"{greek} {gloss}; {gloss}; cp\. {greek}$",
    ur"{greek} {gloss}; {text}:{text}$",
    ur"{greek} {text}$",
    ur"{greek}$",
    ur"{greek}, Gk\. deity$",
    ur"{greek}, \*{greek}$",
    ur"{greek}, a city in Transjordania$",
    ur"{greek}, addition of {greek} indicates {text}$",
    ur"{greek}, an adj\. {gloss}, {text} \({text}\) \+{greek} \({greek}\) {gloss} \(hence {gloss}\)$",
    ur"{greek}, cp\. {greek} \({greek}, {greek}\) {gloss}$",
    ur"{greek}, cp\. {greek} {gloss}",
    ur"{greek}, cp\. {greek}$",
    ur"{greek}, cp\. {greek}; ={greek}, which is preferred in later Gk\.$",
    ur"{greek}, cp\. {greek}; {gloss}$",
    ur"{greek}, in early Gk. {gloss}$",
    ur"{greek}, originally nt\. pl\. of {greek} with change in accent reflecting emphasis {gloss}; stronger than {greek}$",
    ur"{greek}, the term for {text} in Hittite and Egyptian texts and Homer$",
    ur"{greek}, {greek} /{greek} {gloss}, hence {greek} signifies close of pregnancy$",
    ur"{greek}, {greek} \(no present in use\)$",
    ur"{greek}, {greek} \({greek} \+{greek}\) {gloss} fr\. {greek}; {gloss}$",
    ur"{greek}, {greek} fr\. {greek} \({greek}\) {gloss}$",
    ur"{greek}, {greek} fr\. {greek}$",
    ur"{greek}, {greek} fr\. {greek}, cp\. {greek} {gloss}$",
    ur"{greek}, {greek} fr\. {greek}; in later Gk\. {greek} gives way to {greek}$",
    ur"{greek}, {greek} fr\. {greek}; {gloss}$",
    ur"{greek}, {greek} fr\. {greek}; {gloss}, hence {gloss}$",
    ur"{greek}, {greek} via the mid\.$",
    ur"{greek}, {greek} via {greek} {gloss}, in various senses, including {text} as {gloss} and {gloss}$",
    ur"{greek}, {greek} via {greek}; the prefix, apparently redundant, makes the idea of {text} in {greek} explicit$",
    ur"{greek}, {greek} {gloss} ={text} {greek}$",
    ur"{greek}, {greek} {gloss} \(cp\. {greek}\)$",
    ur"{greek}, {greek} {gloss} also {gloss}, as compound fr\. {greek}$",
    ur"{greek}, {greek} {gloss} as in {text}$",
    ur"{greek}, {greek} {gloss} formed from the fut\. of {greek}, the compound fr\. {greek}$",
    ur"{greek}, {greek} {gloss} fr\. the mid\. of {greek}; {gloss}$",
    ur"{greek}, {greek} {gloss} fr\. {greek} {gloss}$",
    ur"{greek}, {greek} {gloss} fr\. {greek}$",
    ur"{greek}, {greek} {gloss} fr\. {greek}; {gloss}$",
    ur"{greek}, {greek} {gloss} or {gloss}$",
    ur"{greek}, {greek} {gloss} {text} fr\. {greek} {gloss}; {greek} has the force of {gloss}, i\. e\. {text}$",
    ur"{greek}, {greek} {gloss} {text}’; {greek} emphasizes {text}$",
    ur"{greek}, {greek} {gloss}$",
    ur"{greek}, {greek} {gloss}, as compound fr\. {greek}$",
    ur"{greek}, {greek} {gloss}, cp\. {greek}; {gloss}, hence {gloss}$",
    ur"{greek}, {greek} {gloss}, cp\. {greek}; {text}$",
    ur"{greek}, {greek} {gloss}, {text}$",
    ur"{greek}, {greek} {gloss}; Hom\. {gloss}, then {gloss}$",
    ur"{greek}, {greek} {gloss}; intensive form {half-gloss}$",
    ur"{greek}, {greek} {gloss}; prim\. {gloss}, {text}$",
    ur"{greek}, {greek} {gloss}; {gloss}$",
    ur"{greek}, {greek} {gloss}; {gloss}, hence {text}$",
    ur"{greek}, {greek} {text} ={gloss}$",
    ur"{greek}, {greek}$",
    ur"{greek}, {greek}, cp\. {greek} and {greek} {gloss}$",
    ur"{greek}, {greek}, cp\. {greek}$",
    ur"{greek}, {greek}, {greek} {gloss}$",
    ur"{greek}, {greek}; for older {greek}$",
    ur"{greek}, {greek}; in non- biblical Gk\. {greek} in this word signifies {gloss}; {gloss} ={gloss}$",
    ur"{greek}, {greek}; prim\. a commercial term$",
    ur"{greek}, {greek}; prim\. {gloss} then {gloss}, {text}$",
    ur"{greek}, {greek}; rarely found for the older {greek}$",
    ur"{greek}, {greek}; the idea of separation is strong in var\. senses including the act\. {gloss}, and the mid\. {gloss}, which implies a {greek} or {gloss} out of \({greek}\) a number of possibilities$",
    ur"{greek}, {greek}; the noun is more freq\. than the adj\. {greek}, {greek}$",
    ur"{greek}, {greek}; this 2 aor\. form is commonly used for the aor\. of {greek}$",
    ur"{greek}, {greek}; various senses in non- bibl\. Gk\.$",
    ur"{greek}, {greek}; {gloss} and so {gloss} on a specific object$",
    ur"{greek}, {greek}; {gloss} i\. e\. {gloss}$",
    ur"{greek}, {greek}; {gloss} {text}$",
    ur"{greek}, {greek}; {gloss}$",
    ur"{greek}, {greek}; {gloss}, e\. g\. {text}$",
    ur"{greek}, {greek}; {gloss}, hence {gloss}$",
    ur"{greek}, {greek}; {gloss}, then by extension {gloss}$",
    ur"{greek}, {greek}; {greek} expresses the opposite of {greek} {gloss} and focuses on separation, with such senses as {gloss}; mod\. Gk\. {gloss} from a position$",
    ur"{greek}, {greek}; {text} {gloss}$",
    ur"{greek}, {greek}; {text} {gloss}, hence {gloss} and so {gloss}$",
    ur"{greek}, {greek}; {text}$",
    ur"{greek}- \(of complex derivation\) \+{greek}- \(cp\. {greek} {gloss}\)$",
    ur"{greek}; =next entry$",
    ur"{greek}; a late form for {greek} {gloss}$",
    ur"{greek}; act\. {gloss}, mid\. {gloss} or {gloss}, pass\. {gloss}$",
    ur"{greek}; antonym {greek}$",
    ur"{greek}; any {gloss} or {gloss}$",
    ur"{greek}; freq\. in ins\. and pap\. of public servants$",
    ur"{greek}; in Hom\. {gloss}, then gener\. {gloss}$",
    ur"{greek}; in ancient Gk\. in var\. senses of a {gloss}, such as {text}$",
    ur"{greek}; in both a bad sense {gloss} and a good sense {gloss}$",
    ur"{greek}; only in biblical usage$",
    ur"{greek}; prim\. {gloss}, then {gloss}, {gloss}$",
    ur"{greek}; the form with accent on the second syllable signifies {gloss}, with accent on the final syllable {gloss}$",
    ur"{greek}; the suffix- {greek} may have affinity with {greek}, {greek} {gloss}, and related terms; {gloss}$",
    ur"{greek}; tr\. {gloss}$",
    ur"{greek}; {gloss} {text}, {text} {gloss} {text}$",
    ur"{greek}; {gloss}$",
    ur"{greek}; {gloss}, esp\. {text}$",
    ur"{greek}; {gloss}, freq\. {text}$",
    ur"{greek}; {gloss}; cp\. {greek} {text} {gloss}$",
    ur"{greek}; {text}$",
    ur"{greek}; {text}, hence, {gloss}$",
    ur"{see} next entry on the etymology$",
    ur"{see} next$",
    ur"{see} {greek}$",
    ur"{see} {greek}$",
    ur"{see} {prec} entry$",
    ur"{see} {prec} {greek}- entries and two next entries$",
    ur"{see} {prec} {greek}- entries; the act\., which is not used in NT ={gloss}$",
    ur"{see} {prec}$",
    ur"{text}; {text} {greek} {gloss} {text} {gloss}; {text} {gloss}$",
    ur"ἀ- \(ἁ-\) copul\., {greek}$",
    ur"ἀ- copul\., {greek} {gloss} ={gloss}$",
    ur"ἀ- copul\., {greek} {gloss}$",
    ur"ἀ- priv, {greek}$",
    ur"ἀ- priv\. \(ἁ- by metathesis of aspiration\), {greek}, otherwise a word of uncertain orig\.$",
    ur"ἀ- priv\., cp\. {greek}, {text}$",
    ur"ἀ- priv\., fr\. {greek} via the fut\. mid\. form of {greek}:{greek}$",
    ur"ἀ- priv\., {greek} =Attic {greek} s$",
    ur"ἀ- priv\., {greek} ={greek} {gloss} {text}; {gloss}$",
    ur"ἀ- priv\., {greek} \({greek}, {greek} {gloss}\) {gloss} or \({greek}, {greek} {gloss} fr\. {greek} {gloss}\) {gloss}$",
    ur"ἀ- priv\., {greek} \({greek}, {greek}\) {gloss}$",
    ur"ἀ- priv\., {greek} \({greek}, {greek}\) {gloss}; {gloss}$",
    ur"ἀ- priv\., {greek} fr\. {greek}$",
    ur"ἀ- priv\., {greek} via 2 aor\. {greek}; {gloss}$",
    ur"ἀ- priv\., {greek} {gloss} fr\. {greek} {gloss}$",
    ur"ἀ- priv\., {greek} {gloss} fr\. {greek}$",
    ur"ἀ- priv\., {greek} {gloss} fr\. {greek}; lit\. {gloss}$",
    ur"ἀ- priv\., {greek} {gloss} fr\. {greek}; {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}, cp\. {greek}$",
    ur"ἀ- priv\., {greek} {gloss}, esp\. {text}$",
    ur"ἀ- priv\., {greek} {gloss}, fr\. {greek} via {greek} {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}, freq\. in 3 sg\. {greek}$",
    ur"ἀ- priv\., {greek} {gloss}, {text}; {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}; cp\. {greek} {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}; {gloss}$",
    ur"ἀ- priv\., {greek} {gloss}; {gloss}, hence {gloss}$",
    ur"ἀ- priv\., {greek}$",
    ur"ἀ- priv\., {greek}, cp\. {greek} and {greek}$",
    ur"ἀ- priv\., {greek}, q\. v\., in sense of {gloss}; {text}$",
    ur"ἀ- priv\., {greek}, {greek} {gloss} fr. {greek}$",
    ur"ἀ- priv\., {greek}, {greek} {gloss}, cp\. {greek} {gloss}$",
    ur"ἀ- priv\., {greek}, {greek}$",
    ur"ἀ- priv\., {greek}; {gloss}$",
    ur"ἀ- priv\., {greek}; {gloss}, {text} {gloss} {text}$",
    ur"ἀ- priv\., {greek}; {text}$",
    ur"ἀ\.- priv\., {greek} \(used in the phrase {greek} {greek} {gloss}\) fr\. {greek}$",
    ur"ἀ\.- priv\., {greek}, cp\. {greek}$",
    ur"ἁ- copul\. {gloss} =Skt\. {skt}-, cp\. {greek} and oblique forms$",
    ur"ἁ- copul\., {greek} \(etym\. complex, with idea of {gloss}\) as in {greek} {gloss}; {gloss}$",
    ur"ἡ {greek} {gloss} and ὁ {greek} {gloss}, fr\. a common root:cp\. Lat\. {latin} {gloss}$",
    ur"ὁ {greek} {gloss}$",
    ur"Hom\. {greek} {gloss}; cp\. Lat\. {latin}$",
    ur"=older {greek}$",
    ur"cp\. {greek} {gloss}, {text}; {gloss}$",
    ur"related to a Heb\. word for {gloss}$",
    ur"Lat\. orig\.$",
    ur"cp\. {greek}, assoc\. w\. Skt\., {gloss}, such as {gloss}, {gloss}$",
    ur"generally accepted as contraction of {greek} and {greek}:in a broad sense ={gloss}$",
    ur"cp\. {greek} ={greek} {gloss}; prim\. {gloss}, {text}$",
    ur"identical with Gothic- k$",
    ur"Heb\.; {gloss}$",
    ur"{greek}; early writers:{text}, later Gk\. in a more general sense of {gloss}$",
    ur"{greek}; prim\. a kinship term {gloss}$",
    ur"{greek}; contrast {greek}$",
    ur"{greek}, a poetic term ={greek}$",
    ur"{greek}; contrast {greek}; {gloss}$",
    ur"Heb\.; also found in the more correct form {greek}$",
    ur"of Semitic orig\.$",
    ur"Skt\. assoc\.; cp\. Lat\. {latin} {gloss} and its transferred sense {gloss}$",
    ur"{greek}, {greek}, cp\. {greek} {gloss}$",
    ur"Ionic and Hell\. form ={greek}, cp\. Lat\. {latin}; the central mng\. {gloss}$",
    ur"=earlier {greek}; {text}, then in past tenses {gloss}$",
    ur"cp\. {greek} and Lat\. {latin}$",
    ur"orig\. uncertain; opp\. {greek}, {greek} {gloss}$",
    ur"{greek}, {greek} {gloss}; {gloss}, then of containers for other objects such as money$",
    ur"{greek} fr\. {greek}; {gloss}, hence {gloss}$",
    ur"cp\. the earlier {greek}$",
    ur"{greek}; by- form of the older {greek} {gloss}, also {gloss}$",
    ur"Ionic and later Gr\. for {greek} {gloss}$",
    ur"cp\. {greek} {gloss} and {greek} {gloss}; {text} {gloss}, {text} {gloss}$",
    ur"Aram\. place name$",
    ur"{greek}; {gloss}, but usually pl\. {greek} {gloss}$",
    ur"{greek}, which s\. for details; in older Gk\. {gloss}, as well as {gloss}$",
    ur"{greek} {gloss} \+- {greek}; cp\. {greek}$",
    ur"dim\. of {greek}, derived fr\. its gen\.; {gloss}, with pejorative aspect$",
    ur"derived fr\. the gen\. of {greek}; {gloss}$",
    ur"Skt\. assoc\.; in Hom\. {gloss} in various occupations and social roles, and as {gloss}$",
    ur"nt\. noun fr\. the adj\. {greek}, {gloss}; {gloss}, then {gloss}$",
    ur"{greek},- {greek} {gloss}; {gloss}$",
    ur"in Gk\. lit\. {text}$",
    ur"cp\. the poetic form {greek} and Hell\. {greek}, cp\. also Lat\. {latin} \(older form of {latin}/{latin}\)$",
    ur"etym\. complex, cp\. prec\.$",
    ur"also {greek}- in some non- biblical mss\.$",
    ur"Skt\. {skt} {gloss}, cp\. next$",
    ur"perh\. related to prec\. by dissimilation or change of consonant$",
    ur"{greek} late form of {greek}, fr\. {greek} {gloss}, also {gloss}$",
    ur"{greek} late form of {greek}, cp\. prec\.$",
    ur"{greek} late form of {greek}, cp\. {greek} \(ε\) {greek}$",
    ur"cp\. next$",
    ur"also {greek}, {greek} in various mss\.$",
    ur"impersonal verb from {greek} {gloss}$",
    ur"cp\. {greek} {gloss}, {greek}$",
    ur"a formation developed from \*{greek} {greek} {gloss} and present in {greek} {greek}, hence the gen\. {greek} {greek} and associated inflection$",
    ur"the time of the day for δ\. varies in Gk\. lit, but eventually δ\. chiefly refers to {gloss}$",
    ur"late for {greek}$",
    ur"cp\. {greek} and {greek}, {greek}$",
    ur"the verbal aspect of 2b in prec\.$",
    ur"in Hom\. {greek}$",
    ur"mid\. of {greek} {gloss}, not {greek} {gloss}$",
    ur"{greek}; ={greek}$",
    ur"{greek}; the nt\. pl\. {greek} {greek} is used occasionally$",
    ur"cp\. Hom\. {greek} {gloss}$",
    ur"not to be confused with the homograph {greek} {gloss}, with which the impersonal {greek} is associated$",
    ur"cp\. {greek}- {greek}, {greek}- {greek}, {greek} \({greek} \+- {greek}, like {greek}\) {gloss}$",
    ur"{greek}, {greek}; {greek} {greek} ={gloss}, states Hesychius$",
    ur"Epic {greek} {gloss}$",
    ur"perh\. short form of {greek}$",
    ur"a common name, {text}$",
    ur"{greek}, {greek}; {gloss}, then {gloss}, {text}$",
    ur"etym\. complex; {gloss}, also {gloss} as distinguished from those of highter status$",
    ur"Lat\. {latin}, {text}$",
    ur"also {greek} {greek} {gloss}$",
    ur"also {greek} {greek}$",
    ur"basic sense {gloss}$",
    ur"{greek}, {greek} {gloss}, the basic idea of {greek} is {text}; the prep\. generally functions spatially {gloss}$",
    ur"{greek}, {greek} {gloss}, from the idea of {gloss} derives the sense {gloss} in ref\. to character$",
    ur"the prep\. functions intensively {gloss}$",
    ur"{greek}, {greek}, s\. {greek}$",
    ur"{greek}, {greek}; {gloss}; cp\. {greek}$",
    ur"{greek}, {greek}; rare:{text} {gloss}$",
    ur"onomatopoetic word$",
    ur"intensive of {greek}$",
    ur"{greek}, {greek}:{greek} {gloss}; {gloss}$",
    ur"{greek}; cp\. οἱ {greek} {gloss} {text}$",
    ur"{greek}, {greek}, cp\. {greek}; {gloss}$",
    ur"{greek}, {greek}, {greek}$",
    ur"cp\. {greek}, {greek}:{greek}:{gloss}, then {gloss}; {gloss}$",
    ur"cp\. {greek}; a function- oriented rather than status- oriented term$",
    ur"{greek} \+formation underlying e\. g\. {greek}$",
    ur"{greek} is intensive; {gloss} ={text}$",
]

compiled_regexes = []

for regex in regexes:
    for name, substitution in regex_templates.items():
        regex = re.sub("{{{}}}".format(name), substitution, regex)
    compiled_regexes.append(re.compile(regex))

danker = load_yaml("../data-cleanup/danker-concise-lexicon/components.yaml")

first_fail = None
count = 0

for lexeme, metadata in sorted_items(danker):
    components = metadata["components"]

    matched = False
    for compiled_regex in compiled_regexes:
        if compiled_regex.match(components):
            matched = True
            break

    if matched:
        count += 1
    else:
        if not first_fail:
            first_fail = (lexeme, components)

print "{}/{} = {}%".format(count, len(danker), int(1000 * count / len(danker)) / 10)
if first_fail:
    print first_fail[0]
    print first_fail[1]
