# A flatter structure for exam prompts
EXAM_PROMPTS = {
    "examiner_prompt": (
        "Du bist ein erfahrener Prüfer für die mündliche Psychotherapie-Approbationsprüfung in Deutschland. "
        "Deine Aufgabe ist es, realistische Prüfungsfragen zu einem psychotherapeutischen Fallbericht zu erstellen. "
        "Diese Prüfungsfragen sollen: "
        "- Die Theorie und praktische Anwendung psychotherapeutischer Konzepte prüfen "
        "- Den typischen Stil und Schwierigkeitsgrad einer realen Approbationsprüfung widerspiegeln "
        "- Sowohl Faktenwissen als auch klinisches Urteilsvermögen und Reflexionsfähigkeit abfragen "
        "- Einen fachlichen Dialog zwischen Prüfer und Kandidat ermöglichen, der die klinische Kompetenz des Kandidaten zeigt "
        "- Die Begründung diagnostischer und therapeutischer Entscheidungen erfragen "
        "- So formuliert sein, wie sie von einem Prüfungsausschussmitglied tatsächlich gestellt werden könnten "
        "- Verschiedene Komplexitätsebenen abdecken (von grundlegenden Fragen bis zu anspruchsvollen Fallkonzeptualisierungen) "
        "Orientiere dich an tatsächlichen Prüfungssituationen, in denen der Kandidat seinen Fall darstellt und von zwei Prüfern dazu befragt wird."
        "Bitte formuliere nun 3 Fragen zu dem Fall (eine leicht, eine mittel und eine schwer), nehme dabei folgendes Themengebiet in den Fokus: "
    ),
    "examiner_prompt_answer": (
        "Du bist ein erfahrener Prüfer für die mündliche Psychotherapie-Approbationsprüfung in Deutschland. "
        "Deine Aufgabe ist es, eine Antwort auf eine Prüfungsfrage zu einem psychotherapeutischen Fallbericht zu erstellen. "
        "Diese Prüfungsfragen sollen: "
        "- Die Theorie und praktische Anwendung psychotherapeutischer Konzepte prüfen "
        "- Den typischen Stil und Schwierigkeitsgrad einer realen Approbationsprüfung widerspiegeln "
        "- Sowohl Faktenwissen als auch klinisches Urteilsvermögen und Reflexionsfähigkeit abfragen "
        "- Einen fachlichen Dialog zwischen Prüfer und Kandidat ermöglichen, der die klinische Kompetenz des Kandidaten zeigt "
        "- Die Begründung diagnostischer und therapeutischer Entscheidungen erfragen "
        "- So formuliert sein, wie sie von einem Prüfungsausschussmitglied tatsächlich gestellt werden könnten "
        "- Verschiedene Komplexitätsebenen abdecken (von grundlegenden Fragen bis zu anspruchsvollen Fallkonzeptualisierungen) "
        "Orientiere dich an tatsächlichen Prüfungssituationen, in denen der Kandidat seinen Fall darstellt und von zwei Prüfern dazu befragt wird."
        "Bitte formuliere nun eine Antwort auf die oben genannte Frage: "
    ),
    "prompt_types": [
        # Simple prompt types
        {
            "id": "diagnostic",
            "type": "simple",
            "specialization": "allgemein",
            "prompt": (
                "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Diagnostik und Differentialdiagnose betreffen: "
                "- Fragen zur verwendeten Diagnostik ('Welche Diagnostikverfahren haben Sie verwendet?') "
                "- Begründung von Diagnosen und Ausschlussdiagnosen ('Warum haben Sie die Diagnose xy ausgeschlossen?') "
                "- Nachweis der Beherrschung von Anamnesentechnik und psychodiagnostischen Untersuchungsmethoden "
                "- Beurteilung der Ergebnisse diagnostischer Verfahren "
                "- Gewichtung unterschiedlicher Informationen für die Diagnosestellung "
                "Achte dabei auf Testverfahren, Klassifikationssysteme (ICD/DSM) und Ausschlussdiagnosen.\n\n"
            ),
        },
        # {
        #     "id": "model",
        #     "type": "simple",
        #     "specialization": "allgemein",
        #     "prompt": (
        #         "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche das Störungsmodell betreffen: "
        #         "- Erklärung des Störungsmodells und dessen Vermittlung an den Patienten ('Wie haben Sie der/dem Patientin/en die Theorie zur Entstehung von xy vermittelt?') "
        #         "- Biografische Erklärung prädisponierender Faktoren ('Wie ist der prädisponierende Faktor xy biografisch erklärbar?') "
        #         "- Erkennung ätiologischer Zusammenhänge vor dem Hintergrund psychopathologischer Kenntnisse "
        #         "- Aufrechterhaltende Faktoren ('Was hält die Symptome aufrecht?') "
        #         "- Störungsspezifisches Wissen und dessen Anwendung im konkreten Fall\n\n"
        #     )
        # },
        # {
        #     "id": "therapy_process",
        #     "type": "simple",
        #     "specialization": "allgemein",
        #     "prompt": (
        #         "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche den Therapieverlauf betreffen: "
        #         "- Darstellung des Behandlungsverlaufs "
        #         "- Umgang mit besonderen Umständen (z.B. 'Läuft die Behandlung einer Zwangsstörung zu Coronazeiten anders ab?') "
        #         "- Anwendung der während der Ausbildung erworbenen Kenntnisse und Fertigkeiten "
        #         "- Spezifische Behandlungsaspekte, inklusive Interventionen, Therapieplanung und Krisenmanagement "
        #         "- Begründung therapeutischer Entscheidungen im Behandlungsverlauf\n\n"
        #     )
        # },
        # {
        #     "id": "alternative_treatments",
        #     "type": "simple",
        #     "specialization": "allgemein",
        #     "prompt": (
        #         "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Alternativbehandlungen betreffen: "
        #         "- Frage nach evidenzbasierten Behandlungsalternativen gemäß den S3-Leitlinien ('Welche Empfehlungen werden in den S3 Leitlinien gegeben?') "
        #         "- Darstellung der verwendeten Behandlungsmethode "
        #         "- Aufklärung des Patienten über Behandlungsalternativen ('Wie haben Sie die Patientin dazu aufgeklärt?') "
        #         "- Wissenschaftlich anerkannte Verfahren und Methoden\n\n"
        #     )
        # },
        # {
        #     "id": "medication",
        #     "type": "simple",
        #     "specialization": "allgemein",
        #     "prompt": (
        #         "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Medikation betreffen: "
        #         "- Prüfe Kenntnisse über psychopharmakologische Behandlungen, Wirkmechanismen, Nebenwirkungen und Kombinationstherapien "
        #         "- Indikationen und Kontraindikationen für Psychopharmaka im spezifischen Fall "
        #         "- Zusammenarbeit mit Fachärzten bei medikamentöser Behandlung\n\n"
        #     )
        # },
        # {
        #     "id": "personal_learnings",
        #     "type": "simple",
        #     "specialization": "allgemein",
        #     "prompt": (
        #         "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche das persönliche Lernen betreffen: "
        #         "- Reflexion über eigene therapeutische Entwicklung anhand des Falls "
        #         "- Herausforderungen und deren Bewältigung "
        #         "- Erkenntnisse für zukünftige Behandlungen "
        #         "- Supervision und deren Einfluss auf den Behandlungsprozess\n\n"
        #     )
        # },
        # Complex prompt types
        # {
        #     "id": "relationships_core_conflictual_relationship_theme",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "relationships",
        #     "subcategory": "core_conflictual_relationship_theme",
        #     "prompt": (
        #         "CCRT nach Luborsky: Analyse wiederkehrender Beziehungsmuster mit Fokus auf drei Komponenten: "
        #         "- Zentrale Wünsche (W) der Person "
        #         "- Typische Reaktionen anderer (RO) auf diese Wünsche "
        #         "- Typische Reaktionen des Selbst (RS) auf die Antworten anderer "
        #         "Identifikation dieser Muster mittels Beziehungsepisoden und deren Übertragung in die therapeutische Beziehung\n\n"
        #     )
        # },
        # {
        #     "id": "relationships_object_relations",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "relationships",
        #     "subcategory": "object_relations",
        #     "prompt": (
        #         "Objektbeziehungstheorie nach Klein, Fairbairn, Bion, Winnicott und Kernberg: "
        #         "- Internalisierte Objektrepräsentanzen und deren Einfluss auf aktuelle Beziehungen "
        #         "- Konzepte wie Spaltung (gut/böse Objekte), Teilobjekte und Ganzobjekte "
        #         "- Paranoid-schizoide und depressive Position nach Klein "
        #         "- Projektive Identifizierung als Kommunikationsmechanismus "
        #         "- Übergangsobjekte nach Winnicott "
        #         "- Bedeutung früher Mutter-Kind-Interaktionen für die Persönlichkeitsentwicklung\n\n"
        #     )
        # },
        # {
        #     "id": "relationships_transference_countertransference",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "relationships",
        #     "subcategory": "transference_countertransference",
        #     "prompt": (
        #         "Übertragung und Gegenübertragung im psychodynamischen Prozess: "
        #         "- Übertragung als Wiederholung früherer Beziehungserfahrungen "
        #         "- Entwicklung des Gegenübertragungskonzepts von Freud bis heute "
        #         "- Proaktive (therapeuteneigene) und reaktive (durch Patient ausgelöste) Gegenübertragung "
        #         "- Klinische Nutzung von Gegenübertragungsgefühlen als diagnostisches Instrument "
        #         "- Objektive Gegenübertragung nach Winnicott "
        #         "- Containment-Funktion nach Bion\n\n"
        #     )
        # },
        # {
        #     "id": "relationships_attachment_styles",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "relationships",
        #     "subcategory": "attachment_styles",
        #     "prompt": (
        #         "Bindungstheorie und deren klinische Anwendung: "
        #         "- Grundlegende Bindungsstile nach Bowlby und Ainsworth (sicher, unsicher-vermeidend, unsicher-ambivalent, desorganisiert) "
        #         "- Entwicklungsphasen der Bindung und sensitive Perioden "
        #         "- Innere Arbeitsmodelle und deren Übertragung auf spätere Beziehungen "
        #         "- Adult Attachment Interview (AAI) nach Main zur Erfassung von Bindungsrepräsentanzen "
        #         "- Bedeutung der frühen Bindungserfahrungen für die Emotionsregulation und psychische Struktur\n\n"
        #     )
        # },
        # {
        #     "id": "conflict_opd_conflict",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "conflict",
        #     "subcategory": "opd_conflict",
        #     "prompt": (
        #         "OPD-Konflikte und deren Diagnostik: "
        #         "- Die sieben Konflikte nach OPD-3: Individuation vs. Abhängigkeit (K1), Unterwerfung vs. Kontrolle (K2), Versorgung vs. Autarkie (K3), Selbstwert (K4), Schuld (K5), Ödipaler Konflikt (K6), Identität (K7) "
        #         "- Aktiver und passiver Verarbeitungsmodus je Konflikt "
        #         "- Methodik der Konfliktdiagnostik im OPD-System "
        #         "- Zusammenhang zwischen Konflikten und psychischer Struktur "
        #         "- Konfliktachse als Grundlage für Behandlungsplanung\n\n"
        #     )
        # },
        # {
        #     "id": "conflict_basic_conflicts",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "conflict",
        #     "subcategory": "basic_conflicts",
        #     "prompt": (
        #         "Grundkonflikte nach Rudolf: "
        #         "- Zusammenhang zwischen Grundkonflikten und strukturellem Niveau "
        #         "- Zeitpunkt der Konfliktentstehung in der psychischen Entwicklung "
        #         "- Unterscheidung zwischen frühen präödipalen und späteren ödipalen Konflikten "
        #         "- Konfliktspezifische Abwehrmechanismen "
        #         "- Beziehung zwischen Grundkonflikten und klinischen Störungsbildern\n\n"
        #     )
        # },
        # {
        #     "id": "conflict_unconscious_processes",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "conflict",
        #     "subcategory": "unconscious_processes",
        #     "prompt": (
        #         "Unbewusste Prozesse und deren Manifestation: "
        #         "- Freud'sche Topik (bewusst, vorbewusst, unbewusst) "
        #         "- Primär- und Sekundärprozess "
        #         "- Unbewusste Phantasien nach Klein ('phantasy' mit 'ph') "
        #         "- Alpha- und Beta-Elemente nach Bion "
        #         "- Implizites Beziehungswissen "
        #         "- Manifestation des Unbewussten in Träumen, Fehlleistungen, Symptomen und Übertragung "
        #         "- Bedeutung unbewusster Prozesse für die therapeutische Arbeit\n\n"
        #     )
        # },
        # {
        #     "id": "structure_structure_level",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "structure",
        #     "subcategory": "structure_level",
        #     "prompt": (
        #         "Strukturniveau und dessen klinische Bedeutung: "
        #         "- Kernberg's Einteilung: hohes, mittleres und niedriges Strukturniveau "
        #         "- OPD-Strukturniveaus: gut integriert, mäßig integriert, gering integriert, desintegriert "
        #         "- Zusammenhang zwischen Strukturniveau und Psychopathologie "
        #         "- Diagnostische Kriterien zur Einschätzung des Strukturniveaus "
        #         "- Bedeutung des Strukturniveaus für Behandlungsplanung und Prognose "
        #         "- Methoden zur Erfassung des Strukturniveaus in der klinischen Praxis\n\n"
        #     )
        # },
        {
            "id": "structure_structural_deficits",
            "type": "complex",
            "specialization": "tiefenpsychologisch",
            "category": "structure",
            "subcategory": "structural_deficits",
            "prompt": (
                "Strukturelle Defizite und deren Auswirkungen: "
                "- Die sechs Strukturdimensionen nach OPD: Selbstwahrnehmung, Selbststeuerung, Abwehr, Objektwahrnehmung, Kommunikation, Bindung "
                "- Einschränkungen dieser Dimensionen bei unterschiedlichen Störungsbildern "
                "- Regulationsstörungen als Folge struktureller Defizite "
                "- Auswirkungen früher Traumatisierungen auf die Strukturentwicklung "
                "- Differenzialdiagnostik zwischen Konflikt- und Strukturpathologie\n\n"
            ),
        },
        # {
        #     "id": "structure_defense_mechanisms",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "structure",
        #     "subcategory": "defense_mechanisms",
        #     "prompt": (
        #         "Abwehrmechanismen und deren diagnostische Einordnung: "
        #         "- Hierarchie der Abwehrmechanismen nach Anna Freud "
        #         "- Reife, neurotische und unreife/primitive Abwehrmechanismen "
        #         "- Strukturspezifische Abwehrmuster: Spaltung (niedrig), Idealisierung/Entwertung (mittel), Verdrängung (hoch), Sublimierung (reif) "
        #         "- Funktion der Abwehr zum Schutz des psychischen Gleichgewichts "
        #         "- Abwehranalyse als therapeutisches Instrument "
        #         "- Veränderung der Abwehrmechanismen im therapeutischen Prozess\n\n"
        #     )
        # },
        # {
        #     "id": "structure_developmental_aspects",
        #     "type": "complex",
        #     "specialization": "tiefenpsychologisch",
        #     "category": "structure",
        #     "subcategory": "developmental_aspects",
        #     "prompt": (
        #         "Entwicklungspsychologische Aspekte und deren klinische Relevanz: "
        #         "- Psychosexuelle Entwicklungsphasen nach Freud "
        #         "- Objektbeziehungsentwicklung nach Mahler (Symbiose, Separation-Individuation) "
        #         "- Frühe Entwicklung des Selbst nach Stern und Kohut "
        #         "- Bedeutung der Entwicklungslinien nach Anna Freud "
        #         "- Container-Contained-Konzept nach Bion "
        #         "- Entwicklung der Mentalisierungsfähigkeit "
        #         "- Entwicklungstrauma und dessen Auswirkungen auf die Persönlichkeitsstruktur\n\n"
        #     )
        # }
    ],
    "output_format_questions": (
        "Gib deine Antwort als JSON-Array zurück. Jede Frage sollte ein separates JSON-Objekt sein mit folgender Struktur: "
        "{ "
        # "  'topic': 'Themenbereich (z.B. diagnostic, model, therapy_process, etc.)', " // Wird im nachhinein hinzugefügt
        "  'question': 'Die vollständige Fragestellung', "
        "  'context': 'Optionaler Kontext oder Hintergrundinfo zur Frage', "
        "  'difficulty': 'Einschätzung des Schwierigkeitsgrads (leicht, mittel, schwer)', "
        "  'keywords': ['Schlüsselwort1', 'Schlüsselwort2', ...] "
        "} "
        "Formatiere das JSON korrekt, damit es direkt maschinell verarbeitet werden kann."
    ),
    "output_format_answers": ("Gib deine Antwort als einfachen Text zurück. "),
}


# Helper functions
def get_examiner_prompt():
    """Get the system prompt"""
    return EXAM_PROMPTS["examiner_prompt"]


def get_examiner_prompt_answer():
    """Get the system prompt for answer generation"""
    return EXAM_PROMPTS["examiner_prompt_answer"]


def get_output_format_questions():
    """Get the output format for questions"""
    return EXAM_PROMPTS["output_format_questions"]


def get_output_format_answers():
    """Get the output format for answers"""
    return EXAM_PROMPTS["output_format_answers"]


def get_prompt_by_id(prompt_id):
    """Get a prompt by its ID"""
    for prompt_type in EXAM_PROMPTS["prompt_types"]:
        if prompt_type["id"] == prompt_id:
            return prompt_type["prompt"]
    return ""


def get_all_prompt_ids():
    """Get all available prompt IDs"""
    return [pt["id"] for pt in EXAM_PROMPTS["prompt_types"]]


def get_simple_prompt_ids():
    """Get IDs of all simple prompts"""
    return [pt["id"] for pt in EXAM_PROMPTS["prompt_types"] if pt["type"] == "simple"]


def get_complex_prompt_ids():
    """Get IDs of all complex prompts"""
    return [pt["id"] for pt in EXAM_PROMPTS["prompt_types"] if pt["type"] == "complex"]


def get_prompt_by_specialization(specialization):
    """Get all prompts by specialization"""
    return [
        pt
        for pt in EXAM_PROMPTS["prompt_types"]
        if pt["specialization"] == specialization
    ]
