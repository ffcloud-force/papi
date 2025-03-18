# Define a dictionary to organize prompts by category
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
    "Bitte formuliere nun 2 - 5 Fragen zu dem Fall, nehme dabei folgendes Themengebiet in den Fokus:"
  ),
  "case_questions": {
      "diagnostic": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Diagnostik und Differentialdiagnose betreffen: "
          "- Fragen zur verwendeten Diagnostik ('Welche Diagnostikverfahren haben Sie verwendet?') "
          "- Begründung von Diagnosen und Ausschlussdiagnosen ('Warum haben Sie die Diagnose xy ausgeschlossen?') "
          "- Nachweis der Beherrschung von Anamnesentechnik und psychodiagnostischen Untersuchungsmethoden "
          "- Beurteilung der Ergebnisse diagnostischer Verfahren "
          "- Gewichtung unterschiedlicher Informationen für die Diagnosestellung "
          "Achte dabei auf Testverfahren, Klassifikationssysteme (ICD/DSM) und Ausschlussdiagnosen."
      ),
      "model": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche das Störungsmodell betreffen: "
          "- Erklärung des Störungsmodells und dessen Vermittlung an den Patienten ('Wie haben Sie der/dem Patientin/en die Theorie zur Entstehung von xy vermittelt?') "
          "- Biografische Erklärung prädisponierender Faktoren ('Wie ist der prädisponierende Faktor xy biografisch erklärbar?') "
          "- Erkennung ätiologischer Zusammenhänge vor dem Hintergrund psychopathologischer Kenntnisse "
          "- Aufrechterhaltende Faktoren ('Was hält die Symptome aufrecht?') "
          "- Störungsspezifisches Wissen und dessen Anwendung im konkreten Fall "
      ),
      "therapy_process": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche den Therapieverlauf betreffen: "
          "- Darstellung des Behandlungsverlaufs "
          "- Umgang mit besonderen Umständen (z.B. 'Läuft die Behandlung einer Zwangsstörung zu Coronazeiten anders ab?') "
          "- Anwendung der während der Ausbildung erworbenen Kenntnisse und Fertigkeiten "
          "- Spezifische Behandlungsaspekte, inklusive Interventionen, Therapieplanung und Krisenmanagement "
          "- Begründung therapeutischer Entscheidungen im Behandlungsverlauf "
      ),
      "alternative_treatments": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Alternativbehandlungen betreffen: "
          "- Frage nach evidenzbasierten Behandlungsalternativen gemäß den S3-Leitlinien ('Welche Empfehlungen werden in den S3 Leitlinien gegeben?') "
          "- Darstellung der verwendeten Behandlungsmethode "
          "- Aufklärung des Patienten über Behandlungsalternativen ('Wie haben Sie die Patientin dazu aufgeklärt?') "
          "- Wissenschaftlich anerkannte Verfahren und Methoden "
      ),
      "medication": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche die Medikation betreffen: "
          "- Prüfe Kenntnisse über psychopharmakologische Behandlungen, Wirkmechanismen, Nebenwirkungen und Kombinationstherapien "
          "- Indikationen und Kontraindikationen für Psychopharmaka im spezifischen Fall "
          "- Zusammenarbeit mit Fachärzten bei medikamentöser Behandlung "
      ),
      "personal_learnings": (
          "Analysiere den Fall und erstelle eine oder mehrere Fragen zu dem Fall, welche das persönliche Lernen betreffen: "
          "- Reflexion über eigene therapeutische Entwicklung anhand des Falls "
          "- Herausforderungen und deren Bewältigung "
          "- Erkenntnisse für zukünftige Behandlungen "
          "- Supervision und deren Einfluss auf den Behandlungsprozess "
      )
  },
  "case_questions_tp": {
      "relationships": {
        "core_conflictual_relationship_theme": (
          "CCRT nach Luborsky: Analyse wiederkehrender Beziehungsmuster mit Fokus auf drei Komponenten: "
          "- Zentrale Wünsche (W) der Person "
          "- Typische Reaktionen anderer (RO) auf diese Wünsche "
          "- Typische Reaktionen des Selbst (RS) auf die Antworten anderer "
          "Identifikation dieser Muster mittels Beziehungsepisoden und deren Übertragung in die therapeutische Beziehung"
        ),
        "object_relations": (
          "Objektbeziehungstheorie nach Klein, Fairbairn, Bion, Winnicott und Kernberg: "
          "- Internalisierte Objektrepräsentanzen und deren Einfluss auf aktuelle Beziehungen "
          "- Konzepte wie Spaltung (gut/böse Objekte), Teilobjekte und Ganzobjekte "
          "- Paranoid-schizoide und depressive Position nach Klein "
          "- Projektive Identifizierung als Kommunikationsmechanismus "
          "- Übergangsobjekte nach Winnicott "
          "- Bedeutung früher Mutter-Kind-Interaktionen für die Persönlichkeitsentwicklung "
        ),
        "transference_countertransference": (
          "Übertragung und Gegenübertragung im psychodynamischen Prozess: "
          "- Übertragung als Wiederholung früherer Beziehungserfahrungen "
          "- Entwicklung des Gegenübertragungskonzepts von Freud bis heute "
          "- Proaktive (therapeuteneigene) und reaktive (durch Patient ausgelöste) Gegenübertragung "
          "- Klinische Nutzung von Gegenübertragungsgefühlen als diagnostisches Instrument "
          "- Objektive Gegenübertragung nach Winnicott "
          "- Containment-Funktion nach Bion "
        ),
        "attachment_styles": (
          "Bindungstheorie und deren klinische Anwendung: "
          "- Grundlegende Bindungsstile nach Bowlby und Ainsworth (sicher, unsicher-vermeidend, unsicher-ambivalent, desorganisiert) "
          "- Entwicklungsphasen der Bindung und sensitive Perioden "
          "- Innere Arbeitsmodelle und deren Übertragung auf spätere Beziehungen "
          "- Adult Attachment Interview (AAI) nach Main zur Erfassung von Bindungsrepräsentanzen "
          "- Bedeutung der frühen Bindungserfahrungen für die Emotionsregulation und psychische Struktur "
        )
      },
      "conflict": {
        "opd_conflict": (
          "OPD-Konflikte und deren Diagnostik: "
          "- Die sieben Konflikte nach OPD-3: Individuation vs. Abhängigkeit (K1), Unterwerfung vs. Kontrolle (K2), Versorgung vs. Autarkie (K3), Selbstwert (K4), Schuld (K5), Ödipaler Konflikt (K6), Identität (K7) "
          "- Aktiver und passiver Verarbeitungsmodus je Konflikt "
          "- Methodik der Konfliktdiagnostik im OPD-System "
          "- Zusammenhang zwischen Konflikten und psychischer Struktur "
          "- Konfliktachse als Grundlage für Behandlungsplanung "
        ),
        "basic_conflicts": (
          "Grundkonflikte nach Rudolf: "
          "- Zusammenhang zwischen Grundkonflikten und strukturellem Niveau "
          "- Zeitpunkt der Konfliktentstehung in der psychischen Entwicklung "
          "- Unterscheidung zwischen frühen präödipalen und späteren ödipalen Konflikten "
          "- Konfliktspezifische Abwehrmechanismen "
          "- Beziehung zwischen Grundkonflikten und klinischen Störungsbildern "
        ),
        "unconscious_processes": (
          "Unbewusste Prozesse und deren Manifestation: "
          "- Freud'sche Topik (bewusst, vorbewusst, unbewusst) "
          "- Primär- und Sekundärprozess "
          "- Unbewusste Phantasien nach Klein ('phantasy' mit 'ph') "
          "- Alpha- und Beta-Elemente nach Bion "
          "- Implizites Beziehungswissen "
          "- Manifestation des Unbewussten in Träumen, Fehlleistungen, Symptomen und Übertragung "
          "- Bedeutung unbewusster Prozesse für die therapeutische Arbeit "
        )
      },
      "structure": {
        "structure_level": (
          "Strukturniveau und dessen klinische Bedeutung: "
          "- Kernberg's Einteilung: hohes, mittleres und niedriges Strukturniveau "
          "- OPD-Strukturniveaus: gut integriert, mäßig integriert, gering integriert, desintegriert "
          "- Zusammenhang zwischen Strukturniveau und Psychopathologie "
          "- Diagnostische Kriterien zur Einschätzung des Strukturniveaus "
          "- Bedeutung des Strukturniveaus für Behandlungsplanung und Prognose "
          "- Methoden zur Erfassung des Strukturniveaus in der klinischen Praxis "
        ),
        "structural_deficits": (
          "Strukturelle Defizite und deren Auswirkungen: "
          "- Die sechs Strukturdimensionen nach OPD: Selbstwahrnehmung, Selbststeuerung, Abwehr, Objektwahrnehmung, Kommunikation, Bindung "
          "- Einschränkungen dieser Dimensionen bei unterschiedlichen Störungsbildern "
          "- Regulationsstörungen als Folge struktureller Defizite "
          "- Auswirkungen früher Traumatisierungen auf die Strukturentwicklung "
          "- Differenzialdiagnostik zwischen Konflikt- und Strukturpathologie "
        ),
        "defense_mechanisms": (
          "Abwehrmechanismen und deren diagnostische Einordnung: "
          "- Hierarchie der Abwehrmechanismen nach Anna Freud "
          "- Reife, neurotische und unreife/primitive Abwehrmechanismen "
          "- Strukturspezifische Abwehrmuster: Spaltung (niedrig), Idealisierung/Entwertung (mittel), Verdrängung (hoch), Sublimierung (reif) "
          "- Funktion der Abwehr zum Schutz des psychischen Gleichgewichts "
          "- Abwehranalyse als therapeutisches Instrument "
          "- Veränderung der Abwehrmechanismen im therapeutischen Prozess "
        ),
      "developmental_aspects": (
        "Entwicklungspsychologische Aspekte und deren klinische Relevanz: "
        "- Psychosexuelle Entwicklungsphasen nach Freud "
        "- Objektbeziehungsentwicklung nach Mahler (Symbiose, Separation-Individuation) "
        "- Frühe Entwicklung des Selbst nach Stern und Kohut "
          "- Bedeutung der Entwicklungslinien nach Anna Freud "
          "- Container-Contained-Konzept nach Bion "
          "- Entwicklung der Mentalisierungsfähigkeit "
          "- Entwicklungstrauma und dessen Auswirkungen auf die Persönlichkeitsstruktur "
        )
      }
    }
  }

# Helper functions to retrieve prompts
def get_examiner_prompt():
    """Get the system prompt"""
    return EXAM_PROMPTS["examiner_prompt"]

def get_case_question_prompt(question_type):
    """Get a case question prompt by type"""
    return EXAM_PROMPTS["case_questions"].get(question_type, "")

def get_case_question_prompt_tp(general_type, specific_type):
    """Get a case question prompt by type"""
    return EXAM_PROMPTS["case_questions_tp"].get(general_type, {}).get(specific_type, "")
